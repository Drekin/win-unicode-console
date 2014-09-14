
def run():
	global run
	del run
	
	import sys
	from win_unicode_console import runner, console, streams
	
	streams.enable(transcode=False)	# transcoding not needed with custom REPL
	script_provided = len(sys.argv) > 1
	
	if script_provided:
		runner.run_script()
	
	if sys.flags.interactive or not script_provided:
		if sys.flags.interactive and not script_provided:
			console.print_banner()
		try:
			console.enable()
		finally:
			runner.set_inspect_flag(0)

if __name__ == "__main__":
	run()
