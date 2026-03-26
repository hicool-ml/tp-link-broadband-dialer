#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
最小测试服务 - 逐步添加导入
"""

import sys
import os
from pathlib import Path

# 添加site-packages路径
site_packages = r"C:\Program Files\Python311\Lib\site-packages"
if site_packages not in sys.path:
    sys.path.insert(0, site_packages)

# 只导入pywin32核心模块
import win32service
import win32serviceutil
import win32event
import servicemanager

class TestService(win32serviceutil.ServiceFramework):
    """测试服务"""

    _svc_name_ = "TestCleanupService"
    _svc_display_name_ = "Test Cleanup Service"
    _svc_description_ = "Test service for debugging"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_alive = True

        # 立即报告启动中
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

        # 测试：逐步导入模块
        import time
        servicemanager.LogInfoMsg("Step 1: time imported")

        # 测试导入config_manager
        try:
            current_dir = Path(__file__).parent
            sys.path.insert(0, str(current_dir))
            from config_manager import ConfigManager
            servicemanager.LogInfoMsg("Step 2: config_manager imported")
        except Exception as e:
            servicemanager.LogErrorMsg(f"Step 2 failed: {e}")

        # 测试导入browser_manager
        try:
            from browser_manager import BrowserManager
            servicemanager.LogInfoMsg("Step 3: browser_manager imported")
        except Exception as e:
            servicemanager.LogErrorMsg(f"Step 3 failed: {e}")

        # 测试导入playwright
        try:
            from playwright.sync_api import sync_playwright
            servicemanager.LogInfoMsg("Step 4: playwright imported")
        except Exception as e:
            servicemanager.LogErrorMsg(f"Step 4 failed: {e}")

        servicemanager.LogInfoMsg("All imports completed successfully")

        # 主循环
        while self.is_alive:
            result = win32event.WaitForSingleObject(self.hWaitStop, 5000)
            if result == win32event.WAIT_OBJECT_0:
                break

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(TestService)
