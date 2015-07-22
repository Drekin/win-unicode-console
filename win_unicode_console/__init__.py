
from . import info
info.check_Windows()

from . import streams, console, readline_hook


def enable(*, 
		stdin = Ellipsis, 
		stdout = Ellipsis, 
		stderr = Ellipsis, 
		use_readline_hook = True, 
		use_pyreadline = True,
		use_repl = False#, 
	):
	
	streams.enable(stdin=stdin, stdout=stdout, stderr=stderr)
	
	if use_readline_hook:
		readline_hook.enable(use_pyreadline=use_pyreadline)
	
	if use_repl:
		console.enable()

def disable():
	if console.running_console is not None:
		console.disable()
	
	readline_hook.disable()
	streams.disable()
