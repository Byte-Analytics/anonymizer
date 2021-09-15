Bytewireless Anonymizer
=======================

This directory contains data anonymizer app, which is a separate codebase from 
the main mobile optimizer app.

Setup
=====

On Linux, you'll need to install GTK development libraries appropiate for your distribution 
to be able to build wxPython 4.

Create virtualenv with Python 3.9, eg. 

`mkvirtualenv -p python3.9 bytewireless-anonymizer`

`pip install -f requirements.txt`

To build executable version:
----------------------------
* Run `./build` (Linux/macOS) or `pyinstaller build`

To run from source (CLI):
-------------------------
`python src/anonymizer.py --help`

To run from source (GUI):
-------------------------
`python src/anonymizer.py`
