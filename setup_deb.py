from cx_Freeze import setup, Executable
import sys, platform

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

def getTargetName():
    myOS = platform.system()
    if myOS == 'Linux':
        return "AppName"
    elif myOS == 'Windows':
        return "AppName.exe"
    else:
        return "AppName.dmg"

options = {
    'build_exe': {
        'includes': ["sip", "lxml._elementpath", "encodings", "lxml.etree", "PyQt5.QtCore"],
        'excludes': ["_ssl", "doctest", "pdb", "regex", "scipy"]
    }
}

executables = [
    Executable('start.py', base=base, targetName=getTargetName())
]

setup(name='FMIDownloader',
      version='0.1',
      description='Simple weather downloading',
      options=options,
      executables=executables
      )