"""
TP-Link路由器账号清理服务
使用pythonservice.exe启动，避免PyInstaller打包问题
"""

import sys
import os
import subprocess
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

            # 调用cleanup_worker.exe
            cleanup_exe = Path(__file__).parent / "cleanup_worker.exe"

            if cleanup_exe.exists():
                try:
                    subprocess.run(
                        [str(cleanup_exe)],
                        capture_output=True,
                        timeout=100,
                        cwd=str(cleanup_exe.parent)
                    )
                except:
                    pass

        except:
            pass

        self.is_alive = False
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        """服务主循环 - 极简版"""
        try:
            # 立即报告运行状态
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)

            # 记录启动
            try:
                servicemanager.LogInfoMsg("TP-Link路由器账号清理服务已启动")
            except:
                pass

            # 主循环
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
