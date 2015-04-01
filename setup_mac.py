from distutils.core import setup
from setuptools import setup

setup(app=["start.py"],
      setup_requires=["py2app"],
      windows=[{"script":"start.py",
                "dest_base" : "FMIDownloader",
                "icon_resources": [(1, "icon.ico")]}],


      options={
          "py2app":{
              "includes":["sip", "lxml._elementpath", "lxml.etree", "pandas", "PyQt5.QtCore"],
              "excludes":["_ssl","doctest", "pdb", "regex", "macholib", "altgraph", "nose", "modulegraph", "scikit-learn", "scipy", "twitter"]
          }
      })
