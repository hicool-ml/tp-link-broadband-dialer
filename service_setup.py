#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cx_Freeze配置文件 - 用于打包清理服务
"""

import sys
from cx_Freeze import setup, Executable

# 依赖包
build_exe_options = {
    "packages": [
        "win32service",
        "win32serviceutil",
        "win32event",
        "servicemanager",
        "playwright",
        "config_manager",
        "browser_manager",
    ],
    "includes": [
        "win32timezone",
        "pywintypes",
        "win32api",
        "win32con",
    ],
    "excludes": [
        "unittest",
        "setuptools",
        "pip",
        "email",
        "pydoc",
        "doctest",
        "pytest",
        "tkinter",
        "test",
        "json",
        "http.server",
    ],
    "optimize": 0,
}

# 服务可执行文件
base = None
if sys.platform == "win32":
    base = "Win32Service"

executable = [
    Executable(
        "shutdown_cleanup_service_final.py",
        base=base,
        target_name="CleanupService.exe",
    )
]

setup(
    name="CleanupService",
    version="2.1.1",
    description="TP-Link路由器账号清理服务",
    options={"build_exe": build_exe_options},
    executables=executable,
)
