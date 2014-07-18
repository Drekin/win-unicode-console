win-unicode-console
===================

A Python package to enable Unicode support when running Python from Windows console.

Rationale
---------

When running Python in the standard console on Windows, there are several problems when one tries to enter or display Unicode characters. Part of this problem lies in the fact that Python doesn't use the right functions (i.e. ReadConsoleW and WriteConsoleW) when interacting with Windows console (see http://bugs.python.org/issue1602). The module `streams` of our `win_unicode_concole` package provides alternative raw stream objects which are then intercorporated to the standard IO hierarchy (text –> buffer –> raw). Resulting objects `streams.stdin`, `streams.stdout`, and `streams.stderr` can be used instead of `sys.std*` objects. The function `streams.enable` replaces the standard `sys.std*` objects with our ones and `streams.disable` reinstalls the original ones.

Replacing the stream objects solves the problem for standard IO. That is, everything which uses the standard objects for IO (e.g. `input()`, `print()`, output in Python interactive loop) works. But there is another problem – Python interactive loop doesn't use `sys.stdin` for input (see http://bugs.python.org/issue17620) so an alternative implementation of interactive loop is provided in `console` module and its functions `enable` and `disable` maintains (de)activation of our loop.

Since there is no hook to run our interactive loop instead of the standard one, we have to wrap the execution of any Python script so our loop is run at the right place. The logic for this is contained in `runner` module and a helper script `run.py` which is located outside of out package for practical reasons.

Usage
-----

Move the directory `win_unicode_console` and files `sitecustomize.py`, `run.py` to `site-packages` directory of your Python installation to manually install our package (in the case of already present customized `sitecustomize.py`, just adjust it manually). The commands in `sitecustomize.py` activate our custom `sys.stdin`, `sys.stdout`, `sys.stderr` objects which accept Unicode. This module is run by Python automatically on startup.

Since standard Python REPL doesn't use sys.stdin for input, custom REPL has to be installed in order to enter Unicode interactivelly. To do this run Python scripts by `py -m run script.py` instead of `py script.py`. You can put `"C:\Windows\py.exe" -i -m run "%1" %*` to the registry in order to run .py files interactivelly and using custom REPL. To run the custom REPL when plain interactive console is run (just 'py') add environment variable `PYTHONSTARTUP` pointing to `site-packages\run.py`.

Acknowledgements
----------------

The code of `streams` module is based the code submited to http://bugs.python.org/issue1602.
