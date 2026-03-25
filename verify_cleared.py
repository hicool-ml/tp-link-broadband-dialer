#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证路由器账号是否已清空
"""
import sys
sys.path.insert(0, '.')

from playwright.sync_api import sync_playwright
import time

router_ip = "192.168.1.1"
router_password = "Cdu@123"

def check_browser():
    try:
        from browser_manager import BrowserManager
        browser_manager = BrowserManager()
        return browser_manager.get_browser_path()
    except:
        return None

print("=" * 60)
print("验证路由器账号密码")
print("=" * 60)

try:
    executable_path = check_browser()
except:
    executable_path = None

with sync_playwright() as p:
    launch_options = {
        'headless': True,
        'args': ["--no-sandbox", "--disable-gpu"],
    }
    if executable_path:
        launch_options['executable_path'] = executable_path

    browser = p.chromium.launch(**launch_options)
    context = browser.new_context()
    page = context.new_page()

    print("正在访问路由器...")
    page.goto(f"http://{router_ip}/")

    print("正在登录...")
    page.wait_for_selector("input[type='password']", timeout=10000)
    page.fill("input[type='password']", router_password)
    page.keyboard.press("Enter")
    time.sleep(3)

    print("正在导航到网络设置...")
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

    print("\n检查账号密码...")
    try:
        name_input = page.wait_for_selector("#name", timeout=5000)
        if name_input:
            name_value = name_input.input_value()
            print(f"账号: [{name_value}]")
        else:
            print("未找到账号输入框")

        psw_input = page.wait_for_selector("#psw", timeout=5000)
        if psw_input:
            psw_value = psw_input.input_value()
            print(f"密码: [{psw_value}]")
        else:
            print("未找到密码输入框")

        if not name_value and not psw_value:
            print("\n✅ 账号密码已成功清空！")
        else:
            print("\n❌ 账号密码未清空")
    except Exception as e:
        print(f"检查失败: {e}")

    browser.close()

print("\n" + "=" * 60)
