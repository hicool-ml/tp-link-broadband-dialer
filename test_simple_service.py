#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""最简单的测试服务"""

import sys
import os
import win32service
import win32serviceutil
import win32event
import servicemanager
from pathlib import Path

class SimpleTestService(win32serviceutil.ServiceFramework):
    _svc_name_ = "TestService"
    _svc_display_name_ = "Simple Test Service"
    _svc_description_ = "A simple test service"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_alive = True

        # 尝试创建日志
        try:
            log_dir = Path(os.environ.get('TEMP', '/tmp')) / 'test_service'
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / 'test.log'
            with open(log_file, 'w') as f:
                f.write("Service __init__ called\n")
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                ('Service initialized',)
            )
        except Exception as e:
            pass

    def SvcDoRun(self):
        try:
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                ('Service starting',)
            )

            # 写入日志
            log_dir = Path(os.environ.get('TEMP', '/tmp')) / 'test_service'
            log_file = log_dir / 'test.log'
            with open(log_file, 'a') as f:
                f.write("SvcDoRun called\n")

            self.ReportServiceStatus(win32service.SERVICE_RUNNING)

            # 等待停止信号
            while self.is_alive:
                result = win32event.WaitForSingleObject(self.hWaitStop, 1000)
                if result == win32event.WAIT_OBJECT_0:
                    break

        except Exception as e:
            pass

    def SvcStop(self):
        self.is_alive = False
        win32event.SetEvent(self.hWaitStop)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        win32serviceutil.HandleCommandLine(SimpleTestService)
