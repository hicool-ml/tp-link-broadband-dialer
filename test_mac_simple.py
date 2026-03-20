# -*- coding: utf-8 -*-
"""测试MAC地址设置功能 - 简化版"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright
import time
import random
from pathlib import Path

def get_browser_path():
    possible_paths = [
        Path(__file__).parent / "chrome-win64" / "chrome.exe",
        Path(__file__).parent / "dist" / "TP-Link_Dialer" / "chrome-win64" / "chrome.exe",
    ]
    for path in possible_paths:
        if path.exists():
            return str(path)
    return None

def generate_random_mac():
    mac_bytes = [0x02, random.randint(0x00, 0xff), random.randint(0x00, 0xff),
                random.randint(0x00, 0xff), random.randint(0x00, 0xff), random.randint(0x00, 0xff)]
    return ":".join([f"{b:02X}" for b in mac_bytes])

def test_mac_setting():
    router_ip = "192.168.1.1"
    router_password = "Cdu@123"

    browser_path = get_browser_path()
    if not browser_path:
        print("未找到浏览器")
        return

    print(f"使用浏览器: {browser_path}")

    with sync_playwright() as p:
        print("启动浏览器...")
        launch_options = {
            'headless': False,
            'slow_mo': 300,
            'args': ["--no-sandbox", "--disable-gpu", "--disable-web-security"],
        }

        browser = p.chromium.launch(**launch_options, executable_path=browser_path)
        context = browser.new_context()
        page = context.new_page()

        # 访问路由器
        print(f"访问路由器 {router_ip}...")
        page.goto(f"http://{router_ip}/")

        # 登录
        print("登录中...")
        page.wait_for_selector("input[type='password']", timeout=10000)
        page.fill("input[type='password']", router_password)
        page.keyboard.press("Enter")

        # 等待登录并捕获stok
        captured_stok = []
        def capture_stok(route, request):
            import re
            url = request.url
            if "stok=" in url:
                match = re.search(r'stok=([^&]+)', url)
                if match:
                    stok = match.group(1)
                    if stok not in captured_stok:
                        captured_stok.append(stok)
                        print(f"捕获到 stok: {stok}")
            route.continue_()

        page.route("**/*", capture_stok)

        for i in range(15):
            time.sleep(1)
            if captured_stok:
                break

        page.unroute("**/*", capture_stok)

        if not captured_stok:
            print("登录失败")
            browser.close()
            return

        stok = captured_stok[0]
        print("登录成功")

        # 访问PPPoE页面
        print("访问PPPoE配置页面...")
        wanc_url = f"http://{router_ip}/userRpm/PPPoECfgRpm.htm?stok={stok}"
        page.goto(wanc_url, timeout=10000)
        time.sleep(3)

        # 检查MAC输入框
        print("\n检查MAC输入框状态...")
        try:
            mac_input = page.wait_for_selector("#wanMac", timeout=5000)
            if mac_input:
                print(f"找到 #wanMac")
                print(f"  可见: {mac_input.is_visible()}")
                print(f"  启用: {mac_input.is_enabled()}")
                print(f"  当前值: '{mac_input.input_value()}'")
        except Exception as e:
            print(f"未找到 #wanMac: {e}")

        # 检查保存按钮
        try:
            save_btn = page.wait_for_selector("#saveHighSet", timeout=3000)
            if save_btn:
                print(f"找到 #saveHighSet")
                print(f"  可见: {save_btn.is_visible()}")
                print(f"  启用: {save_btn.is_enabled()}")
        except Exception as e:
            print(f"未找到 #saveHighSet: {e}")

        # 生成并填写MAC
        random_mac = generate_random_mac()
        print(f"\n生成随机MAC: {random_mac}")
        print("尝试填写...")

        try:
            # 清空并填写
            page.fill("#wanMac", "")
            time.sleep(0.5)
            page.fill("#wanMac", random_mac)
            time.sleep(0.5)

            # 验证
            current_value = page.input_value("#wanMac")
            print(f"填写后值: '{current_value}'")

            if current_value.upper() == random_mac.upper():
                print("验证成功！MAC已正确填写")

                # 尝试保存
                print("\n点击高级设置保存按钮...")
                page.click("#saveHighSet")
                time.sleep(3)
                print("保存完成")

                # 再次验证
                final_value = page.input_value("#wanMac")
                print(f"保存后值: '{final_value}'")
                if final_value.upper() == random_mac.upper():
                    print("SUCCESS: MAC地址已成功保存！")
                else:
                    print("WARNING: 保存后值不一致")
            else:
                print(f"FAILED: 填写失败. 期望: {random_mac}, 实际: {current_value}")

        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()

        print("\n测试完成，5秒后关闭...")
        time.sleep(5)
        browser.close()

if __name__ == "__main__":
    test_mac_setting()
