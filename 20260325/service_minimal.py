#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
最简单的Windows服务 - 用于测试1053问题
"""

import sys
import win32service
import win32serviceutil
import win32event

class MinimalService(win32serviceutil.ServiceFramework):
    _svc_name_ = "TPLinkMinimalTest"
    _svc_display_name_ = "TP-Link最小测试服务"
    _svc_description_ = "最小化测试服务"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        # 立即报告RUNNING状态
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        # 等待停止信号
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(MinimalService)
