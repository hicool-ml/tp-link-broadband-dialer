#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TP-Link路由器账号清理服务 - 修复版本
关键修复：
1. 删除site-packages注入
2. 极简启动路径
3. 所有重操作放线程
4. 所有import延迟
"""

import sys
import os
import time
import logging
import re
import threading
import subprocess
from pathlib import Path

# ✅ 修复1：删除site-packages注入
# 不再注入site-packages，PyInstaller已经打包了所有依赖

# 只导入核心Windows服务模块（最小化）
import win32service
import win32serviceutil
import win32event
import servicemanager


class ShutdownCleanupService(win32serviceutil.ServiceFramework):
    """关机清理服务 - 极简启动版本"""

    _svc_name_ = "TPLinkShutdownCleanup"
    _svc_display_name_ = "TP-Link路由器账号清理服务"
    _svc_description_ = "在系统关机时自动清除TP-Link路由器中的宽带账号密码"

    def __init__(self, args):
        # ✅ 修复2：最小化初始化
        win32serviceutil.ServiceFramework.__init__(self, args)

        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_alive = True
        self.initialized = False

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
            # 报告服务正在停止
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING, waitHint=120000)

            # ✅ 修复3：使用线程执行清理，不阻塞主线程
            cleanup_thread = threading.Thread(target=self._perform_cleanup, daemon=True)
            cleanup_thread.start()
            cleanup_thread.join(timeout=110)  # 等待最多110秒

        except Exception as e:
            # 即使出错也继续
            pass

        self.is_alive = False
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        """✅ 修复4：极简启动路径"""
        try:
            # ⭐ 第一时间告诉系统：我活着（避免1053）
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)

            # 记录启动日志（如果可能）
            try:
                servicemanager.LogInfoMsg("Service started successfully")
            except:
                pass

            # ⭐ 延迟初始化（放到线程里）
            if not self.initialized:
                init_thread = threading.Thread(target=self._initialize_background, daemon=True)
                init_thread.start()

            # 主循环：只负责"活着"
            while self.is_alive:
                try:
                    result = win32event.WaitForSingleObject(self.hWaitStop, 5000)
                    if result == win32event.WAIT_OBJECT_0:
                        break
                except:
                    time.sleep(5)

        except Exception as e:
            try:
                servicemanager.LogErrorMsg(f"Service error: {str(e)}")
            except:
                pass
            self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def _initialize_background(self):
        """后台初始化（不阻塞主线程）"""
        try:
            # 延迟设置日志
            log_dir = Path(os.environ.get('TEMP', '/tmp')) / 'tplink_cleanup'
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / 'cleanup_service.log'

            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_file, encoding='utf-8', mode='a'),
                ],
                force=True
            )

            logger = logging.getLogger(__name__)
            logger.info("=" * 60)
            logger.info("✅ 服务已启动")
            logger.info("=" * 60)

            # ✅ 修复5：使用importlib延迟导入，避免阻塞
            try:
                import importlib

                # 获取当前目录
                current_dir = Path(__file__).parent
                if str(current_dir) not in sys.path:
                    sys.path.insert(0, str(current_dir))

                # 延迟导入模块
                config_module = importlib.import_module("config_manager")
                ConfigManager = config_module.ConfigManager

                # 验证配置
                config_mgr = ConfigManager()
                config = config_mgr.get_config()
                logger.info(f"路由器IP: {config.get('router_ip')}")
                logger.info(f"路由器密码: {'已配置' if config.get('router_password') else '未配置'}")

            except Exception as e:
                logger.warning(f"初始化警告: {e}")

            self.initialized = True

        except Exception as e:
            # 初始化失败不影响服务运行
            pass

    def _perform_cleanup(self):
        """执行清理（在线程中运行）"""
        try:
            # 设置日志
            log_dir = Path(os.environ.get('TEMP', '/tmp')) / 'tplink_cleanup'
            log_file = log_dir / 'cleanup_service.log'

            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_file, encoding='utf-8', mode='a'),
                ],
                force=True
            )

            logger = logging.getLogger(__name__)
            logger.info("=" * 60)
            logger.info("🚨 开始执行关机清理")
            logger.info("=" * 60)

            # ✅ 修复6：使用独立进程执行清理，避免阻塞服务
            current_dir = Path(__file__).parent
            cleanup_script = current_dir / "cleanup_worker.py"

            if cleanup_script.exists():
                # 使用独立Python进程执行清理
                result = subprocess.run(
                    [sys.executable, str(cleanup_script)],
                    capture_output=True,
                    text=True,
                    timeout=100,
                    cwd=str(current_dir)
                )

                if result.stdout:
                    logger.info(result.stdout)
                if result.stderr:
                    logger.error(result.stderr)
            else:
                logger.error(f"找不到清理脚本: {cleanup_script}")

            logger.info("✅ 关机清理完成")

        except Exception as e:
            # 清理失败也要继续关机
            try:
                logger = logging.getLogger(__name__)
                logger.error(f"清理失败: {e}")
            except:
                pass


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(ShutdownCleanupService)
