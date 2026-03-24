# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
import os
from pathlib import Path

# 包含项目特定的 Python 模块
project_dir = Path(os.getcwd())
datas = [
    (str(project_dir / 'tplink_http_cleaner.py'), '.'),
]

binaries = []

# 隐藏导入
hiddenimports = [
    'win32service',
    'win32serviceutil',
    'win32event',
    'win32con',
    'servicemanager',
    'win32api',
    'win32timezone',
    'requests',
    'requests.packages',
    'requests.packages.urllib3',
    'requests.packages.urllib3.exceptions',
    'urllib3',
    'urllib3.exceptions',
    'urllib3.packages',
    'tplink_http_cleaner',
    'json',
    'time',
    'logging',
    'pathlib',
    'email',
    'email.message',
    'email.parser',
    'email.generator',
    'email._policybase',
    'email.header',
    'email.charset',
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

# 收集pywin32
tmp_ret = collect_all('pywin32')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

# 收集pywin32_system32
tmp_ret = collect_all('pywin32_system32')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

a = Analysis(
    ['service_http_simple.py'],
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
        'tkinter',
        'playwright',
        'selenium',
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
    name='CleanupService',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='CleanupService',
)
