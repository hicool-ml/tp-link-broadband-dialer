#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TP-Link路由器宽带拨号工具 - Windows服务版本

作为系统服务运行，可以在关机时更可靠地拦截关机事件并执行断开拨号操作。

特性：
- 作为Windows服务运行，关机优先级高
- 接受SERVICE_CONTROL_SHUTDOWN控制码
- 关机超时时间最长可达3分钟（默认30秒）
- 自动启动，无需用户登录
- 保留GUI控制面板用于配置和监控
"""

import os
import sys
import time
import logging
import threading
import subprocess
from pathlib import Path
import win32service
import win32serviceutil
import win32event
import win32con
import servicemanager
import win32api
import win32gui
import win32process

# 导入主程序的核心功能
from tp_link_broadband_dialer import (
    get_resource_path,
    check_browser,
    TPLinkBroadbandDialer
)


class TPLinkDialerService(win32serviceutil.ServiceFramework):
    """TP-Link宽带拨号服务"""

    _svc_name_ = "TPLinkBroadbandDialer"
    _svc_display_name_ = "TP-Link宽带拨号服务"
    _svc_description_ = "在关机前自动断开TP-Link路由器拨号并清除账号信息"

    def __init__(self, args):
        """初始化服务"""
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_alive = True
        self.dialer = None
        self.control_panel = None
        self.control_panel_process = None
        
        # 设置日志
        self.setup_logging()
        
    def setup_logging(self):
        """设置日志"""
        log_dir = Path(os.environ.get('TEMP', '/tmp')) / 'tplink_dialer'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / 'service.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("=" * 60)
        self.logger.info("TP-Link宽带拨号服务启动")
        self.logger.info("=" * 60)
        
    def SvcStop(self):
        """停止服务"""
        self.logger.info("收到停止服务请求...")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        
        # 设置停止标志
        self.is_alive = False
        win32event.SetEvent(self.hWaitStop)
        
        # 停止拨号器
        if self.dialer:
            try:
                self.logger.info("正在停止拨号器...")
                self.dialer.stop()
            except Exception as e:
                self.logger.error(f"停止拨号器时出错: {e}")
        
        # 关闭控制面板
        if self.control_panel_process:
            try:
                self.logger.info("正在关闭控制面板...")
                self.control_panel_process.terminate()
                self.control_panel_process.wait(timeout=5)
            except Exception as e:
                self.logger.error(f"关闭控制面板时出错: {e}")
        
        self.logger.info("服务已停止")
        
    def SvcShutdown(self):
        """关机时的处理"""
        self.logger.info("=" * 60)
        self.logger.info("收到系统关机通知！")
        self.logger.info("=" * 60)
        
        # 报告服务正在停止
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        
        # 执行关机前的清理操作
        self.perform_shutdown_cleanup()
        
        # 设置停止标志
        self.is_alive = False
        win32event.SetEvent(self.hWaitStop)
        
        self.logger.info("关机清理完成，允许系统关机")
        
    def perform_shutdown_cleanup(self):
        """执行关机前的清理操作"""
        try:
            # 如果有拨号器实例，使用它来断开和清除
            if self.dialer and hasattr(self.dialer, 'router'):
                self.logger.info("使用拨号器实例执行关机前清理...")
                
                # 断开拨号
                if hasattr(self.dialer, 'disconnect_dialer'):
                    self.logger.info("正在断开拨号...")
                    try:
                        success = self.dialer.disconnect_dialer()
                        if success:
                            self.logger.info("✓ 拨号已断开")
                        else:
                            self.logger.warning("✗ 拨号断开失败")
                    except Exception as e:
                        self.logger.error(f"断开拨号时出错: {e}")
                
                # 清除账号
                if hasattr(self.dialer, 'clear_account'):
                    self.logger.info("正在清除账号信息...")
                    try:
                        success = self.dialer.clear_account()
                        if success:
                            self.logger.info("✓ 账号信息已清除")
                        else:
                            self.logger.warning("✗ 账号清除失败")
                    except Exception as e:
                        self.logger.error(f"清除账号时出错: {e}")
            else:
                self.logger.warning("拨号器实例不可用，无法执行清理操作")
                
        except Exception as e:
            self.logger.error(f"执行关机清理时出错: {e}")
            
    def SvcDoRun(self):
        """服务主循环"""
        self.logger.info("服务开始运行...")
        
        # 报告服务正在运行
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        
        try:
            # 初始化拨号器
            self.logger.info("正在初始化拨号器...")
            self.dialer = TPLinkBroadbandDialer()
            self.logger.info("拨号器初始化完成")
            
            # 启动控制面板（可选）
            self.start_control_panel()
            
            # 进入主循环
            self.logger.info("进入服务主循环...")
            while self.is_alive:
                # 等待停止信号，每秒检查一次
                result = win32event.WaitForSingleObject(
                    self.hWaitStop, 
                    1000  # 1秒超时
                )
                
                if result == win32event.WAIT_OBJECT_0:
                    # 收到停止信号
                    break
                    
                # 在这里可以添加定期任务
                # 例如：检查连接状态、自动重连等
                
        except Exception as e:
            self.logger.error(f"服务运行时出错: {e}", exc_info=True)
            self.ReportServiceStatus(win32service.SERVICE_STOPPED)
            
    def start_control_panel(self):
        """启动GUI控制面板"""
        try:
            self.logger.info("正在启动控制面板...")
            
            # 获取当前Python解释器路径
            python_exe = sys.executable
            
            # 获取主程序脚本路径
            if getattr(sys, 'frozen', False):
                # 打包后的EXE
                script_path = os.path.join(
                    os.path.dirname(sys.executable),
                    'tp_link_broadband_dialer.exe'
                )
            else:
                # 开发环境
                script_path = os.path.join(
                    os.path.dirname(__file__),
                    'tp_link_broadband_dialer.py'
                )
            
            # 启动控制面板进程
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = win32con.SW_SHOW
            
            self.control_panel_process = subprocess.Popen(
                [script_path],
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            
            self.logger.info(f"控制面板已启动 (PID: {self.control_panel_process.pid})")
            
        except Exception as e:
            self.logger.error(f"启动控制面板时出错: {e}")


def install_service():
    """安装服务"""
    try:
        print("正在安装TP-Link宽带拨号服务...")
        
        # 设置服务参数
        service_args = [
            'install',
            '--startup', 'auto',  # 自动启动
            '--username', None,    # 使用本地系统账户
            '--password', None,
            '--description', '在关机前自动断开TP-Link路由器拨号并清除账号信息'
        ]
        
        # 安装服务
        win32serviceutil.HandleCommandLine(
            TPLinkDialerService,
            service_args
        )
        
        print("✓ 服务安装成功！")
        print("\n服务名称: TPLinkBroadbandDialer")
        print("显示名称: TP-Link宽带拨号服务")
        print("启动类型: 自动")
        print("\n使用以下命令管理服务:")
        print("  启动服务: net start TPLinkBroadbandDialer")
        print("  停止服务: net stop TPLinkBroadbandDialer")
        print("  卸载服务: python tp_link_broadband_dialer_service.py remove")
        
    except Exception as e:
        print(f"✗ 服务安装失败: {e}")
        import traceback
        traceback.print_exc()


def remove_service():
    """卸载服务"""
    try:
        print("正在卸载TP-Link宽带拨号服务...")
        
        # 先停止服务
        try:
            win32serviceutil.StopService(TPLinkDialerService._svc_name_)
            print("✓ 服务已停止")
        except:
            print("（服务未运行）")
        
        # 移除服务
        win32serviceutil.RemoveService(TPLinkDialerService._svc_name_)
        print("✓ 服务已卸载")
        
    except Exception as e:
        print(f"✗ 服务卸载失败: {e}")
        import traceback
        traceback.print_exc()


def start_service():
    """启动服务"""
    try:
        print("正在启动TP-Link宽带拨号服务...")
        win32serviceutil.StartService(TPLinkDialerService._svc_name_)
        print("✓ 服务已启动")
        print("\n服务正在后台运行，可以通过控制面板进行配置和监控")
    except Exception as e:
        print(f"✗ 服务启动失败: {e}")
        import traceback
        traceback.print_exc()


def stop_service():
    """停止服务"""
    try:
        print("正在停止TP-Link宽带拨号服务...")
        win32serviceutil.StopService(TPLinkDialerService._svc_name_)
        print("✓ 服务已停止")
    except Exception as e:
        print(f"✗ 服务停止失败: {e}")
        import traceback
        traceback.print_exc()


def show_status():
    """显示服务状态"""
    try:
        status = win32serviceutil.QueryServiceStatus(TPLinkDialerService._svc_name_)
        
        state_map = {
            win32service.SERVICE_STOPPED: "已停止",
            win32service.SERVICE_START_PENDING: "正在启动",
            win32service.SERVICE_STOP_PENDING: "正在停止",
            win32service.SERVICE_RUNNING: "正在运行",
            win32service.SERVICE_CONTINUE_PENDING: "正在继续",
            win32service.SERVICE_PAUSE_PENDING: "正在暂停",
            win32service.SERVICE_PAUSED: "已暂停",
        }
        
        state = state_map.get(status[1], "未知状态")
        print(f"服务状态: {state}")
        
        if status[1] == win32service.SERVICE_RUNNING:
            print("✓ 服务正在运行")
        elif status[1] == win32service.SERVICE_STOPPED:
            print("× 服务已停止")
            
    except Exception as e:
        print(f"无法查询服务状态: {e}")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'install':
            install_service()
        elif command == 'remove' or command == 'uninstall':
            remove_service()
        elif command == 'start':
            start_service()
        elif command == 'stop':
            stop_service()
        elif command == 'status':
            show_status()
        elif command == 'restart':
            stop_service()
            time.sleep(2)
            start_service()
        else:
            print("TP-Link宽带拨号服务管理工具")
            print("\n用法:")
            print("  python tp_link_broadband_dialer_service.py install   - 安装服务")
            print("  python tp_link_broadband_dialer_service.py remove    - 卸载服务")
            print("  python tp_link_broadband_dialer_service.py start     - 启动服务")
            print("  python tp_link_broadband_dialer_service.py stop      - 停止服务")
            print("  python tp_link_broadband_dialer_service.py restart   - 重启服务")
            print("  python tp_link_broadband_dialer_service.py status    - 查看状态")
    else:
        # 作为服务运行（由服务管理器调用）
        win32serviceutil.HandleCommandLine(TPLinkDialerService)
