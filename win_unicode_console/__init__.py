
from win_unicode_console import streams, console, readline_hook

streams_ = streams


def enable(*, 
	streams=["stdin", "stdout", "stderr"], 
	transcode=None, 
	use_readline_hook=True, 
	use_pyreadline=True,
	use_repl=False):
	
	if transcode is None:
		if use_readline_hook and use_pyreadline and readline_hook.pyreadline:
			transcode = True
				# pyreadline assumes that encoding of all sys.stdio objects is the same
			
		elif use_repl:
			transcode = False
			
		else:
			transcode = True
				# actually Python REPL assumes that sys.stdin.encoding == sys.stdout.encoding and cannot handle UTF-16 on both input and output
	
	streams_.enable(streams, transcode=transcode)
	
	if use_readline_hook:
		readline_hook.enable(use_pyreadline=use_pyreadline)
	
	if use_repl:
		console.enable()

def disable():
	if console.running_console is not None:
		console.disable()
	
	readline_hook.disable()
	streams.disable()
