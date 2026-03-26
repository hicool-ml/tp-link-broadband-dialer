#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
服务包装器 - 简单启动Python脚本
"""

import sys
import os
import subprocess
import win32service
import win32serviceutil
import win32event
import servicemanager
from pathlib import Path

class ServiceWrapper(win32serviceutil.ServiceFramework):
    """服务包装器"""

    _svc_name_ = "TPLinkShutdownCleanup"
    _svc_display_name_ = "TP-Link路由器账号清理服务"
    _svc_description_ = "在系统关机时自动清除TP-Link路由器中的宽带账号密码"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_alive = True

        # 立即报告启动中
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)

    def SvcStop(self):
        """停止服务"""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.is_alive = False
        win32event.SetEvent(self.hWaitStop)
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def SvcShutdown(self):
        """关机时的处理"""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING, waitHint=60000)

        # 启动Python脚本执行清理
        try:
            script_path = Path(__file__).parent / "shutdown_cleanup_service.py"
            python_exe = r"C:\Program Files\Python311\python.exe"

            if script_path.exists():
                # 使用subprocess调用Python脚本
                result = subprocess.run(
                    [python_exe, str(script_path), "cleanup"],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    cwd=str(script_path.parent)
                )
                servicemanager.LogInfoMsg(
                    f"清理完成: {result.stdout}\n{result.stderr}"
                )
        except Exception as e:
            servicemanager.LogErrorMsg(f"清理失败: {e}")

        self.is_alive = False
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        """服务主循环"""
        # 立即报告运行状态
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )

        # 主循环
        while self.is_alive:
            win32event.WaitForSingleObject(self.hWaitStop, 5000)


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(ServiceWrapper)
