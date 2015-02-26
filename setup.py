from distutils.core import setup
import py2exe
setup(windows=[{"script":"start.py",
                "dest_base" : "FMIDownloader",
                "icon_resources": [(1, "icon.ico")]}],


      options={
          "py2exe":{
              "includes":["sip", "lxml._elementpath", "lxml.etree", "pandas", "PyQt5.QtCore"]
          }
      })