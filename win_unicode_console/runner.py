
import __main__
import argparse
import sys
import traceback
import tokenize
from ctypes import pythonapi, POINTER, c_long, cast
from types import CodeType as Code

from . import console, enable


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


def print_exception_without_first_line(etype, value, tb, limit=None, file=None, chain=True):
	if file is None:
		file = sys.stderr
	
	lines = iter(traceback.TracebackException(
		type(value), value, tb, limit=limit).format(chain=chain))
	
	next(lines)
	for line in lines:
		print(line, file=file, end="")


def run_script(args):
	sys.argv = [args.script] + args.script_arguments
	path = args.script
	__main__.__file__ = path
	
	try:
		code = get_code(path)
	except Exception as e:
		print_exception_without_first_line(e.__class__, e, e.__traceback__.tb_next.tb_next)
	else:
		try:
			exec(code, __main__.__dict__)
		except BaseException as e:
			if not sys.flags.inspect and isinstance(e, SystemExit):
				raise
			else:
				traceback.print_exception(e.__class__, e, e.__traceback__.tb_next)

def run_with_custom_repl(args):
	enable()
	
	if args.script:
		run_script(args)
	
	if sys.flags.interactive or not args.script:
		if sys.flags.interactive and not args.script:
			console.print_banner()
		try:
			console.enable()
		finally:
			set_inspect_flag(0)

def run_with_standard_repl(args):
	enable()
	
	if args.script:
		run_script(args)
	
	if sys.flags.interactive and not args.script:
		console.print_banner()

def run_arguments():
	parser = argparse.ArgumentParser(description="Runs a script with win_unicode_console enabled.")
	
	group = parser.add_mutually_exclusive_group()
	group.add_argument("--custom-repl", dest="use_repl", action="store_true", 
		help="use win_unicode_console.console REPL")
	group.add_argument("--standard-repl", dest="use_repl", action="store_false", 
		help="use the standard Python REPL (default)")
	parser.set_defaults(use_repl=False)
	
	parser.add_argument("script", nargs="?")
	parser.add_argument("script_arguments", nargs=argparse.REMAINDER, metavar="script-arguments")
	
	try:
		args = parser.parse_args(sys.argv[1:])
	except SystemExit:
		set_inspect_flag(0)	# don't go interactive after printing help
		raise
	
	if args.use_repl:
		run_with_custom_repl(args)
	else:
		run_with_standard_repl(args)
