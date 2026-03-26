#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TP-Link路由器账号清理服务 - 超简化版（v3）
"""

import sys
import os
import time
import logging
import re
from pathlib import Path

# 添加site-packages路径
site_packages = r"C:\Program Files\Python311\Lib\site-packages"
if site_packages not in sys.path:
    sys.path.insert(0, site_packages)

import win32service
import win32serviceutil
import win32event
import win32con
import servicemanager

# 导入Playwright
from playwright.sync_api import sync_playwright

# 尝试导入项目模块
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from config_manager import ConfigManager
from browser_manager import BrowserManager


# 禁用Playwright的自动更新
os.environ["PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD"] = "1"


class ShutdownCleanupService(win32serviceutil.ServiceFramework):
    """关机清理服务"""

    _svc_name_ = "TPLinkShutdownCleanup"
    _svc_display_name_ = "TP-Link路由器账号清理服务"
    _svc_description_ = "在系统关机时自动清除TP-Link路由器中的宽带账号密码"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_alive = True
        self.logger = None
        self.log_dir = Path(os.environ.get('TEMP', '/tmp')) / 'tplink_cleanup'

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
        self._setup_logging()
        self.logger.info("🚨 收到系统关机通知！")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING, waitHint=60000)
        self._perform_cleanup()
        self.is_alive = False
        win32event.SetEvent(self.hWaitStop)
        self.logger.info("关机清理完成")

    def SvcDoRun(self):
        """服务主循环"""
        # 立即报告运行状态
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)

        # 后台初始化
        self._setup_logging()
        self.logger.info("✅ 服务已启动")

        # 验证配置
        try:
            config_manager = ConfigManager()
            config = config_manager.get_config()
            self.logger.info(f"路由器IP: {config.get('router_ip')}")
        except Exception as e:
            self.logger.warning(f"配置验证失败: {e}")

        self.logger.info("服务就绪，等待关机事件...")

        # 主循环
        count = 0
        while self.is_alive:
            result = win32event.WaitForSingleObject(self.hWaitStop, 5000)
            if result == win32event.WAIT_OBJECT_0:
                break
            count += 1
            if count % 12 == 0:
                self.logger.info(f"服务运行中... ({count // 12}分钟)")

    def _setup_logging(self):
        """设置日志"""
        if self.logger:
            return

        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            log_file = self.log_dir / 'cleanup_service.log'
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[logging.FileHandler(log_file, encoding='utf-8', mode='a')],
                force=True
            )
        except:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[logging.StreamHandler()],
                force=True
            )
        self.logger = logging.getLogger(__name__)

    def _perform_cleanup(self):
        """执行清理"""
        try:
            self.logger.info("开始执行清理...")

            config_manager = ConfigManager()
            config = config_manager.get_config()
            router_ip = config.get('router_ip', '192.168.1.1')
            router_password = config.get('router_password', '')

            if not router_password:
                self.logger.warning("密码未配置，跳过清理")
                return

            # 这里执行实际的清理操作...
            self.logger.info("清理功能需要进一步实现")

        except Exception as e:
            self.logger.error(f"清理失败: {e}", exc_info=True)


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(ShutdownCleanupService)
