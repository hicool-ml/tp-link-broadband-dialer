#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""最小的测试服务"""

import sys
import os

# 添加site-packages路径
site_packages = r"C:\Program Files\Python311\Lib\site-packages"
if site_packages not in sys.path:
    sys.path.insert(0, site_packages)

import win32service
import win32serviceutil
import win32event
import servicemanager

class MinTestService(win32serviceutil.ServiceFramework):
    _svc_name_ = "MinTestService"
    _svc_display_name_ = "Minimal Test Service"
    _svc_description_ = "Minimal test"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_alive = True
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        while self.is_alive:
            result = win32event.WaitForSingleObject(self.hWaitStop, 1000)
            if result == win32event.WAIT_OBJECT_0:
                break

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.is_alive = False
        win32event.SetEvent(self.hWaitStop)
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(MinTestService)
