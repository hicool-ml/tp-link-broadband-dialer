#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
路由器连接测试

实际测试：
1. 连接到路由器
2. 登录
3. 检查当前状态
4. （可选）测试账号清除
"""

import sys
import os
import time
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

# 添加site-packages路径
site_packages = r"C:\Program Files\Python311\Lib\site-packages"
if site_packages not in sys.path:
    sys.path.insert(0, site_packages)

from playwright.sync_api import sync_playwright
import re

def test_router_connection():
    """测试路由器连接"""
    print("=" * 60)
    print("路由器连接测试")
    print("=" * 60)

    # 读取配置
    from config_manager import ConfigManager
    config_manager = ConfigManager()
    config = config_manager.get_config()

    router_ip = config.get('router_ip', '192.168.1.1')
    router_password = config.get('router_password', '')

    if not router_password:
        print("[ERROR] 路由器密码未配置！")
        print("请先配置路由器信息。")
        return False

    print(f"\n路由器信息:")
    print(f"  IP: {router_ip}")
    print(f"  密码: {'已设置' if router_password else '未设置'}")

    print(f"\n开始连接测试...\n")

    try:
        # 获取浏览器路径
        from browser_manager import BrowserManager
        browser_manager = BrowserManager()
        browser_path = browser_manager.get_browser_path()

        if not browser_path:
            print("[WARN] 未找到内置浏览器，使用系统浏览器")

        captured_stok = []

        def capture_stok(route, request):
            url = request.url
            if "stok=" in url:
                match = re.search(r"stok=([^/&?#]+)", url)
                if match and not captured_stok:
                    stok_value = match.group(1)
                    captured_stok.append(stok_value)
                    print(f"[OK] 捕获到登录令牌: {stok_value[:20]}...")
            route.continue_()

        with sync_playwright() as p:
            print("[1/5] 启动浏览器...")
            launch_options = {
                'headless': False,  # 显示浏览器，便于观察
                'slow_mo': 500,
                'args': [
                    "--no-sandbox",
                    "--disable-gpu",
                    "--lang=zh-CN",
                ],
            }

            if browser_path:
                launch_options['executable_path'] = browser_path

            browser = p.chromium.launch(**launch_options)
            context = browser.new_context()
            page = context.new_page()
            page.route("**/*", capture_stok)

            print(f"[2/5] 访问路由器管理页面 (http://{router_ip}/)...")
            page.goto(f"http://{router_ip}/", timeout=30000)

            print("[3/5] 输入管理员密码...")
            page.wait_for_selector("input[type='password']", timeout=10000)
            page.fill("input[type='password']", router_password)
            page.keyboard.press("Enter")

            print("[4/5] 等待登录...")
            for i in range(15):
                time.sleep(1)
                if captured_stok:
                    break

            page.unroute("**/*", capture_stok)

            if not captured_stok:
                print("[ERROR] 登录失败！请检查密码是否正确。")
                browser.close()
                return False

            print("[OK] 登录成功！")
            time.sleep(2)

            # 检查当前状态
            print("\n[5/5] 检查路由器状态...")

            try:
                # 尝试导航到网络设置
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

            # 获取WAN IP
            try:
                ip_element = page.wait_for_selector("#wanIpLbl", timeout=5000)
                if ip_element:
                    ip_address = ip_element.inner_text()
                    print(f"\n当前状态:")
                    print(f"  WAN IP: {ip_address}")

                    if ip_address and ip_address != "0.0.0.0" and ip_address.strip():
                        print(f"  状态: 已连接")
                    else:
                        print(f"  状态: 未连接")
            except Exception as e:
                print(f"[WARN] 无法获取IP状态: {e}")

            # 检查账号配置
            try:
                name_input = page.wait_for_selector("#name", timeout=3000)
                if name_input:
                    name_value = name_input.input_value()
                    print(f"  宽带账号: {name_value if name_value else '(未配置)'}")
            except:
                print(f"  宽带账号: 无法获取")

            print("\n" + "=" * 60)
            print("[SUCCESS] 路由器连接测试完成")
            print("=" * 60)

            # 等待一段时间观察
            print("\n浏览器将在10秒后关闭...")
            time.sleep(10)

            browser.close()
            return True

    except Exception as e:
        print(f"\n[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_router_connection()
    print(f"\n测试结果: {'成功' if success else '失败'}")
    exit(0 if success else 1)
