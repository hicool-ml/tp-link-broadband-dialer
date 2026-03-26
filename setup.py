#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""安装脚本 - 将服务安装为Python包"""

from setuptools import setup

setup(
    name='TPLinkCleanupService',
    version='2.1.0',
    description='TP-Link Router Account Cleanup Service',
    author='Kilo Code',
    # 将服务脚本安装为包
    py_modules=['shutdown_cleanup_service', 'config_manager', 'browser_manager'],
)
