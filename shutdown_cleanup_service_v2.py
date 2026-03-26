#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TP-Link路由器账号清理服务 - 简化版（用于调试）
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
        """执行实际的清理操作（参考主程序的断开逻辑）"""
        try:
            captured_stok = []

            def capture_stok(route, request):
                url = request.url
                if "stok=" in url:
                    match = re.search(r"stok=([^/&?#]+)", url)
                    if match and not captured_stok:
                        stok_value = match.group(1)
                        captured_stok.append(stok_value)
                        self.logger.info(f"✅ 从网络请求中捕获到 stok: {stok_value}")
                route.continue_()

            with sync_playwright() as p:
                self.logger.info("🌐 正在启动 Chromium 浏览器（无头模式）...")

                executable_path = None
                try:
                    executable_path = check_browser()
                    self.logger.info(f"✅ 使用内置浏览器: {executable_path}")
                except RuntimeError as e:
                    self.logger.warning(f"⚠️ {e}")
                    if not getattr(sys, 'frozen', False):
                        self.logger.info("⚠️ 开发环境：使用系统默认浏览器")
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

                # ===== 登录路由器 =====
                self.logger.info("🔌 正在访问路由器管理页面...")
                self.logger.info(f"   目标: http://{self.router_ip}/")
                page.goto(f"http://{self.router_ip}/", timeout=30000)

                self.logger.info("🔑 等待登录密码输入框...")
                page.wait_for_selector("input[type='password']", timeout=10000)
                self.logger.info("   找到密码输入框，正在填写...")
                page.fill("input[type='password']", self.router_password)
                self.logger.info("   已填写密码，正在提交登录...")
                page.keyboard.press("Enter")

                self.logger.info("⏳ 正在验证登录，等待token响应...")

                # 等待捕获到 stok
                for i in range(15):
                    time.sleep(1)
                    if captured_stok:
                        break

                page.unroute("**/*", capture_stok)

                if not captured_stok:
                    self.logger.error("❌ 登录失败，请检查管理员密码")
                    browser.close()
                    return False

                stok = captured_stok[0]
                self.logger.info("✅ 登录成功")

                # ===== 导航到上网设置页面 =====
                self.logger.info("🚀 正在访问上网设置页面...")
                self.logger.info("   方式: 菜单导航（确保页面完整加载）")
                self.logger.info(f"   📍 返回主页: http://{self.router_ip}/")
                page.goto(f"http://{self.router_ip}/")
                time.sleep(2)

                try:
                    router_set_btn = page.wait_for_selector("#routerSetMbtn", timeout=3000)
                    if router_set_btn:
                        self.logger.info("   📍 点击'路由器设置'按钮...")
                        router_set_btn.click()
                        time.sleep(2)
                except:
                    self.logger.info("   ⚠️ 未找到路由器设置按钮")

                try:
                    network_menu = page.wait_for_selector("#network_rsMenu", timeout=3000)
                    if network_menu:
                        self.logger.info("   📍 点击'网络'菜单...")
                        network_menu.click()
                        time.sleep(2)
                except:
                    self.logger.info("   ⚠️ 未找到网络菜单")

                # 点击上网设置菜单
                internet_menu_selectors = [
                    "#network_rsMenu",
                    "li#network_rsMenu",
                    "li.menuLi",
                    "li:has-text('上网设置')",
                ]

                menu_clicked = False
                for selector in internet_menu_selectors:
                    try:
                        menu_item = page.wait_for_selector(selector, timeout=2000)
                        if menu_item:
                            self.logger.info(f"   📍 点击上网设置菜单 ({selector})...")
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

                # 验证页面是否真的在上网设置页面
                self.logger.info("   🔍 验证页面位置...")
                try:
                    name_input = page.wait_for_selector("#name", timeout=5000)
                    if name_input:
                        self.logger.info("   ✅ 已进入上网设置页面")
                    else:
                        self.logger.warning("   ⚠️ 页面验证失败，但继续执行")
                except:
                    self.logger.warning("   ⚠️ 无法验证页面位置，但继续执行")

                # ===== 断开连接 =====
                self.logger.info("🔌 正在断开网络连接...")
                self.logger.info("   按钮: #disconnect")
                try:
                    disconnect_btn = page.wait_for_selector("#disconnect", timeout=5000)
                    if disconnect_btn:
                        self.logger.info("   ✅ 找到断开按钮，正在点击...")
                        disconnect_btn.click()
                        self.logger.info("   ✅ 已点击断开按钮")
                        time.sleep(2)
                        self.logger.info("✅ 网络连接已断开")
                    else:
                        self.logger.warning("   ⚠️ 断开按钮不存在（可能已经断开）")
                except Exception as e:
                    self.logger.warning(f"   ⚠️ 查找/点击断开按钮失败: {e}")

                # ===== 清除账号密码 =====
                self.logger.info("🗑️ 正在清除账号密码...")
                success = False

                try:
                    # 清空账号
                    self.logger.info("   📝 清空账号输入框 (#name)...")
                    name_input = page.wait_for_selector("#name", timeout=5000)
                    if name_input:
                        name_input.fill("")
                        self.logger.info("   ✅ 账号输入框已清空")
                    else:
                        self.logger.warning("   ⚠️ 未找到账号输入框")

                    # 清空密码
                    self.logger.info("   📝 清空密码输入框 (#psw)...")
                    psw_input = page.wait_for_selector("#psw", timeout=5000)
                    if psw_input:
                        psw_input.fill("")
                        self.logger.info("   ✅ 密码输入框已清空")
                    else:
                        self.logger.warning("   ⚠️ 未找到密码输入框")

                    # 验证账号密码是否真的被清除了
                    self.logger.info("   🔍 正在验证账号密码是否已清除...")
                    time.sleep(1)
                    name_value = name_input.input_value() if name_input else ""
                    psw_value = psw_input.input_value() if psw_input else ""
                    self.logger.info(f"   📋 验证结果：账号=[{name_value}], 密码=[{psw_value}]")

                    if not name_value and not psw_value:
                        self.logger.info("✅ 账号密码已清除")
                        success = True
                    else:
                        self.logger.error(f"❌ 清除失败：账号=[{name_value}], 密码=[{psw_value}]")
                except Exception as e:
                    self.logger.error(f"⚠️ 清除账号密码时出错: {e}")
                    import traceback
                    self.logger.error(f"详细错误: {traceback.format_exc()}")

                # ===== 保存配置 =====
                self.logger.info("💾 正在保存配置（空账号密码）...")
                self.logger.info("   按钮: #save")
                try:
                    save_btn = page.wait_for_selector("#save", timeout=5000)
                    if save_btn:
                        self.logger.info("   ✅ 找到保存按钮，正在点击...")
                        save_btn.click()
                        self.logger.info("   ✅ 已点击保存按钮")
                        time.sleep(2)
                        self.logger.info("✅ 配置已保存")
                    else:
                        self.logger.warning("   ⚠️ 未找到保存按钮")
                except Exception as e:
                    self.logger.warning(f"   ⚠️ 保存配置时出错: {e}")

                self.logger.info("=" * 60)
                if success:
                    self.logger.info("✅ 断开并清除完成")
                else:
                    self.logger.error("❌ 清除验证失败")
                self.logger.info("=" * 60)

                time.sleep(2)
                browser.close()
                return success

        except Exception as e:
            self.logger.error(f"❌ 清除账号时发生错误: {e}")
            import traceback
            self.logger.error(f"详细错误: {traceback.format_exc()}")
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
        self.log_dir = None

        # 立即报告服务正在启动（关键：快速响应）
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)

        # 最小化初始化 - 只设置日志路径，不创建文件
        try:
            self.log_dir = Path(r"C:\Program Files\TPLinkDialer\logs")
        except:
            self.log_dir = Path(os.environ.get('TEMP', '/tmp')) / 'tplink_cleanup'

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
        # 快速设置日志（如果还没设置）
        if not self.logger:
            log_file = self.log_dir / 'cleanup_service.log'
            try:
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

        self.logger.info("=" * 60)
        self.logger.info("🚨 收到系统关机通知！")
        self.logger.info("=" * 60)

        # 报告服务正在停止
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
            # 先报告服务已运行（关键：避免超时）
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)

            # 然后设置日志（在后台进行）
            log_file = self.log_dir / 'cleanup_service.log'
            try:
                self.log_dir.mkdir(parents=True, exist_ok=True)
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
            self.logger.info("=" * 60)
            self.logger.info("✅ 服务已启动")
            self.logger.info(f"日志文件: {log_file}")
            self.logger.info("=" * 60)

            # 验证配置（在后台进行）
            try:
                config_manager = ConfigManager()
                config = config_manager.get_config()
                self.logger.info(f"配置信息:")
                self.logger.info(f"  路由器IP: {config.get('router_ip')}")
                self.logger.info(f"  路由器密码: {'已设置' if config.get('router_password') else '未设置'}")
            except Exception as e:
                self.logger.warning(f"验证配置时出错: {e}")

            # 初始化清理器（在后台进行）
            try:
                self.logger.info("正在初始化清理器...")
                self.cleaner = RouterAccountCleaner()
                self.logger.info("✅ 清理器初始化完成")
            except Exception as e:
                self.logger.error(f"⚠️ 清理器初始化失败: {e}")
                self.logger.warning("服务将继续运行，但清理功能可能无法正常工作")

            self.logger.info("✅ 服务已就绪，等待关机事件...")

            # 主循环：等待关机或停止事件
            count = 0
            while self.is_alive:
                result = win32event.WaitForSingleObject(self.hWaitStop, 5000)

                if result == win32event.WAIT_OBJECT_0:
                    break

                count += 1
                # 定期记录心跳（每分钟）
                if count % 12 == 0:
                    self.logger.info(f"💓 服务运行中... ({count // 12}分钟)")

        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ 服务运行时出错: {e}", exc_info=True)
            self.ReportServiceStatus(win32service.SERVICE_STOPPED)


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(ShutdownCleanupService)
