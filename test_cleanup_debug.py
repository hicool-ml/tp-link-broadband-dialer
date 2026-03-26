#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试清理功能的调试脚本
"""

import sys
import os
import time
import logging
from pathlib import Path

# 添加项目路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# 导入必要模块
from config_manager import ConfigManager
from browser_manager import BrowserManager

# 导入Playwright
from playwright.sync_api import sync_playwright
import re

# 设置控制台编码
if sys.platform == 'win32':
    import ctypes
    import io
    ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()],
    force=True
)
logger = logging.getLogger(__name__)

# 禁用Playwright的自动更新
os.environ["PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD"] = "1"


def get_resource_path(relative_path):
    """获取PyInstaller打包后的内置资源路径"""
    if hasattr(sys, '_MEIPASS'):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent
    return str(base_path / relative_path)


def check_browser():
    """验证浏览器是否存在并返回路径"""
    browser_manager = BrowserManager()
    try:
        browser_path = browser_manager.get_browser_path()
        if browser_path:
            return browser_path
    except Exception:
        pass
    raise RuntimeError("浏览器未安装！请运行程序安装向导安装浏览器。")


def test_cleanup():
    """测试清理功能"""

    logger.info("=" * 60)
    logger.info("开始测试路由器账号清理功能")
    logger.info("=" * 60)

    # 读取配置
    config_manager = ConfigManager()
    config = config_manager.get_config()

    router_ip = config.get('router_ip', '192.168.1.1')
    router_password = config.get('router_password', '')

    logger.info(f"路由器地址: {router_ip}")
    logger.info(f"路由器密码: {'已配置' if router_password else '未配置'}")

    if not router_password:
        logger.error("错误：路由器密码未配置！")
        return False

    try:
        captured_stok = []

        def capture_stok(route, request):
            url = request.url
            if "stok=" in url:
                match = re.search(r"stok=([^/&?#]+)", url)
                if match and not captured_stok:
                    stok_value = match.group(1)
                    captured_stok.append(stok_value)
                    logger.info(f"✅ 捕获到 stok: {stok_value}")
            route.continue_()

        with sync_playwright() as p:
            logger.info("🌐 正在启动浏览器...")

            executable_path = None
            try:
                executable_path = check_browser()
                logger.info(f"✅ 浏览器路径: {executable_path}")
            except RuntimeError as e:
                logger.warning(f"⚠️ {e}")

            launch_options = {
                'headless': False,  # 调试时显示浏览器
                'slow_mo': 500,
                'args': [
                    "--no-sandbox",
                    "--disable-gpu",
                    "--disable-web-security",
                    "--lang=zh-CN",
                ],
            }

            if executable_path:
                launch_options['executable_path'] = executable_path

            browser = p.chromium.launch(**launch_options)
            context = browser.new_context()
            page = context.new_page()
            page.route("**/*", capture_stok)

            # ===== 登录 =====
            logger.info("🔌 访问路由器...")
            page.goto(f"http://{router_ip}/", timeout=30000)

            logger.info("🔑 等待密码输入框...")
            page.wait_for_selector("input[type='password']", timeout=10000)
            logger.info("   填写密码...")
            page.fill("input[type='password']", router_password)
            logger.info("   提交登录...")
            page.keyboard.press("Enter")

            logger.info("⏳ 等待token...")
            for i in range(15):
                time.sleep(1)
                if captured_stok:
                    break

            page.unroute("**/*", capture_stok)

            if not captured_stok:
                logger.error("❌ 登录失败")
                browser.close()
                return False

            logger.info("✅ 登录成功")

            # ===== 导航到上网设置 =====
            logger.info("🚀 导航到上网设置...")
            page.goto(f"http://{router_ip}/")
            time.sleep(2)

            try:
                router_set_btn = page.wait_for_selector("#routerSetMbtn", timeout=3000)
                if router_set_btn:
                    logger.info("   点击路由器设置...")
                    router_set_btn.click()
                    time.sleep(2)
            except:
                pass

            try:
                network_menu = page.wait_for_selector("#network_rsMenu", timeout=3000)
                if network_menu:
                    logger.info("   点击网络菜单...")
                    network_menu.click()
                    time.sleep(2)
            except:
                pass

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
                        logger.info(f"   点击上网设置菜单 ({selector})...")
                        menu_item.click()
                        menu_clicked = True
                        time.sleep(2)
                        break
                except:
                    continue

            if not menu_clicked:
                logger.error("❌ 无法打开上网设置")
                browser.close()
                return False

            # 验证在上网设置页面
            logger.info("   🔍 验证页面...")
            try:
                name_input = page.wait_for_selector("#name", timeout=5000)
                if name_input:
                    logger.info("   ✅ 已进入上网设置页面")
            except:
                logger.warning("   ⚠️ 无法验证页面")

            # ===== 断开连接 =====
            logger.info("🔌 断开连接...")
            try:
                disconnect_btn = page.wait_for_selector("#disconnect", timeout=5000)
                if disconnect_btn:
                    logger.info("   点击断开按钮...")
                    disconnect_btn.click()
                    time.sleep(2)
                    logger.info("✅ 已断开")
            except:
                logger.warning("   断开按钮不存在")

            # ===== 清除账号密码 =====
            logger.info("🗑️ 清除账号密码...")
            success = False

            try:
                name_input = page.wait_for_selector("#name", timeout=5000)
                psw_input = page.wait_for_selector("#psw", timeout=5000)

                if name_input:
                    name_input.fill("")
                    logger.info("   ✅ 账号已清空")

                if psw_input:
                    psw_input.fill("")
                    logger.info("   ✅ 密码已清空")

                time.sleep(1)
                name_value = name_input.input_value() if name_input else ""
                psw_value = psw_input.input_value() if psw_input else ""
                logger.info(f"   📋 验证: 账号=[{name_value}], 密码=[{psw_value}]")

                if not name_value and not psw_value:
                    logger.info("✅ 账号密码已清除")
                    success = True
            except Exception as e:
                logger.error(f"   清除失败: {e}")

            # ===== 保存 =====
            logger.info("💾 保存配置...")
            try:
                save_btn = page.wait_for_selector("#save", timeout=5000)
                if save_btn:
                    logger.info("   点击保存按钮...")
                    save_btn.click()
                    time.sleep(2)
                    logger.info("✅ 已保存")
            except:
                logger.warning("   保存失败")

            logger.info("=" * 60)
            logger.info("测试完成！")
            logger.info("=" * 60)

            time.sleep(5)
            browser.close()
            return success

    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = test_cleanup()
    if success:
        print("\n✅ 测试成功")
    else:
        print("\n❌ 测试失败")

    input("\n按回车键退出...")
