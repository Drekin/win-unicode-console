
import __builtin__ as builtins

from .readline_hook import readline
from .info import assure_PY2


assure_PY2()


original_raw_input = builtins.raw_input
original_input = builtins.input


def raw_input(prompt=""):
	"""raw_input([prompt]) -> string

Read a string from standard input.  The trailing newline is stripped.
If the user hits EOF (Unix: Ctl-D, Windows: Ctl-Z+Return), raise EOFError.
On Unix, GNU readline is used if enabled.  The prompt string, if given,
is printed without a trailing newline before reading."""
	
	line = readline(prompt)
	if line:
		return line[:-1] # strip strailing "\n"
	else:
		raise EOFError

def input(prompt=""):
	"""input([prompt]) -> value

Equivalent to eval(raw_input(prompt))."""
	
	return eval(raw_input(prompt))


def enable():
	builtins.raw_input = raw_input
	builtins.input = input

def disable():
	builtins.raw_input = original_raw_input
	builtins.input = original_input
