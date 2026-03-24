#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TP-Link 路由器账号清理服务 - HTTP 版本（简洁版）
使用 HTTP 接口直接操作路由器，不使用浏览器
"""

import win32service
import win32serviceutil
import win32event
import servicemanager

import time
import json
import os
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from tplink_http_cleaner import TPLinkHTTPCleaner


# =========================
# HTTP 客户端封装（适配服务接口）
# =========================
class TPLinkHTTPClient:
    def __init__(self, router_ip, password, logger):
        self.cleaner = TPLinkHTTPCleaner(router_ip, password)
        self.logger = logger

        # 替换 cleaner 的日志方法
        self.cleaner._log = logger

    def run(self):
        # 使用 TPLinkHTTPCleaner 的清理流程
        return self.cleaner.run_cleanup()


# =========================
# Windows 服务
# =========================
class TPLinkCleanupService(win32serviceutil.ServiceFramework):
    _svc_name_ = "TPLinkCleanupService"
    _svc_display_name_ = "TP-Link 账号清理服务 (HTTP版)"
    _svc_description_ = "系统关机时自动清除路由器宽带账号"

    def __init__(self, args):
        super().__init__(args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.is_alive = True

        self.log_file = Path(os.environ.get("TEMP", "C:\\Temp")) / "tplink_cleanup.log"

    def log(self, msg):
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")
        except:
            pass

    def SvcStop(self):
        self.log("收到停止请求")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.is_alive = False
        win32event.SetEvent(self.stop_event)

    def SvcShutdown(self):
        self.log("🚨 收到关机事件")

        try:
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING, waitHint=120000)

            # ===== 读取配置 =====
            config_file = Path(os.environ.get("USERPROFILE", ".")) / ".tplink_dialer" / "config.json"

            if not config_file.exists():
                self.log("⚠️ 配置文件不存在，跳过清理")
                return

            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)

            router_ip = config.get("router_ip", "192.168.1.1")
            router_password = config.get("router_password", "")

            if not router_password:
                self.log("⚠️ 路由器密码未配置，跳过清理")
                return

            self.log(f"路由器IP: {router_ip}")
            self.log(f"路由器密码: {'***' if router_password else '(未设置)'}")

            # ===== 执行清理 =====
            client = TPLinkHTTPClient(router_ip, router_password, self.log)
            client.run()

        except Exception as e:
            self.log(f"❌ 清理异常: {e}")
            import traceback
            self.log(traceback.format_exc())

        self.is_alive = False
        win32event.SetEvent(self.stop_event)

    def SvcDoRun(self):
        self.log("=" * 60)
        self.log("✅ 服务已启动")
        self.log("=" * 60)

        self.ReportServiceStatus(win32service.SERVICE_RUNNING)

        while self.is_alive:
            win32event.WaitForSingleObject(self.stop_event, 5000)


# =========================
# 入口
# =========================
if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(TPLinkCleanupService)
