
from .info import check_Windows, PY2
check_Windows()

from . import streams, console, readline_hook

if PY2:
	from . import raw_input


# PY3 # def enable(*, 
def enable(
		stdin = Ellipsis, 
		stdout = Ellipsis, 
		stderr = Ellipsis, 
		use_readline_hook = True, 
		use_pyreadline = True, 
		use_raw_input = True, # PY2
		raw_input__return_unicode = raw_input.RETURN_UNICODE if PY2 else None, 
		use_repl = False#, 
	):
	
	streams.enable(stdin=stdin, stdout=stdout, stderr=stderr)
	
	if use_readline_hook:
		readline_hook.enable(use_pyreadline=use_pyreadline)
	
	if PY2 and use_raw_input:
		raw_input.enable(raw_input__return_unicode)
	
	if use_repl:
		console.enable()

def disable():
	if console.running_console is not None:
		console.disable()
	
	if PY2:
		raw_input.disable()
	
	readline_hook.disable()
	streams.disable()
