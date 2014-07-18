
from types import CodeType as Code
import sys
import traceback
import __main__
from ctypes import pythonapi, POINTER, c_long, cast
import tokenize


inspect_flag = cast(pythonapi.Py_InspectFlag, POINTER(c_long)).contents

def set_inspect_flag(value):
	inspect_flag.value = int(value)


def update_code(codeobj, **kwargs):
	fields = ["argcount", "kwonlyargcount", "nlocals", "stacksize", "flags",
		"code", "consts", "names", "varnames", "filename", "name",
		"firstlineno", "lnotab", "freevars", "cellvars"]
	
	def field_values():
		for field in fields:
			value = kwargs.get(field, None)
			if value is None:
				yield getattr(codeobj, "co_{}".format(field))
			else:
				yield value
	
	return Code(*field_values())

def update_code_recursively(codeobj, **kwargs):
	updated = {}
	
	def update(codeobj, **kwargs):
		result = updated.get(codeobj, None)
		if result is not None:
			return result
		
		if any(isinstance(c, Code) for c in codeobj.co_consts):
			consts = tuple(update(c, **kwargs) if isinstance(c, Code) else c
				for c in codeobj.co_consts)
		else:
			consts = codeobj.co_consts
		
		result = update_code(codeobj, consts=consts, **kwargs)
		updated[codeobj] = result
		return result
	
	return update(codeobj, **kwargs)


def get_code(path):
	with tokenize.open(path) as f:	# opens with detected source encoding
		source = f.read()
	
	try:
		code = compile(source, path, "exec")
	except UnicodeEncodeError:
		code = compile(source, "<encoding error>", "exec")
		code = update_code_recursively(code, filename=path)
			# so code constains correct filename (even if it contains Unicode)
			# and tracebacks show contents of code lines
	
	return code

class MainLoader:
	# to reload __main__ properly
	
	def __init__(self, path):
		self.path = path
	
	def load_module(self, name):
		code = get_code(self.path)
		exec(code, __main__.__dict__)
		return __main__
		
def run_script():
	sys.argv.pop(0)	# so sys.argv looks correct from script being run
	path = sys.argv[0]
	__main__.__file__ = path
	__main__.__loader__ = MainLoader(path)
	
	
	try:
		code = get_code(path)
	except Exception as e:
		traceback.print_exception(e.__class__, e, e.__traceback__.tb_next.tb_next, chain=False)
	else:
		try:
			exec(code, __main__.__dict__)
		except BaseException as e:
			if not sys.flags.inspect and isinstance(e, SystemExit):
				raise
			else:
				traceback.print_exception(e.__class__, e, e.__traceback__.tb_next)

