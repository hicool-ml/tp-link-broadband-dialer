#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TP-Link路由器账号清理服务 - 极简版本
架构：服务只负责调用cleanup_worker.exe，完全不接触Playwright
"""

import sys
import os
import subprocess
import threading
from pathlib import Path

# 只导入Windows服务核心模块
import win32service
import win32serviceutil
import win32event
import servicemanager


class ShutdownCleanupService(win32serviceutil.ServiceFramework):
    """关机清理服务 - 极简架构"""

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
        try:
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING, waitHint=120000)

            # ✅ 关键：调用独立exe执行清理，不在服务中启动浏览器
            cleanup_exe = Path(__file__).parent / "cleanup_worker.exe"

            if cleanup_exe.exists():
                try:
                    # 使用subprocess调用独立exe
                    subprocess.run(
                        [str(cleanup_exe)],
                        capture_output=True,
                        timeout=100,
                        cwd=str(cleanup_exe.parent)
                    )
                except subprocess.TimeoutExpired:
                    # 超时也继续
                    pass
                except Exception:
                    # 出错也继续
                    pass

        except Exception:
            pass

        self.is_alive = False
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        """服务主循环 - 极简版"""
        try:
            # ⭐ 立即报告运行状态（避免1053）
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)

            # 记录启动
            try:
                servicemanager.LogInfoMsg("TP-Link路由器账号清理服务已启动")
            except:
                pass

            # 验证cleanup_worker.exe存在
            cleanup_exe = Path(__file__).parent / "cleanup_worker.exe"
            if not cleanup_exe.exists():
                try:
                    servicemanager.LogWarningMsg(f"cleanup_worker.exe不存在: {cleanup_exe}")
                except:
                    pass

            # 主循环：只负责"活着"
            while self.is_alive:
                try:
                    result = win32event.WaitForSingleObject(self.hWaitStop, 5000)
                    if result == win32event.WAIT_OBJECT_0:
                        break
                except:
                    pass

        except Exception as e:
            try:
                servicemanager.LogErrorMsg(f"服务错误: {str(e)}")
            except:
                pass
            self.ReportServiceStatus(win32service.SERVICE_STOPPED)


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(ShutdownCleanupService)
