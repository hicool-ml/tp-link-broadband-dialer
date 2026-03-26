#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
最小化测试服务 - 用于调试1053错误
"""

import sys
import os
from pathlib import Path

# 添加site-packages路径
site_packages = r"C:\Program Files\Python311\Lib\site-packages"
if site_packages not in sys.path:
    sys.path.insert(0, site_packages)

import win32service
import win32serviceutil
import win32event
import servicemanager
import time

class MinimalTestService(win32serviceutil.ServiceFramework):
    """最小化测试服务"""

    _svc_name_ = "MinimalTestService"
    _svc_display_name_ = "Minimal Test Service"
    _svc_description_ = "A minimal test service for debugging"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_alive = True

        # 立即报告状态
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.is_alive = False
        win32event.SetEvent(self.hWaitStop)
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def SvcDoRun(self):
        # 立即报告运行状态
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )

        # 等待停止信号
        while self.is_alive:
            win32event.WaitForSingleObject(self.hWaitStop, 3000)

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(MinimalTestService)
