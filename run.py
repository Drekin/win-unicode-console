
def run():
	global run
	del run
	
	import sys
	from win_unicode_console import runner, console
	
	script_provided = len(sys.argv) > 1
	
	if len(sys.argv) > 1:
		runner.run_script()
	
	if sys.flags.interactive or not script_provided:
		try:
			console.enable()
		finally:
			runner.set_inspect_flag(0)

run()

