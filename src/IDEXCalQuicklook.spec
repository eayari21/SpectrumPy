# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['windows-qt.py'],
             pathex=['/Users/ethanayari/Dropbox/Mac/Documents/GitHub/SpectrumPy copy/python_dev'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='IDEXCalQuicklook',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False , icon='impact.ico')
app = BUNDLE(exe,
             name='IDEXCalQuicklook.app',
             icon='impact.ico',
             bundle_identifier=None)
