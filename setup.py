
import os.path as path
from io import open # PY2
from setuptools import setup


ENCODING = "UTF-8"
HERE = path.abspath(path.dirname(__file__))

def read(*relative_path_parts):
	with open(path.join(HERE, *relative_path_parts), encoding=ENCODING) as f:
		return f.read()

VERSION = "0.5"
README = "README.rst"
URL = "https://github.com/Drekin/win-unicode-console"

setup(
	name="win_unicode_console",
	version=VERSION,
	
	packages=["win_unicode_console"],
	py_modules=["run"],
	
	author="Drekin",
	author_email="drekin@gmail.com",
	license="MIT",
	url=URL,
	download_url="{}/archive/{}.zip".format(URL, VERSION),
	
	description="Enable Unicode input and display when running Python from Windows console.",
	long_description=read(README),
	keywords=["Windows", "Unicode", "console"],
	classifiers=[
		"Development Status :: 4 - Beta", 
		"Environment :: Console", 
		"Intended Audience :: Developers", 
		"License :: OSI Approved :: MIT License", 
		"Operating System :: Microsoft :: Windows", 
		"Programming Language :: Python :: 3", 
		"Programming Language :: Python :: 3.4", 
		"Programming Language :: Python :: 3.5", 
		"Programming Language :: Python :: 2", 
		"Programming Language :: Python :: 2.7", 
	]
)
