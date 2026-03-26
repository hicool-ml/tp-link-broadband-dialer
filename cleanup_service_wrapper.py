#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
清理服务包装器 - 最小化版本
只负责启动时记录日志，关机时调用Python脚本
"""

import sys
import os
import subprocess
import win32service
import win32serviceutil
import win32event
import servicemanager
from pathlib import Path

class CleanupServiceWrapper(win32serviceutil.ServiceFramework):
    """清理服务包装器"""

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
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING, waitHint=120000)

        try:
            # 获取脚本路径
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller打包后的路径
                script_dir = Path(sys.executable).parent
            else:
                script_dir = Path(__file__).parent

            script_path = script_dir / "shutdown_cleanup_service_final.py"

            if script_path.exists():
                # 使用Python运行脚本
                python_exe = r"C:\Program Files\Python311\python.exe"

                # 如果找不到Python，尝试使用sys.executable
                if not os.path.exists(python_exe):
                    python_exe = sys.executable

                # 调用清理脚本
                result = subprocess.run(
                    [python_exe, str(script_path), "--cleanup-only"],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    cwd=str(script_dir)
                )

                # 记录结果
                if result.stdout:
                    servicemanager.LogInfoMsg(result.stdout[:1000])
                if result.stderr:
                    servicemanager.LogWarningMsg(result.stderr[:1000])
            else:
                servicemanager.LogErrorMsg(f"找不到清理脚本: {script_path}")

        except Exception as e:
            servicemanager.LogErrorMsg(f"清理失败: {str(e)}")

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
        count = 0
        while self.is_alive:
            result = win32event.WaitForSingleObject(self.hWaitStop, 5000)

            if result == win32event.WAIT_OBJECT_0:
                break

            count += 1
            # 每分钟记录一次心跳
            if count % 12 == 0:
                try:
                    servicemanager.LogInfoMsg(f"服务运行中... ({count // 12}分钟)")
                except:
                    pass


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(CleanupServiceWrapper)
