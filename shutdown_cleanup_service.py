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
    raise RuntimeError("浏览器未安装！")


class RouterAccountCleaner:
    """路由器账号清理器"""

    def __init__(self):
        config_manager = ConfigManager()
        config = config_manager.get_config()
        self.router_ip = config.get('router_ip', '192.168.1.1')
        self.router_password = config.get('router_password', '')
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"路由器地址: {self.router_ip}")

    def clear_account(self):
        """清除路由器账号密码"""
        try:
            self.logger.info("=" * 60)
            self.logger.info("开始执行清理流程")
            self.logger.info("=" * 60)
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
                        self.logger.info(f"✅ 捕获到 stok: {stok_value}")
                route.continue_()

            with sync_playwright() as p:
                self.logger.info("🌐 启动浏览器（无头模式）...")

                executable_path = None
                try:
                    executable_path = check_browser()
                    self.logger.info(f"✅ 使用浏览器: {executable_path}")
                except RuntimeError as e:
                    self.logger.warning(f"⚠️ {e}")
                    if not getattr(sys, 'frozen', False):
                        self.logger.info("⚠️ 开发环境：使用系统浏览器")
                    else:
                        raise

                launch_options = {
                    'headless': True,
                    'slow_mo': 300,
                    'args': ["--no-sandbox", "--disable-gpu", "--disable-web-security", "--lang=zh-CN"],
                    'handle_sigint': False,
                }

                if executable_path:
                    launch_options['executable_path'] = executable_path

                browser = p.chromium.launch(**launch_options)
                context = browser.new_context()
                page = context.new_page()
                page.route("**/*", capture_stok)

                # 登录
                self.logger.info("🔌 访问路由器...")
                page.goto(f"http://{self.router_ip}/", timeout=30000)
                self.logger.info("🔑 等待密码框...")
                page.wait_for_selector("input[type='password']", timeout=10000)
                page.fill("input[type='password']", self.router_password)
                page.keyboard.press("Enter")

                self.logger.info("⏳ 等待token...")
                for i in range(15):
                    time.sleep(1)
                    if captured_stok:
                        break

                page.unroute("**/*", capture_stok)

                if not captured_stok:
                    self.logger.error("❌ 登录失败")
                    browser.close()
                    return False

                self.logger.info("✅ 登录成功")

                # 导航到上网设置
                self.logger.info("🚀 导航到上网设置...")
                page.goto(f"http://{self.router_ip}/")
                time.sleep(2)

                try:
                    router_set_btn = page.wait_for_selector("#routerSetMbtn", timeout=3000)
                    if router_set_btn:
                        router_set_btn.click()
                        time.sleep(2)
                except:
                    pass

                try:
                    network_menu = page.wait_for_selector("#network_rsMenu", timeout=3000)
                    if network_menu:
                        network_menu.click()
                        time.sleep(2)
                except:
                    pass

                menu_clicked = False
                for selector in ["#network_rsMenu", "li#network_rsMenu", "li.menuLi"]:
                    try:
                        menu_item = page.wait_for_selector(selector, timeout=2000)
                        if menu_item:
                            menu_item.click()
                            menu_clicked = True
                            time.sleep(2)
                            break
                    except:
                        continue

                if not menu_clicked:
                    self.logger.error("❌ 无法打开上网设置")
                    browser.close()
                    return False

                # 断开连接
                self.logger.info("🔌 断开连接...")
                try:
                    disconnect_btn = page.wait_for_selector("#disconnect", timeout=5000)
                    if disconnect_btn:
                        disconnect_btn.click()
                        time.sleep(2)
                        self.logger.info("✅ 已断开")
                except:
                    self.logger.warning("断开按钮不存在")

                # 清除账号密码
                self.logger.info("🗑️ 清除账号密码...")
                success = False

                try:
                    name_input = page.wait_for_selector("#name", timeout=5000)
                    psw_input = page.wait_for_selector("#psw", timeout=5000)

                    if name_input:
                        name_input.fill("")
                        self.logger.info("   ✅ 账号已清空")

                    if psw_input:
                        psw_input.fill("")
                        self.logger.info("   ✅ 密码已清空")

                    time.sleep(1)
                    name_value = name_input.input_value() if name_input else ""
                    psw_value = psw_input.input_value() if psw_input else ""
                    self.logger.info(f"   📋 验证: 账号=[{name_value}], 密码=[{psw_value}]")

                    if not name_value and not psw_value:
                        self.logger.info("✅ 账号密码已清除")
                        success = True
                except Exception as e:
                    self.logger.error(f"清除失败: {e}")

                # 保存
                self.logger.info("💾 保存配置...")
                try:
                    save_btn = page.wait_for_selector("#save", timeout=5000)
                    if save_btn:
                        save_btn.click()
                        time.sleep(2)
                        self.logger.info("✅ 已保存")
                except:
                    self.logger.warning("保存失败")

                self.logger.info("=" * 60)
                if success:
                    self.logger.info("✅ 断开并清除完成")
                else:
                    self.logger.error("❌ 清除验证失败")

                time.sleep(2)
                browser.close()
                return success

        except Exception as e:
            self.logger.error(f"清除账号时发生错误: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False


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

            cleaner = RouterAccountCleaner()
            success = cleaner.clear_account()

            if success:
                self.logger.info("账号密码已成功清除")
            else:
                self.logger.warning("账号密码清除失败")

        except Exception as e:
            self.logger.error(f"清理失败: {e}", exc_info=True)


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(ShutdownCleanupService)
