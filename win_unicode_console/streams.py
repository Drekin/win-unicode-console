
from ctypes import byref, windll, c_ulong

from win_unicode_console.buffer import get_buffer

import io
import sys
import time


kernel32 = windll.kernel32
GetStdHandle = kernel32.GetStdHandle
ReadConsoleW = kernel32.ReadConsoleW
WriteConsoleW = kernel32.WriteConsoleW
GetLastError = kernel32.GetLastError


ERROR_SUCCESS = 0
ERROR_NOT_ENOUGH_MEMORY = 8
ERROR_OPERATION_ABORTED = 995

STDIN_HANDLE = GetStdHandle(-10)
STDOUT_HANDLE = GetStdHandle(-11)
STDERR_HANDLE = GetStdHandle(-12)

STDIN_FILENO = 0
STDOUT_FILENO = 1
STDERR_FILENO = 2

EOF = b"\x1a"

MAX_BYTES_WRITTEN = 32767	# arbitrary because WriteConsoleW ability to write big buffers depends on heap usage


class ReprMixin:
	def __repr__(self):
		modname = self.__class__.__module__
		clsname = self.__class__.__qualname__
		attributes = []
		for name in ["name", "encoding"]:
			try:
				value = getattr(self, name)
			except AttributeError:
				pass
			else:
				attributes.append("{}={}".format(name, repr(value)))
		
		return "<{}.{} {}>".format(modname, clsname, " ".join(attributes))


class WindowsConsoleRawIOBase(ReprMixin, io.RawIOBase):
	def __init__(self, name, handle, fileno):
		self.name = name
		self.handle = handle
		self.file_no = fileno
	
	def fileno(self):
		return self.file_no
	
	def isatty(self):
		super().isatty()	# for close check in default implementation
		return True

class WindowsConsoleRawReader(WindowsConsoleRawIOBase):
	def readable(self):
		return True
	
	def readinto(self, b):
		bytes_to_be_read = len(b)
		if not bytes_to_be_read:
			return 0
		elif bytes_to_be_read % 2:
			raise ValueError("cannot read odd number of bytes from UTF-16-LE encoded console")
		
		buffer = get_buffer(b, writable=True)
		code_units_to_be_read = bytes_to_be_read // 2
		code_units_read = c_ulong()
		
		retval = ReadConsoleW(self.handle, buffer, code_units_to_be_read, byref(code_units_read), None)
		if GetLastError() == ERROR_OPERATION_ABORTED:
			time.sleep(0.1)	# wait for KeyboardInterrupt
		if not retval:
			raise OSError("Windows error {}".format(GetLastError()))
		
		if buffer[0] == EOF:
			return 0
		else:
			return 2 * code_units_read.value

class WindowsConsoleRawWriter(WindowsConsoleRawIOBase):
	def writable(self):
		return True
	
	@staticmethod
	def _error_message(errno):
		if errno == ERROR_SUCCESS:
			return "Windows error {} (ERROR_SUCCESS); zero bytes written on nonzero input, probably just one byte given".format(errno)
		elif errno == ERROR_NOT_ENOUGH_MEMORY:
			return "Windows error {} (ERROR_NOT_ENOUGH_MEMORY); try to lower `win_unicode_console.streams.MAX_BYTES_WRITTEN`".format(errno)
		else:
			return "Windows error {}".format(errno)
	
	def write(self, b):
		bytes_to_be_written = len(b)
		buffer = get_buffer(b)
		code_units_to_be_written = min(bytes_to_be_written, MAX_BYTES_WRITTEN) // 2
		code_units_written = c_ulong()
		
		retval = WriteConsoleW(self.handle, buffer, code_units_to_be_written, byref(code_units_written), None)
		bytes_written = 2 * code_units_written.value
		
		# fixes both infinite loop of io.BufferedWriter.flush() on when the buffer has odd length
		#	and situation when WriteConsoleW refuses to write lesser that MAX_BYTES_WRITTEN bytes
		if bytes_written == 0 != bytes_to_be_written:
			raise OSError(self._error_message(GetLastError()))
		else:
			return bytes_written

class TextTranscodingWrapper(ReprMixin, io.TextIOBase):
	encoding = None
	
	def __init__(self, base, encoding):
		self.base = base
		self.encoding = encoding
	
	@property
	def errors(self):
		return self.base.errors
	
	@property
	def line_buffering(self):
		return self.base.line_buffering
	
	def seekable(self):
		return self.base.seekable()
	
	def readable(self):
		return self.base.readable()
	
	def writable(self):
		return self.base.writable()
	
	def flush(self):
		self.base.flush()
	
	def close(self):
		self.base.close()
	
	@property
	def closed(self):
		return self.base.closed
	
	@property
	def name(self):
		return self.base.name
	
	def fileno(self):
		return self.base.fileno()
	
	def isatty(self):
		return self.base.isatty()
	
	def write(self, s):
		return self.base.write(s)
	
	def tell(self):
		return self.base.tell()
	
	def truncate(self, pos=None):
		return self.base.truncate(pos)
	
	def seek(self, cookie, whence=0):
		return self.base.seek(cookie, whence)
	
	def read(self, size=None):
		return self.base.read(size)
	
	def __next__(self):
		return next(self.base)
	
	def readline(self, size=-1):
		return self.base.readline(size)
	
	@property
	def newlines(self):
		return self.base.newlines


stdin_raw = WindowsConsoleRawReader("<stdin>", STDIN_HANDLE, STDIN_FILENO)
stdout_raw = WindowsConsoleRawWriter("<stdout>", STDOUT_HANDLE, STDOUT_FILENO)
stderr_raw = WindowsConsoleRawWriter("<stderr>", STDERR_HANDLE, STDERR_FILENO)

stdin_text = io.TextIOWrapper(io.BufferedReader(stdin_raw), encoding="utf-16-le", line_buffering=True)
stdout_text = io.TextIOWrapper(io.BufferedWriter(stdout_raw), encoding="utf-16-le", line_buffering=True)
stderr_text = io.TextIOWrapper(io.BufferedWriter(stderr_raw), encoding="utf-16-le", line_buffering=True)

stdin_text_transcoded = TextTranscodingWrapper(stdin_text, encoding="utf-8")
stdout_text_transcoded = TextTranscodingWrapper(stdout_text, encoding="utf-8")
stderr_text_transcoded = TextTranscodingWrapper(stderr_text, encoding="utf-8")


def disable():
	sys.stdin.flush()
	sys.stdout.flush()
	sys.stderr.flush()
	sys.stdin = sys.__stdin__
	sys.stdout = sys.__stdout__
	sys.stderr = sys.__stderr__

def check_stream(stream, fileno):
	if stream is None:	# e.g. with IDLE
		return True
	
	try:
		_fileno = stream.fileno()
	except io.UnsupportedOperation:
		return False
	else:
		if _fileno == fileno and stream.isatty():
			stream.flush()
			return True
		else:
			return False
	
def enable_reader(*, transcode=True):
		# transcoding because Python tokenizer cannot handle UTF-16
	if check_stream(sys.stdin, STDIN_FILENO):
		if transcode:
			sys.stdin = stdin_text_transcoded
		else:
			sys.stdin = stdin_text

def enable_writer(*, transcode=True):
	if check_stream(sys.stdout, STDOUT_FILENO):
		if transcode:
			sys.stdout = stdout_text_transcoded
		else:
			sys.stdout = stdout_text

def enable_error_writer(*, transcode=True):
	if check_stream(sys.stderr, STDERR_FILENO):
		if transcode:
			sys.stderr = stderr_text_transcoded
		else:
			sys.stderr = stderr_text

enablers = {"stdin": enable_reader, "stdout": enable_writer, "stderr": enable_error_writer}

def enable(streams=("stdin", "stdout", "stderr"), *, transcode=frozenset(enablers.keys())):
	if transcode is True:
		transcode = enablers.keys()
	elif transcode is False:
		transcode = set()
	
	if not set(streams) | set(transcode) <= enablers.keys():
		raise ValueError("invalid stream names")
	
	for stream in streams:
		enablers[stream](transcode=(stream in transcode))

