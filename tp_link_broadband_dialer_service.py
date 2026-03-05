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
- 独立于GUI，无需图形界面
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

# 导入主程序的核心功能
from tp_link_broadband_dialer import (
    get_resource_path,
    check_browser
)

# 导入Playwright
from playwright.sync_api import sync_playwright
import re


class TPLinkBroadbandDialer:
    """TP-Link宽带拨号器（无GUI版本）"""
    
    def __init__(self, router_ip="192.168.1.1", router_password="Cdu@123"):
        """初始化拨号器
        
        Args:
            router_ip: 路由器IP地址
            router_password: 路由器管理员密码
        """
        self.router_ip = router_ip
        self.router_password = router_password
        self.saved_account = ""
        self.saved_password = ""
        self.logger = logging.getLogger(__name__)
        
    def connect(self, account, password):
        """连接拨号
        
        Args:
            account: 宽带账号
            password: 宽带密码
            
        Returns:
            bool: 是否连接成功
        """
        try:
            self.logger.info("=" * 50)
            self.logger.info("开始连接流程...")
            self.logger.info(f"账号: {account}")
            self.logger.info(f"密码: {'*' * len(password)}")
            self.logger.info("=" * 50)
            
            # 保存账号密码
            self.saved_account = account
            self.saved_password = password
            
            # 用于存储捕获的 stok
            captured_stok = []
            
            def capture_stok(route, request):
                """捕获包含 stok 的请求"""
                url = request.url
                if "stok=" in url:
                    match = re.search(r"stok=([^/&?#]+)", url)
                    if match and not captured_stok:
                        stok_value = match.group(1)
                        captured_stok.append(stok_value)
                        self.logger.info(f"捕获到 stok: {stok_value}")
                route.continue_()
            
            with sync_playwright() as p:
                self.logger.info("正在启动浏览器...")
                
                # 获取内置浏览器路径
                executable_path = None
                try:
                    executable_path = check_browser()
                    self.logger.info(f"使用内置浏览器: {executable_path}")
                except RuntimeError as e:
                    self.logger.warning(f"{e}")
                    if not getattr(sys, 'frozen', False):
                        self.logger.info("开发环境：使用系统默认浏览器")
                    else:
                        raise
                
                # 启动浏览器
                launch_options = {
                    'headless': True,
                    'slow_mo': 300,
                    'args': [
                        "--no-sandbox",
                        "--disable-gpu",
                        "--disable-dev-shm-usage",
                        "--disable-extensions",
                        "--disable-plugins",
                        "--lang=zh-CN",
                        "--disable-web-security",
                        "--disable-features=VizDisplayCompositor",
                    ],
                    'handle_sigint': False,
                }
                
                if executable_path:
                    launch_options['executable_path'] = executable_path
                
                browser = p.chromium.launch(**launch_options)
                context = browser.new_context()
                page = context.new_page()
                
                # 设置路由来监听所有请求
                page.route("**/*", capture_stok)
                
                self.logger.info("正在访问路由器管理页面...")
                page.goto(f"http://{self.router_ip}/")
                
                # 登录
                page.wait_for_selector("input[type='password']", timeout=10000)
                page.fill("input[type='password']", self.router_password)
                page.keyboard.press("Enter")
                
                self.logger.info("正在验证登录...")
                
                # 等待捕获到 stok
                for i in range(15):
                    time.sleep(1)
                    if captured_stok:
                        break
                
                # 停止监听
                page.unroute("**/*", capture_stok)
                
                if not captured_stok:
                    self.logger.error("登录失败")
                    browser.close()
                    return False
                
                stok = captured_stok[0]
                self.logger.info("登录成功")
                
                # 等待页面加载
                time.sleep(3)
                
                # 导航到上网设置
                self.logger.info("正在进入路由设置...")
                try:
                    router_set_btn = page.wait_for_selector("#routerSetMbtn", timeout=5000)
                    if router_set_btn:
                        router_set_btn.click()
                        time.sleep(2)
                except:
                    pass
                
                try:
                    network_menu = page.wait_for_selector("#network_rsMenu", timeout=5000)
                    if network_menu:
                        network_menu.click()
                        time.sleep(2)
                except:
                    pass
                
                # 配置拨号方式
                self.logger.info("正在配置拨号方式...")
                try:
                    wan_sel = page.wait_for_selector("#wanSel .value", timeout=5000)
                    if wan_sel:
                        current_value = wan_sel.inner_text()
                        
                        if "宽带拨号上网" not in current_value and "PPPoE" not in current_value:
                            wan_sel_box = page.wait_for_selector("#wanSel", timeout=5000)
                            wan_sel_box.click()
                            time.sleep(1)
                            
                            pppoe_option_selectors = [
                                "#selOptsUlwanSel li:has-text('宽带拨号上网')",
                                "#selOptsUlwanSel li[title='宽带拨号上网']",
                                "li.option:has-text('宽带拨号上网')",
                            ]
                            
                            for selector in pppoe_option_selectors:
                                try:
                                    pppoe_option = page.wait_for_selector(selector, timeout=1000)
                                    if pppoe_option:
                                        pppoe_option.click()
                                        time.sleep(1)
                                        break
                                except:
                                    continue
                except Exception as e:
                    self.logger.warning(f"配置拨号方式时出错: {e}")
                
                # 填写账号密码
                self.logger.info("正在输入账号密码...")
                
                try:
                    page.wait_for_selector("#name", timeout=10000)
                    page.wait_for_selector("#psw", timeout=5000)
                except:
                    self.logger.error("无法找到账号密码输入框")
                    browser.close()
                    return False
                
                # 清空并填写账号
                page.fill("#name", "")
                page.fill("#name", account)
                
                # 清空并填写密码
                page.fill("#psw", "")
                page.fill("#psw", password)
                
                # 触发 blur 事件
                page.locator("#psw").blur()
                
                time.sleep(1)
                
                # 点击连接（最多尝试3次）
                max_attempts = 3
                connection_success = False
                
                for attempt in range(1, max_attempts + 1):
                    self.logger.info(f"正在进行第 {attempt}/{max_attempts} 次拨号...")
                    
                    # 点击连接按钮
                    try:
                        page.click("#save")
                        self.logger.info("已点击保存按钮")
                    except Exception as e:
                        self.logger.warning(f"点击#save失败: {e}")
                        try:
                            page.click("button:has-text('保存'), button:has-text('连接'), .save-btn")
                            self.logger.info("已点击备用按钮")
                        except Exception as e2:
                            self.logger.warning(f"点击备用按钮也失败: {e2}")
                    
                    self.logger.info("正在等待拨号完成（10秒）...")
                    time.sleep(10)
                    
                    # 检查连接状态
                    self.logger.info("正在检查连接状态...")
                    try:
                        time.sleep(3)
                        
                        # 获取IP地址
                        self.logger.info("正在获取WAN IP地址...")
                        ip_element = page.wait_for_selector("#wanIpLbl", timeout=5000)
                        if ip_element:
                            ip_address = ip_element.inner_text()
                            self.logger.info(f"获取到IP地址: {ip_address}")
                            
                            if ip_address and ip_address != "0.0.0.0" and ip_address != "0.0.0.0 ":
                                self.logger.info("=" * 50)
                                self.logger.info("拨号成功！")
                                self.logger.info(f"已获取IP地址: {ip_address}")
                                self.logger.info("=" * 50)
                                connection_success = True
                                break
                            else:
                                if attempt < max_attempts:
                                    self.logger.warning(f"拨号未成功（IP={ip_address}），准备重试...")
                                    time.sleep(2)
                                else:
                                    self.logger.warning("多次尝试后仍无法获取有效IP")
                        else:
                            if attempt < max_attempts:
                                self.logger.warning("无法获取IP地址元素，准备重试...")
                                time.sleep(2)
                    except Exception as e:
                        if attempt < max_attempts:
                            self.logger.warning(f"验证连接时出错，准备重试...")
                            time.sleep(2)
                
                browser.close()
                
                if connection_success:
                    return True
                else:
                    self.logger.error("拨号失败")
                    return False
                    
        except Exception as e:
            self.logger.error(f"连接时发生错误: {e}")
            return False
    
    def disconnect(self):
        """断开拨号并清除账号
        
        Returns:
            bool: 是否成功清除账号密码
        """
        disconnect_success = False
        try:
            self.logger.info("=" * 50)
            self.logger.info("开始断开流程...")
            self.logger.info("=" * 50)
            
            # 用于存储捕获的 stok
            captured_stok = []
            
            def capture_stok(route, request):
                """捕获包含 stok 的请求"""
                url = request.url
                if "stok=" in url:
                    match = re.search(r"stok=([^/&?#]+)", url)
                    if match and not captured_stok:
                        stok_value = match.group(1)
                        captured_stok.append(stok_value)
                        self.logger.info(f"捕获到 stok: {stok_value}")
                route.continue_()
            
            with sync_playwright() as p:
                self.logger.info("正在启动浏览器...")
                
                # 获取内置浏览器路径
                executable_path = None
                try:
                    executable_path = check_browser()
                    self.logger.info(f"使用内置浏览器: {executable_path}")
                except RuntimeError as e:
                    self.logger.warning(f"{e}")
                    if not getattr(sys, 'frozen', False):
                        self.logger.info("开发环境：使用系统默认浏览器")
                    else:
                        raise
                
                # 启动浏览器
                launch_options = {
                    'headless': True,
                    'slow_mo': 300,
                    'args': [
                        "--no-sandbox",
                        "--disable-gpu",
                        "--disable-dev-shm-usage",
                        "--disable-extensions",
                        "--disable-plugins",
                        "--lang=zh-CN",
                        "--disable-web-security",
                        "--disable-features=VizDisplayCompositor",
                    ],
                    'handle_sigint': False,
                }
                
                if executable_path:
                    launch_options['executable_path'] = executable_path
                
                browser = p.chromium.launch(**launch_options)
                context = browser.new_context()
                page = context.new_page()
                
                # 设置路由来监听所有请求
                page.route("**/*", capture_stok)
                
                self.logger.info("正在访问路由器管理页面...")
                page.goto(f"http://{self.router_ip}/")
                
                # 登录
                page.wait_for_selector("input[type='password']", timeout=10000)
                page.fill("input[type='password']", self.router_password)
                page.keyboard.press("Enter")
                
                self.logger.info("正在验证登录...")
                
                # 等待捕获到 stok
                for i in range(15):
                    time.sleep(1)
                    if captured_stok:
                        break
                
                # 停止监听
                page.unroute("**/*", capture_stok)
                
                if not captured_stok:
                    self.logger.error("登录失败")
                    browser.close()
                    return False
                
                stok = captured_stok[0]
                self.logger.info("登录成功")
                
                # 等待页面加载
                time.sleep(3)
                
                # 导航到上网设置
                self.logger.info("正在进入路由设置...")
                try:
                    router_set_btn = page.wait_for_selector("#routerSetMbtn", timeout=5000)
                    if router_set_btn:
                        router_set_btn.click()
                        time.sleep(2)
                except:
                    pass
                
                try:
                    network_menu = page.wait_for_selector("#network_rsMenu", timeout=5000)
                    if network_menu:
                        network_menu.click()
                        time.sleep(2)
                except:
                    pass
                
                # 断开连接
                self.logger.info("正在断开网络连接...")
                try:
                    disconnect_btn = page.wait_for_selector("#disconnect", timeout=5000)
                    if disconnect_btn:
                        disconnect_btn.click()
                        time.sleep(2)
                except:
                    self.logger.warning("未找到断开按钮")
                
                # 清除账号密码
                self.logger.info("正在清除账号密码...")
                try:
                    # 清空账号
                    self.logger.info("正在清空账号输入框...")
                    name_input = page.wait_for_selector("#name", timeout=5000)
                    if name_input:
                        name_input.fill("")
                        self.logger.info("账号输入框已清空")
                    
                    # 清空密码
                    self.logger.info("正在清空密码输入框...")
                    psw_input = page.wait_for_selector("#psw", timeout=5000)
                    if psw_input:
                        psw_input.fill("")
                        self.logger.info("密码输入框已清空")
                    
                    # 验证账号密码是否真的被清除了
                    self.logger.info("正在验证账号密码是否已清除...")
                    time.sleep(1)
                    name_value = name_input.input_value()
                    psw_value = psw_input.input_value()
                    self.logger.info(f"验证结果：账号=[{name_value}], 密码=[{psw_value}]")
                    
                    if not name_value and not psw_value:
                        self.logger.info("账号密码已清除")
                        disconnect_success = True
                    else:
                        self.logger.error(f"清除失败：账号=[{name_value}], 密码=[{psw_value}]")
                        disconnect_success = False
                except Exception as e:
                    self.logger.error(f"清除账号密码时出错: {e}")
                    disconnect_success = False
                
                # 保存（保存空账号密码）
                self.logger.info("正在保存配置...")
                try:
                    save_btn = page.wait_for_selector("#save", timeout=5000)
                    if save_btn:
                        save_btn.click()
                        time.sleep(2)
                except:
                    self.logger.warning("保存配置时出错")
                
                self.logger.info("=" * 50)
                if disconnect_success:
                    self.logger.info("断开并清除完成")
                else:
                    self.logger.error("清除验证失败")
                self.logger.info("=" * 50)
                
                time.sleep(2)
                browser.close()
                
        except Exception as e:
            self.logger.error(f"断开时发生错误: {e}")
            disconnect_success = False
        
        # 清除保存的账号密码
        self.saved_account = ""
        self.saved_password = ""
        
        # 返回是否成功清除
        return disconnect_success
    
    def stop(self):
        """停止拨号器"""
        self.logger.info("拨号器已停止")


class TPLinkDialerService(win32serviceutil.ServiceFramework):
    """TP-Link宽带拨号服务
    
    服务职责：
    - 在关机时自动断开拨号并清除账号信息
    - 不负责连接拨号（由GUI控制面板负责）
    - 不需要用户界面
    """

    _svc_name_ = "TPLinkBroadbandDialer"
    _svc_display_name_ = "TP-Link宽带拨号服务"
    _svc_description_ = "在关机前自动断开TP-Link路由器拨号并清除账号信息"

    def __init__(self, args):
        """初始化服务"""
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_alive = True
        self.dialer = None
        
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
        """执行关机前的清理操作
        
        功能：只要关机就删除路由器内的账号密码
        """
        try:
            self.logger.info("=" * 60)
            self.logger.info("开始执行关机清理操作...")
            self.logger.info("=" * 60)
            
            # 创建拨号器实例（如果还没有）
            if not self.dialer:
                self.logger.info("初始化拨号器...")
                self.dialer = TPLinkBroadbandDialer()
            
            # 执行断开和清除操作
            self.logger.info("正在断开拨号并清除账号...")
            success = self.dialer.disconnect()
            
            if success:
                self.logger.info("✓ 账号密码已成功清除")
            else:
                self.logger.warning("✗ 账号密码清除失败")
            
            self.logger.info("=" * 60)
            self.logger.info("关机清理操作完成")
            self.logger.info("=" * 60)
                
        except Exception as e:
            self.logger.error(f"执行关机清理时出错: {e}", exc_info=True)
            
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
            
            # 进入主循环
            self.logger.info("进入服务主循环...")
            self.logger.info("服务已就绪，等待关机事件...")
            
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
                # 例如：检查连接状态、记录日志等
                
        except Exception as e:
            self.logger.error(f"服务运行时出错: {e}", exc_info=True)
            self.ReportServiceStatus(win32service.SERVICE_STOPPED)


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
