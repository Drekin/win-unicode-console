
import sys, traceback
from ctypes import pythonapi, cdll, c_size_t, c_char_p, c_void_p, cast, CFUNCTYPE, POINTER, addressof

PyMem_Malloc = pythonapi.PyMem_Malloc
PyMem_Malloc.restype = c_size_t
PyMem_Malloc.argtypes = [c_size_t]

strncpy = cdll.msvcrt.strncpy
strncpy.restype = c_char_p
strncpy.argtypes = [c_char_p, c_char_p, c_size_t]

HOOKFUNC = CFUNCTYPE(c_char_p, c_void_p, c_void_p, c_char_p)

PyOS_ReadlineFunctionPointer = c_void_p.in_dll(pythonapi, "PyOS_ReadlineFunctionPointer")


def new_zero_terminated_string(b):
	p = PyMem_Malloc(len(b) + 1)
	strncpy(cast(p, c_char_p), b, len(b) + 1)
	return p


class ReadlineHookManager:
	def __init__(self):
		self.readline_wrapper_ref = HOOKFUNC(self.readline_wrapper)
		self.address = c_void_p.from_address(addressof(self.readline_wrapper_ref)).value
		self.original_address = PyOS_ReadlineFunctionPointer.value
		self.readline_hook = None
	
	def readline_wrapper(self, stdin, stdout, prompt):
		try:
			try:
				if sys.stdin.encoding != sys.stdout.encoding:
					raise ValueError("sys.stdin.encoding != sys.stdout.encoding, readline hook doesn't know, which one to use to decode prompt")
				
			except ValueError:
				traceback.print_exc(file=sys.stderr)
				try:
					prompt = prompt.decode("utf-8")
				except UnicodeDecodeError:
					prompt = ""
				
			else:
				prompt = prompt.decode(sys.stdout.encoding)
			
			try:
				line = self.readline_hook(prompt)
			except KeyboardInterrupt:
				return 0
			else:
				return new_zero_terminated_string(line.encode(sys.stdin.encoding))
			
		except:
			print("Intenal win_unicode_console error", file=sys.stderr)
			traceback.print_exc(file=sys.stderr)
			return new_zero_terminated_string(b"\n")
	
	def install_hook(self, hook):
		self.readline_hook = hook
		PyOS_ReadlineFunctionPointer.value = self.address
	
	def restore_original(self):
		self.readline_hook = None
		PyOS_ReadlineFunctionPointer.value = self.original_address


def readline(prompt):
	sys.stdout.write(prompt)
	sys.stdout.flush()
	return sys.stdin.readline()


class PyReadlineManager:
	def __init__(self):
		self.original_codepage = pyreadline.unicode_helper.pyreadline_codepage
	
	def set_codepage(self, codepage):
		pyreadline.unicode_helper.pyreadline_codepage = codepage
	
	def restore_original(self):
		self.set_codepage(self.original_codepage)

try:
	import pyreadline.unicode_helper
except ImportError:
	pyreadline = None
else:
	pyreadline_manager = PyReadlineManager()

manager = ReadlineHookManager()


def enable(*, use_pyreadline=True):
	if use_pyreadline and pyreadline:
		pyreadline_manager.set_codepage(sys.stdin.encoding)
			# pyreadline assumes that encoding of all sys.stdio objects is the same
	else:
		manager.install_hook(readline)

def disable():
	if pyreadline:
		pyreadline_manager.restore_original()
	
	manager.restore_original()

