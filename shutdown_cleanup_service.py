#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TP-Link路由器账号清理服务

作为Windows后台服务运行，在系统关机时自动断开路由器拨号并清除账号密码。
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


def get_resource_path(relative_path):
    """获取PyInstaller打包后的内置资源路径"""
    if hasattr(sys, '_MEIPASS'):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent
    return str(base_path / relative_path)


# 禁用Playwright的自动更新
os.environ["PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD"] = "1"

# 创建浏览器管理器
browser_manager = BrowserManager()


def check_browser():
    """验证浏览器是否存在并返回路径"""
    try:
        browser_path = browser_manager.get_browser_path()
        if browser_path:
            return browser_path
    except Exception:
        pass
    raise RuntimeError("浏览器未安装！请运行程序安装向导安装浏览器。")


class RouterAccountCleaner:
    """路由器账号清理器"""

    def __init__(self):
        # 从配置文件读取路由器信息
        config_manager = ConfigManager()
        config = config_manager.get_config()

        # 获取路由器配置
        self.router_ip = config.get('router_ip', '')
        self.router_password = config.get('router_password', '')

        # 如果没有配置 IP，使用默认值
        if not self.router_ip:
            self.router_ip = '192.168.1.1'

        self.logger = logging.getLogger(__name__)
        self.logger.info(f"路由器地址: {self.router_ip}")

        if not self.router_password:
            self.logger.warning("路由器管理密码未配置，清理功能可能无法工作")

    def clear_account(self):
        """清除路由器账号密码

        返回: bool - 是否成功清除
        """
        try:
            self.logger.info("=" * 60)
            self.logger.info("开始执行清理流程")
            self.logger.info("=" * 60)

            # 执行清理
            return self._perform_cleanup()

        except Exception as e:
            self.logger.error(f"清理流程发生错误: {e}", exc_info=True)
            return False

    def _perform_cleanup(self):
        """执行实际的清理操作"""
        try:
            captured_stok = []

            def capture_stok(route, request):
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
                page.route("**/*", capture_stok)

                self.logger.info("正在访问路由器管理页面...")
                page.goto(f"http://{self.router_ip}/", timeout=30000)

                page.wait_for_selector("input[type='password']", timeout=10000)
                page.fill("input[type='password']", self.router_password)
                page.keyboard.press("Enter")

                self.logger.info("正在验证登录...")

                for i in range(15):
                    time.sleep(1)
                    if captured_stok:
                        break

                page.unroute("**/*", capture_stok)

                if not captured_stok:
                    self.logger.error("登录失败")
                    browser.close()
                    return False

                self.logger.info("登录成功")
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
                        self.logger.info("已断开网络连接")
                except:
                    self.logger.warning("未找到断开按钮或断开失败")

                # 清除账号密码
                self.logger.info("正在清除账号密码...")
                success = False

                try:
                    name_input = page.wait_for_selector("#name", timeout=5000)
                    psw_input = page.wait_for_selector("#psw", timeout=5000)

                    if name_input and psw_input:
                        name_input.fill("")
                        psw_input.fill("")

                        time.sleep(1)
                        name_value = name_input.input_value()
                        psw_value = psw_input.input_value()

                        self.logger.info(f"验证结果：账号=[{name_value}], 密码=[{psw_value}]")

                        if not name_value and not psw_value:
                            self.logger.info("账号密码已清除")
                            success = True
                        else:
                            self.logger.error(f"清除失败：账号=[{name_value}], 密码=[{psw_value}]")
                except Exception as e:
                    self.logger.error(f"清除账号密码时出错: {e}")

                # 保存配置
                self.logger.info("正在保存配置...")
                try:
                    save_btn = page.wait_for_selector("#save", timeout=5000)
                    if save_btn:
                        save_btn.click()
                        time.sleep(2)
                        self.logger.info("配置已保存")
                except:
                    self.logger.warning("保存配置时出错")

                self.logger.info("=" * 60)
                if success:
                    self.logger.info("账号密码清除成功")
                else:
                    self.logger.error("账号密码清除失败")
                self.logger.info("=" * 60)

                time.sleep(2)
                browser.close()
                return success

        except Exception as e:
            self.logger.error(f"清除账号时发生错误: {e}", exc_info=True)
            return False


class ShutdownCleanupService(win32serviceutil.ServiceFramework):
    """关机清理服务

    职责：在系统关机时自动清除路由器中的账号密码
    """

    _svc_name_ = "TPLinkShutdownCleanup"
    _svc_display_name_ = "TP-Link路由器账号清理服务"
    _svc_description_ = "在系统关机时自动清除TP-Link路由器中的宽带账号密码"

    # 设置更长的关机超时时间（3分钟 = 180000 毫秒）
    _svc_shutdown_timeout_ = 180000

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_alive = True
        self.cleaner = None
        self.logger = None

        # 设置更长的关机超时
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)

        self.setup_logging()

        # 验证配置
        self.validate_config()

    def setup_logging(self):
        """设置日志"""
        log_dir = Path(r"C:\Program Files\TPLinkDialer\logs")
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
        except:
            log_dir = Path(os.environ.get('TEMP', '/tmp')) / 'tplink_cleanup'
            log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / 'cleanup_service.log'

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
        self.logger.info("TP-Link路由器账号清理服务启动")
        self.logger.info(f"日志文件: {log_file}")
        self.logger.info("=" * 60)

    def validate_config(self):
        """验证配置是否正确"""
        try:
            config_manager = ConfigManager()
            config = config_manager.get_config()

            self.logger.info(f"配置信息:")
            self.logger.info(f"  路由器IP: {config.get('router_ip')}")
            self.logger.info(f"  路由器密码: {'已设置' if config.get('router_password') else '未设置'}")

            if not config.get('router_password'):
                self.logger.warning("警告：路由器管理密码未配置，清理功能可能无法工作！")
                self.logger.warning("请使用主程序或服务安装器配置路由器信息。")
        except Exception as e:
            self.logger.error(f"验证配置时出错: {e}")

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

    def SvcShutdown(self):
        """关机时的处理"""
        if not self.logger:
            self.setup_logging()

        self.logger.info("=" * 60)
        self.logger.info("收到系统关机通知！")
        self.logger.info("=" * 60)

        # 报告服务正在停止（延长超时时间）
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING, waitHint=30000)

        # 执行关机清理
        self.perform_shutdown_cleanup()

        self.is_alive = False
        win32event.SetEvent(self.hWaitStop)

        self.logger.info("关机清理完成，允许系统关机")

    def perform_shutdown_cleanup(self):
        """执行关机前的清理操作"""
        try:
            self.logger.info("开始执行关机清理...")

            if not self.cleaner:
                self.cleaner = RouterAccountCleaner()

            success = self.cleaner.clear_account()

            if success:
                self.logger.info("账号密码已成功清除")
            else:
                self.logger.warning("账号密码清除失败")

            self.logger.info("关机清理操作完成")

        except Exception as e:
            self.logger.error(f"执行关机清理时出错: {e}", exc_info=True)

    def SvcDoRun(self):
        """服务主循环"""
        try:
            self.setup_logging()
            self.logger.info("服务开始运行...")

            # 初始化清理器（提前验证配置）
            self.logger.info("正在初始化清理器...")
            try:
                self.cleaner = RouterAccountCleaner()
                self.logger.info("清理器初始化完成")
            except Exception as e:
                self.logger.error(f"清理器初始化失败: {e}")
                self.logger.warning("服务将继续运行，但清理功能可能无法正常工作")

            # 报告服务已启动
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            self.logger.info("服务已就绪，等待关机事件...")

            # 主循环：等待关机或停止事件
            count = 0
            while self.is_alive:
                result = win32event.WaitForSingleObject(self.hWaitStop, 5000)

                if result == win32event.WAIT_OBJECT_0:
                    break

                count += 1
                # 定期记录心跳（每分钟）
                if count % 12 == 0:
                    self.logger.info(f"服务运行中... ({count // 12}分钟)")

        except Exception as e:
            if self.logger:
                self.logger.error(f"服务运行时出错: {e}", exc_info=True)
            self.ReportServiceStatus(win32service.SERVICE_STOPPED)


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(ShutdownCleanupService)
