#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TP-Link 路由器账号清理服务 - HTTP 版本
使用 HTTP 接口直接操作路由器，不使用浏览器
"""

import sys
import os
import time
import logging
import threading
from pathlib import Path

# Windows 服务相关
import win32service
import win32serviceutil
import win32event
import servicemanager

# 导入 HTTP 清理器
from tplink_http_cleaner import TPLinkHTTPCleaner

# 导入配置管理
from config_manager import ConfigManager


class TPLinkCleanupServiceHTTP(win32serviceutil.ServiceFramework):
    """TP-Link 路由器清理服务 - HTTP 版本"""

    _svc_name_ = "TPLinkShutdownCleanup"
    _svc_display_name_ = "TP-Link路由器账号清理服务"
    _svc_description_ = "在系统关机时自动清除TP-Link路由器中的宽带账号密码（HTTP接口版）"

    # 关机超时时间（3分钟）
    _svc_shutdown_timeout_ = 180000

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_alive = True
        self.logger = None
        self.cleaner = None

    def setup_logging(self):
        """设置日志"""
        log_dir = Path(os.environ.get('TEMP', '/tmp')) / 'tplink_cleanup'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / 'cleanup_service.log'

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
            ],
            force=True
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("=" * 60)
        self.logger.info("TP-Link路由器清理服务启动（HTTP版）")
        self.logger.info("=" * 60)

    def validate_config(self):
        """验证配置"""
        try:
            config_manager = ConfigManager()
            config = config_manager.get_config()

            self.logger.info(f"路由器IP: {config.get('router_ip')}")
            self.logger.info(f"路由器密码: {'已配置' if config.get('router_password') else '未配置'}")

            if not config.get('router_password'):
                self.logger.warning("警告：路由器管理密码未配置！")
                self.logger.warning("请使用主程序或服务安装器配置路由器信息。")
        except Exception as e:
            self.logger.error(f"配置验证失败: {e}")

    def SvcDoRun(self):
        """服务主循环"""
        try:
            # 设置日志
            self.setup_logging()

            # 验证配置
            self.validate_config()

            # 立即报告服务已启动
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            self.logger.info("[OK] 服务已就绪，等待关机事件...")

            # 主循环：等待关机或停止事件
            while self.is_alive:
                result = win32event.WaitForSingleObject(
                    self.hWaitStop,
                    5000  # 每5秒检查一次
                )

                if result == win32event.WAIT_OBJECT_0:
                    break

                # 定期记录心跳（每分钟）
                self.logger.debug("服务运行中...")

        except Exception as e:
            if self.logger:
                self.logger.error(f"服务运行出错: {e}")
            self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def SvcStop(self):
        """停止服务"""
        if self.logger:
            self.logger.info("收到停止服务请求...")

        try:
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        except:
            pass

        self.is_alive = False
        win32event.SetEvent(self.hWaitStop)

        if self.logger:
            self.logger.info("服务已停止")

    def SvcShutdown(self):
        """关机时的处理"""
        if not self.logger:
            # 如果日志还没设置，快速设置
            self.setup_logging()

        self.logger.info("=" * 60)
        self.logger.info("🚨 收到系统关机通知！")
        self.logger.info("=" * 60)

        try:
            # 报告服务正在停止（延长超时时间）
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING, waitHint=120000)
        except:
            pass

        # 执行清理
        try:
            self._perform_cleanup()
        except Exception as e:
            if self.logger:
                self.logger.error(f"清理失败: {e}")

        if self.logger:
            self.logger.info("关机清理完成，允许系统关机")

        self.is_alive = False
        win32event.SetEvent(self.hWaitStop)

    def _perform_cleanup(self):
        """执行路由器账号清理"""
        try:
            # 读取配置
            config_manager = ConfigManager()
            config = config_manager.get_config()

            router_ip = config.get('router_ip', '192.168.1.1')
            router_password = config.get('router_password', '')

            if not router_password:
                self.logger.warning("[WARN] 路由器密码未配置，跳过清理")
                return

            # 创建 HTTP 清理器
            cleaner = TPLinkHTTPCleaner(router_ip, router_password)

            # 执行清理
            success = cleaner.run_cleanup()

            if success:
                self.logger.info("[OK] 路由器账号清理完成")
            else:
                self.logger.error("[ERROR] 路由器账号清理失败")

        except Exception as e:
            self.logger.error(f"执行清理时出错: {e}")
            import traceback
            self.logger.error(traceback.format_exc())


# ==================== 服务安装函数 ====================

def install_service():
    """安装服务"""
    try:
        print("正在安装TP-Link路由器清理服务（HTTP版）...")

        # 检查是否已安装
        try:
            win32serviceutil.QueryServiceStatus(TPLinkCleanupServiceHTTP._svc_name_)
            print("服务已安装，正在卸载旧版本...")
            win32serviceutil.RemoveService(TPLinkCleanupServiceHTTP._svc_name_)
            time.sleep(2)
        except:
            pass

        # 安装服务（自动启动）
        win32serviceutil.InstallService(
            None,
            TPLinkCleanupServiceHTTP._svc_name_,
            TPLinkCleanupServiceHTTP._svc_display_name_,
            startType=win32service.SERVICE_AUTO_START,
            description=TPLinkCleanupServiceHTTP._svc_description_
        )

        print("[OK] 服务安装成功!")
        print(f"\n服务名称: {TPLinkCleanupServiceHTTP._svc_name_}")
        print(f"显示名称: {TPLinkCleanupServiceHTTP._svc_display_name_}")
        print("启动类型: 自动")
        print("功能: 关机时自动清除路由器账号密码")
        print("\n管理命令:")
        print(f"  启动服务: net start {TPLinkCleanupServiceHTTP._svc_name_}")
        print(f"  停止服务: net stop {TPLinkCleanupServiceHTTP._svc_name_}")
        print(f"  查看状态: sc query {TPLinkCleanupServiceHTTP._svc_name_}")
        print(f"\n日志位置: %TEMP%\\tplink_cleanup\\cleanup_service.log")

    except Exception as e:
        print(f"[ERROR] 服务安装失败: {e}")


def remove_service():
    """卸载服务"""
    try:
        print("正在卸载TP-Link路由器清理服务...")

        try:
            win32serviceutil.StopService(TPLinkCleanupServiceHTTP._svc_name_)
            print("服务已停止")
        except:
            print("（服务未运行）")

        win32serviceutil.RemoveService(TPLinkCleanupServiceHTTP._svc_name_)
        print("[OK] 服务已卸载")

    except Exception as e:
        print(f"[ERROR] 服务卸载失败: {e}")


# ==================== 命令行入口 ====================

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == 'install':
            install_service()
        elif command == 'remove':
            remove_service()
        elif command == 'start':
            win32serviceutil.StartService(TPLinkCleanupServiceHTTP._svc_name_)
            print("服务已启动")
        elif command == 'stop':
            win32serviceutil.StopService(TPLinkCleanupServiceHTTP._svc_name_)
            print("服务已停止")
        elif command == 'restart':
            win32serviceutil.RestartService(TPLinkCleanupServiceHTTP._svc_name_)
            print("服务已重启")
        elif command == 'status':
            try:
                status = win32serviceutil.QueryServiceStatus(TPLinkCleanupServiceHTTP._svc_name_)
                state = status[1]
                if state == win32service.SERVICE_RUNNING:
                    print("服务状态: 运行中")
                else:
                    print("服务状态: 已停止")
            except:
                print("服务未安装")
        else:
            print(f"未知命令: {command}")
            print("可用命令: install, remove, start, stop, restart, status")
    else:
        win32serviceutil.HandleCommandLine(TPLinkCleanupServiceHTTP)
