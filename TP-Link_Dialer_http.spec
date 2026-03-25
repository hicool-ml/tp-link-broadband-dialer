# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

# 收集所有需要的数据文件
datas = [
    ('app.ico', '.'),
    ('offline.ico', '.'),
]

binaries = []

# 隐藏导入
hiddenimports = [
    'tkinter',
    'queue',
    'threading',
    'ctypes',
    're',
    'time',
    'atexit',
    'config_manager',
    'tplink_http_cleaner',
    'requests',
    'requests.packages',
    'requests.packages.urllib3',
    'requests.packages.urllib3.exceptions',
    'urllib3',
    'urllib3.exceptions',
    'json',
    'hashlib',
    'base64',
    'pathlib',
    'email',
    'email.message',
]

# 收集 requests
tmp_ret = collect_all('requests')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

# 收集 urllib3
tmp_ret = collect_all('urllib3')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

a = Analysis(
    ['tp_link_broadband_dialer_http.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'unittest',
        'setuptools',
        'pip',
        'pydoc',
        'doctest',
        'pytest',
        'playwright',
        'selenium',
        'PIL',
        'pystray',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TP-Link_Dialer_HTTP',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='TP-Link_Dialer_HTTP',
)
