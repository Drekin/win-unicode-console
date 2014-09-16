
win-unicode-console
===================

A Python package to enable Unicode input and display when running Python from Windows console.

General information
-------------------

When running Python in the standard console on Windows, there are several problems when one tries to enter or display Unicode characters. The relevant issue is http://bugs.python.org/issue1602. This package solves some of them.

- First, when you want to display Unicode characters in Windows console, you have to select a font able to display them. This has nothing to do with Python, but is included here for completeness.
  
- The standard stream objects (``sys.stdin``, ``sys.stdout``, ``sys.stderr``) are not capable of reading and displaying Unicode characters in Windows console. This has nothing to do with encoding, since even ``sys.stdin.buffer.raw.readline()`` returns ``b"?\n"`` when entering ``α`` and there is no encoding under which ``sys.stdout.buffer.raw.write`` displays ``α``.
  
  The ``streams`` module provides alternative streams objects, which call ``ReadConsoleW`` and ``WriteConsoleW`` functions to interact with Windows console. The function ``streams.enable`` installs these streams instead of original ones and ``streams.disable`` restores the original ones. After replacing the stream objects, also using ``print`` with a string containing Unicode characters and displaying Unicode characters in the interactive loop works. For ``input``, see below.
  
- Python interactive loop doesn't use ``sys.stdin`` to read input so fixing it doesn't help. Also the ``input`` function may or may not use ``sys.stdin`` depending on whether ``sys.stdin`` and ``sys.stdout`` have the standard filenos. See http://bugs.python.org/issue17620 for more information.
  
  One way to solve this problem is to provide custom REPL which uses the streams. Such REPL is implemented in ``console`` module and based on stdlib module ``code``. The functions ``console.enable`` and ``console.disable`` maintain (de)activation of our loop.
  
  Since there is no hook to run our interactive loop instead of the standard one, we have to wrap the execution of any Python script so our loop is run at the right place. The logic for this is contained in ``runner`` module and a helper script ``run.py``, which is located outside of out package for practical reasons.
  
  Another and more practical solution is to install a custom readline hook. Readline hook is a function which is used to read a single line interactively by Python REPL. It may also be used by ``input`` function under certain conditions (see above). On Linux, this hook is usually set to GNU readline function, which provides features like autocompletion, history,…
  
  The module ``readline_hook`` provides our custom readline hook, which uses ``sys.stdin`` to get the input and is (de)activated by functions ``readline_hook.enable``, ``readline_hook.disable``. There also exists package ``pyreadline`` (https://github.com/pyreadline/pyreadline), which implements GNU readline features on Windows. It provides its own readline hook, which actually supports Unicode input. The problem is, that the input is then encoded using ``sys.stdout.encoding``, which may not be capable of encoding all the characters. Our custom stream objects solve the problem, so the readline hook of ``pyreadline`` can be used as well, and ``readline_hook.enable`` tries to use it if possible as default to preserve the input features of ``pyreadline``.
  
- Readline hook can be called from two places – from the REPL and from ``input`` function. In the first case the prompt is encoded using ``sys.stdin.encoding``, but in the second case ``sys.stdout.encoding`` is used. So we need these two encodings be equal.
  
- Python tokenizer, which is used when parsing the input from REPL, cannot handle UTF-16 or generally any encoding containing null bytes. Because UTF-16-LE is the encoding of Unicode used by Windows, we have to additionally wrap our text stream objects (``io.TextIOWrapper`` with encoding UTF-16-LE over our raw console stream objects) with helper text io objects. This is done automatically by ``streams.enable`` when needed and can be configured.

``win_unicode_console`` package was tested on Python 3.4 and interacts well with ``pyreadline``, ``IPython``, and ``colorama`` packages.


Installation
------------

Install the package from PyPI via ``pip install win-unicode-console`` (recommended) or download the archive and install it from the archive (e.g. ``pip install win_unicode_console-0.3.zip``) or install the package manually by placing directory ``win_unicode_console`` and module ``run.py`` from the archive to ``site-packages`` directory of your Python installation.


Usage
-----

Recommened usage is just calling ``win_unicode_console.enable()`` whenever the fixes should be applied and ``win_unicode_console.disable()`` to revert all the changes. By default, custom stream objects are installed as well as custom readline hook. In the case that ``pyreadline`` is available, its readline hook is reused. For customization, see the sources. The logic should be clear.

Calling ``win_unicode_console.enable()`` may be done automatically on Python startup by putting the command to your ``sitecustomize`` or ``usercustomize`` script. See https://docs.python.org/3/tutorial/interpreter.html#the-customization-modules for more information.

To run a Python script with our custom REPL (which is not needed with the approach above), type ``py -i -m run script.py`` instead of ``py -i script.py``. You can also put ``"C:\Windows\py.exe" -i -m rum "%1" %*`` to the registry in order to run .py files interactivelly and using custom REPL. To run the custom REPL when plain interactive console is run (just 'py') add environment variable ``PYTHONSTARTUP`` pointing to ``site-packages\run.py``.


Backward incompatibility
------------------------

From version 0.3, the custom stream objects have the standard filenos, so calling ``input`` doesn't handle Unicode without custom readline hook.


Acknowledgements
----------------

- The code of ``streams`` module is based on the code submited to http://bugs.python.org/issue1602.
- The idea of providing custom readline hook and the code of ``readline_hook`` module is based on https://github.com/pyreadline/pyreadline.
