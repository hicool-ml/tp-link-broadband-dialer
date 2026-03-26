#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""简化的清理服务用于测试"""

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

class TestCleanupService(win32serviceutil.ServiceFramework):
    _svc_name_ = "TestCleanupService"
    _svc_display_name_ = "Test Cleanup Service"
    _svc_description_ = "Test cleanup service"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_alive = True
        self.logger = None

    def setup_logging(self):
        """设置日志"""
        log_dir = Path(os.environ.get('TEMP', '/tmp')) / 'test_cleanup'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / 'test_service.log'

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
            ],
            force=True
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("测试服务启动")

    def SvcDoRun(self):
        """服务主循环"""
        try:
            self.setup_logging()
            self.logger.info("服务开始运行...")

            # 尝试导入配置管理器
            try:
                sys.path.insert(0, 'D:/13jiao')
                from config_manager import ConfigManager
                config_mgr = ConfigManager()
                config = config_mgr.get_config()
                self.logger.info(f"配置加载成功: router_ip={config.get('router_ip')}")
            except Exception as e:
                self.logger.error(f"配置加载失败: {e}")

            # 报告服务已启动
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            self.logger.info("服务已就绪")

            # 主循环
            while self.is_alive:
                result = win32event.WaitForSingleObject(self.hWaitStop, 1000)
                if result == win32event.WAIT_OBJECT_0:
                    break

                # 每分钟记录一次心跳
                self.logger.info("服务运行中...")

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
    win32serviceutil.HandleCommandLine(TestCleanupService)
