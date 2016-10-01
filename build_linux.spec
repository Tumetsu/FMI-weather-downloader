# -*- mode: python -*-
# https://pythonhosted.org/PyInstaller/spec-files.html#spec-file-operation
block_cipher = None


a = Analysis(['start.py'],
             pathex=['/home/tuomas/Code/FMI-weather-downloader'],
             binaries=None,
             datas=[('./data', './data'),
                          ('./translations', './translations'),
                          ('readme.md', '.'),
                          ('license', '.'),
                          ('icon.ico', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[('tests')],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='FMIDownloader',
          debug=False,
          strip=False,
          upx=True,
          icon="icon.ico",
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='start')
