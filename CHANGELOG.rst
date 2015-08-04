
Changelog
=========

0.4
---

- Python 2 is now supported. Fixes #7.
- The ``runner`` package and ``run`` script were enhanced. Since custom REPL is not needed, it is not used by default, and the runner serves as a way to execute initialization code before running a main script. There are more options for the an initialization code, see the readme file or ``run`` script help.
- The package can be now imported on Unix and other platforms. The top-level ``enable`` function does nothing on platforms other than Windows. Fixes #8.
- The signature of ``streams.enable`` was changed. ``streams.enable_only`` function was added. The functions ``enable_reader``, ``enable_writer``, and ``enable_error_writer`` in ``streams`` module were removed.
- When ``sys.stdin.encoding != sys.stdout.encodin``, ``RuntimeWarning`` is raised by ``readline_hook`` module rather than ``ValueError``.
- The readme file was mostly rewritten.
- A changelog file was added.


0.3.1
-----

- Changed the loader of msvcrt library from windll to cdll. Solved #5.


0.3
---

- Added possibility to set custom readline hook. Also ``pyreadline`` hook can be reused. Custom REPL is no longer needed.
- Added transcoding wrappers to streams, since there is a problem with UTF-16 encoding.
- New interface ``win_unicode_console.enable``, ``.disable``.
- Stream objects have standard filenos now, custom readline hook is needed for ``input()``.


0.2
---

- Better treatment of reading zero or one bytes so infinite loops aren't started on higher levels.
- Added automatical flushing in REPL.
- Interaction with Python object to read and write bytes now uses buffer protocol.
- Changed type of read/written bytes variable from c_long to c_ulong to be compatible with pyreadlines and the specification, which says DWORD. Solves #2.


0.1.2
-----

- Added ``__init__.py`` for better compatibility, see issue #1.


0.1.1
-----

- Better handling of OS level errors on read or write.
- Writing a single byte to the raw stream raises an exception so a buffer of odd length no more loops on ``flush()``.
- There is now maximum limit for bytes to be written by the raw stream so at least something is written (see http://bugs.python.org/issue11395).


0.1
---

- Initial release.
