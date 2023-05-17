Bytewireless Anonymizer
=======================

This directory contains data anonymizer app, which is a separate codebase from the main mobile optimizer app.

Setup
=====

On Linux, you'll need to install GTK development libraries appropiate for your distribution to be able to build
wxPython4.

On macOS, using `pyenv` you might need to install framework as well

```shell
PYTHON_CONFIGURE_OPTS="--enable-framework" pyenv install 3.
```

On linux `--enable-shared` is said to work instead.

Create virtualenv with Python 3.9, e.g.

`mkvirtualenv -p python3.9 bytewireless-anonymizer`

`pip install -r requirements.txt`

To build executable version:
----------------------------

* Run `pyinstaller build.spec`

To run from source (CLI):
-------------------------
`python anonymizer.py --help`

To run from source (GUI):
-------------------------
`python anonymizer.py`
