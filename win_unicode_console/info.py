
import sys
import platform


PY2 = sys.version_info.major < 3


def check_Windows():
	current_platform = platform.system()
	
	if current_platform.lower() != "windows":
		raise RuntimeError("win_unicode_console is for Windows only, not {}.".format(current_platform))


def assure_PY2():
	if not PY2:
		raise RuntimeError("the following is needed only in Python 2")
