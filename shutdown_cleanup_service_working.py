#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试完整的清理服务（逐步添加功能）"""

import sys
import os
import logging
from pathlib import Path

# 添加site-packages路径
site_packages = r"C:\Program Files\Python311\Lib\site-packages"
if site_packages not in sys.path:
    sys.path.insert(0, site_packages)

import win32service
import win32serviceutil
import win32event
import servicemanager

# 尝试导入项目模块
sys.path.insert(0, 'D:/13jiao')

class ShutdownCleanupService(win32serviceutil.ServiceFramework):
    _svc_name_ = "TPLinkShutdownCleanup"
    _svc_display_name_ = "TP-Link路由器账号清理服务"
    _svc_description_ = "在系统关机时自动清除TP-Link路由器中的宽带账号密码"
    _svc_shutdown_timeout_ = 180000  # 3分钟

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_alive = True
        self.logger = None
        self.cleaner = None

    def setup_logging(self):
        """设置日志"""
        log_dir = Path(r"C:\Program Files\TPLinkDialer\logs")
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
        except:
            log_dir = Path(os.environ.get('TEMP', '/tmp')) / 'full_test'
            log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / 'full_test_service.log'

        try:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_file, encoding='utf-8', mode='a'),
                ],
                force=True
            )
        except:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.StreamHandler(),
                ],
                force=True
            )

        self.logger = logging.getLogger(__name__)
        self.logger.info("=" * 60)
        self.logger.info("完整测试服务启动")
        self.logger.info(f"日志文件: {log_file}")
        self.logger.info("=" * 60)

    def SvcDoRun(self):
        """服务主循环"""
        try:
            self.setup_logging()
            self.logger.info("服务开始运行...")

            # 测试1: 导入config_manager
            try:
                from config_manager import ConfigManager
                config_mgr = ConfigManager()
                config = config_mgr.get_config()
                self.logger.info(f"✓ ConfigManager加载成功: {config.get('router_ip')}")
            except Exception as e:
                self.logger.error(f"✗ ConfigManager加载失败: {e}")

            # 测试2: 导入browser_manager
            try:
                from browser_manager import BrowserManager
                self.logger.info("✓ BrowserManager导入成功")
            except Exception as e:
                self.logger.error(f"✗ BrowserManager导入失败: {e}")

            # 测试3: 导入playwright
            try:
                from playwright.sync_api import sync_playwright
                self.logger.info("✓ Playwright导入成功")
            except Exception as e:
                self.logger.error(f"✗ Playwright导入失败: {e}")

            # 测试4: 创建RouterAccountCleaner
            try:
                from shutdown_cleanup_service import RouterAccountCleaner
                self.logger.info("正在创建RouterAccountCleaner...")
                self.cleaner = RouterAccountCleaner()
                self.logger.info("✓ RouterAccountCleaner创建成功")
            except Exception as e:
                self.logger.error(f"✗ RouterAccountCleaner创建失败: {e}")

            # 报告服务已启动
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            self.logger.info("服务已就绪")

            # 主循环
            count = 0
            while self.is_alive:
                result = win32event.WaitForSingleObject(self.hWaitStop, 5000)
                if result == win32event.WAIT_OBJECT_0:
                    break

                count += 1
                if count % 12 == 0:  # 每分钟
                    self.logger.info(f"服务运行中... ({count // 12}分钟)")

        except Exception as e:
            if self.logger:
                self.logger.error(f"服务运行时出错: {e}", exc_info=True)
            self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def SvcStop(self):
        """停止服务"""
        if self.logger:
            self.logger.info("收到停止服务请求...")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.is_alive = False
        win32event.SetEvent(self.hWaitStop)
        if self.logger:
            self.logger.info("服务已停止")
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(FullTestService)
