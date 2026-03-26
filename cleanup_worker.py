#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
清理工作脚本 - 在独立进程中运行
被服务调用，执行实际的路由器清理操作
"""

import sys
import os
import time
import logging
import re
from pathlib import Path

# 禁用Playwright的自动更新
os.environ["PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD"] = "1"

# ✅ 使用importlib延迟导入
def main():
    try:
        # 设置日志
        log_dir = Path(os.environ.get('TEMP', '/tmp')) / 'tplink_cleanup'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / 'cleanup_worker.log'

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
        logger.info("清理工作进程启动")
        logger.info("=" * 60)

        # 延迟导入依赖
        import importlib

        # 获取当前目录
        current_dir = Path(__file__).parent
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))

        # 导入必要模块
        config_module = importlib.import_module("config_manager")
        ConfigManager = config_module.ConfigManager

        from playwright.sync_api import sync_playwright

        # 读取配置
        config_mgr = ConfigManager()
        config = config_mgr.get_config()
        router_ip = config.get('router_ip', '192.168.1.1')
        router_password = config.get('router_password', '')

        if not router_password:
            logger.warning("密码未配置，跳过清理")
            return

        # 执行清理
        clear_router_account(router_ip, router_password, logger)

        logger.info("✅ 清理工作完成")

    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"清理工作失败: {e}", exc_info=True)


def clear_router_account(router_ip, router_password, logger):
    """清除路由器账号密码"""
    try:
        # 导入BrowserManager
        import importlib
        browser_module = importlib.import_module("browser_manager")
        BrowserManager = browser_module.BrowserManager

        browser_manager = BrowserManager()

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
            logger.info("🌐 启动浏览器...")

            executable_path = None
            try:
                executable_path = browser_manager.get_browser_path()
                logger.info(f"✅ 使用浏览器: {executable_path}")
            except RuntimeError as e:
                logger.warning(f"⚠️ {e}")
                if not getattr(sys, 'frozen', False):
                    logger.info("⚠️ 开发环境：使用系统浏览器")
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
            logger.info("🔌 访问路由器...")
            page.goto(f"http://{router_ip}/", timeout=30000)
            logger.info("🔑 等待密码框...")
            page.wait_for_selector("input[type='password']", timeout=10000)
            page.fill("input[type='password']", router_password)
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
                return

            logger.info("✅ 登录成功")

            # 导航到上网设置
            logger.info("🚀 导航到上网设置...")
            page.goto(f"http://{router_ip}/")
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
                logger.error("❌ 无法打开上网设置")
                browser.close()
                return

            # 断开连接
            logger.info("🔌 断开连接...")
            try:
                disconnect_btn = page.wait_for_selector("#disconnect", timeout=5000)
                if disconnect_btn:
                    disconnect_btn.click()
                    time.sleep(2)
                    logger.info("✅ 已断开")
            except:
                logger.warning("断开按钮不存在")

            # 清除账号密码
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
                logger.error(f"清除失败: {e}")

            # 保存
            logger.info("💾 保存配置...")
            try:
                save_btn = page.wait_for_selector("#save", timeout=5000)
                if save_btn:
                    save_btn.click()
                    time.sleep(2)
                    logger.info("✅ 已保存")
            except:
                logger.warning("保存失败")

            logger.info("=" * 60)
            if success:
                logger.info("✅ 断开并清除完成")
            else:
                logger.error("❌ 清除验证失败")

            time.sleep(2)
            browser.close()

    except Exception as e:
        logger.error(f"清除账号时发生错误: {e}")
        import traceback
        logger.error(traceback.format_exc())


if __name__ == '__main__':
    main()
