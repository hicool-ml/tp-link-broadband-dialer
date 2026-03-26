#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import time
import logging
from pathlib import Path

import win32service
import win32serviceutil
import win32event


class TPLinkCleanupServiceHTTP(win32serviceutil.ServiceFramework):

    _svc_name_ = "TPLinkShutdownCleanup"
    _svc_display_name_ = "TP-Link路由器账号清理服务"
    _svc_description_ = "关机自动清除路由器账号（HTTP版）"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)

        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_alive = True
        self.logger = None

        # ✅ 防1053关键
        try:
            self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        except:
            pass

    # ================= 日志 =================

    def setup_logging(self):
        if self.logger:
            return

        log_dir = Path(os.environ.get('TEMP', 'C:\\Windows\\Temp')) / 'tplink_cleanup'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / 'cleanup_service.log'

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.FileHandler(log_file, encoding='utf-8')],
            force=True
        )

        self.logger = logging.getLogger(__name__)

    # ================= 服务运行 =================

    def SvcDoRun(self):
        try:
            # ✅ 关键：立即RUNNING
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)

            # 后台初始化（不会影响1053）
            self.setup_logging()

            if self.logger:
                self.logger.info("服务已启动，等待关机...")

            while self.is_alive:
                result = win32event.WaitForSingleObject(self.hWaitStop, 5000)
                if result == win32event.WAIT_OBJECT_0:
                    break

        except Exception as e:
            if self.logger:
                self.logger.error(f"运行错误: {e}")

    # ================= 停止 =================

    def SvcStop(self):
        try:
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        except:
            pass

        self.is_alive = False
        win32event.SetEvent(self.hWaitStop)

    # ================= 关机 =================

    def SvcShutdown(self):

        self.setup_logging()

        self.logger.info("=== 收到关机通知 ===")

        try:
            self.ReportServiceStatus(
                win32service.SERVICE_STOP_PENDING,
                waitHint=120000
            )
        except:
            pass

        try:
            self._perform_cleanup()
        except Exception as e:
            self.logger.error(f"清理失败: {e}")

        self.logger.info("清理完成")

        self.is_alive = False
        win32event.SetEvent(self.hWaitStop)

    # ================= 清理逻辑 =================

    def _perform_cleanup(self):
        try:
            # ✅ 延迟导入（关键）
            from config_manager import ConfigManager
            from tplink_http_cleaner import TPLinkHTTPCleaner

            config = ConfigManager().get_config()

            router_ip = config.get('router_ip', '192.168.1.1')
            password = config.get('router_password')

            if not password:
                self.logger.warning("未配置密码，跳过")
                return

            cleaner = TPLinkHTTPCleaner(router_ip, password)

            success = cleaner.run_cleanup()

            if success:
                self.logger.info("清理成功")
            else:
                self.logger.error("清理失败")

        except Exception as e:
            import traceback
            self.logger.error(traceback.format_exc())


# ================= 入口 =================

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(TPLinkCleanupServiceHTTP)
