from distutils.core import setup
import py2exe
setup(windows=[{"script":"start.py"}],
      options={
          "py2exe":{
              "includes":["sip", "lxml._elementpath", "lxml.etree", "pandas", "PyQt5.QtCore"]
          }
      })