
import code
import sys
import __main__


def print_banner():
	print("Python {} on {}".format(sys.version, sys.platform))
	print('Type "help", "copyright", "credits" or "license" for more information.')

class InteractiveConsole(code.InteractiveConsole):
	# code.InteractiveConsole without banner
	# exits on EOF
	# also more robust treating of sys.ps1, sys.ps2
	# prints prompt into stderr rather than stdout
	# flushes sys.stderr and sys.stdout
	
	def __init__(self, locals=None, filename="<stdin>"):
		self.done = False
		super().__init__(locals, filename)
	
	def raw_input(self, prompt=""):
		sys.stderr.write(prompt)
		return input()
	
	def runcode(self, code):
		super().runcode(code)
		sys.stderr.flush()
		sys.stdout.flush()
	
	def interact(self):
		#sys.ps1 = "~>> "
		#sys.ps2 = "~.. "
		
		try:
			sys.ps1
		except AttributeError:
			sys.ps1 = ">>> "
		
		try:
			sys.ps2
		except AttributeError:
			sys.ps2 = "... "
		
		more = 0
		while not self.done:
			try:
				if more:
					try:
						prompt = sys.ps2
					except AttributeError:
						prompt = ""
				else:
					try:
						prompt = sys.ps1
					except AttributeError:
						prompt = ""
				
				try:
					line = self.raw_input(prompt)
				except EOFError:
					self.on_EOF()
				else:
					more = self.push(line)
				
			except KeyboardInterrupt:
				self.write("\nKeyboardInterrupt\n")
				self.resetbuffer()
				more = 0
	
	def on_EOF(self):
		self.write("\n")
		# sys.exit()
		raise SystemExit from None


running_console = None

def enable():
	global running_console
	
	if running_console is not None:
		raise RuntimeError("interactive console already running")
	else:
		running_console = InteractiveConsole(__main__.__dict__) 
		running_console.interact() 

def disable():
	global running_console
	
	if running_console is None:
		raise RuntimeError("interactive console is not running")
	else:
		running_console.done = True
		running_console = None

