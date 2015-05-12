# -*- mode: python -*-
a = Analysis(['server.py'],
             pathex=['~/programming/python/SW-Contest/Ship-Fighters'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)

for d in a.datas:
    if 'pyconfig' in d[0]: 
        a.datas.remove(d)
        break

pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas+Tree('./res', prefix='res'),
          name='server.exe',
		  icon='ship_icon.ico',
          debug=False,
          strip=None,
          upx=True,
          console=False)
