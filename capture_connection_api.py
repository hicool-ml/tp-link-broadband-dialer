#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
捕获连接流程的API请求（包括填写账号密码和连接）
"""
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from playwright.sync_api import sync_playwright
import time

router_ip = "192.168.1.1"
router_password = "Cdu@123"
test_account = "test123"
test_password = "test123456"

def check_browser():
    try:
        from browser_manager import BrowserManager
        browser_manager = BrowserManager()
        return browser_manager.get_browser_path()
    except:
        return None

captured_requests = []

interesting_requests = []

def log_request(request):
    """记录所有 POST 请求"""
    if request.method == "POST":
        url = request.url
        post_data = request.post_data or ""

        # 只记录可能相关的请求
        keywords = ['pppoe', 'wan', 'mac', 'connect', 'save', 'protocol', 'network']
        if any(kw in post_data.lower() or kw in url.lower() for kw in keywords):
            interesting_requests.append({
                'url': url,
                'post_data': post_data,
                'timestamp': time.time()
            })
            print(f"\n>>> 捕获到相关请求:")
            print(f"    URL: {url}")
            print(f"    Data: {post_data}")

print("=" * 60)
print("捕获连接流程API请求")
print("=" * 60)
print(f"测试账号: {test_account}")
print(f"测试密码: {'*' * len(test_password)}")
print()

try:
    executable_path = check_browser()
    if executable_path:
        print(f"使用浏览器: {executable_path}")
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

    page.on("request", log_request)

    print("正在访问路由器...")
    page.goto(f"http://{router_ip}/")

    print("正在登录...")
    page.wait_for_selector("input[type='password']", timeout=10000)
    page.fill("input[type='password']", router_password)
    page.keyboard.press("Enter")
    time.sleep(3)
    print("登录成功")

    # 导航到网络设置
    print("\n正在导航到网络设置...")
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
            print("已进入网络设置")
    except:
        pass

    # 设置随机MAC
    print("\n正在设置随机MAC...")
    try:
        mac_sel = page.wait_for_selector("#wanMacSel", timeout=5000)
        if mac_sel:
            mac_sel.click()
            time.sleep(1)

            # 查找自定义MAC选项
            import random
            mac_bytes = [0x02, random.randint(0x00, 0xff), random.randint(0x00, 0xff),
                        random.randint(0x00, 0xff), random.randint(0x00, 0xff), random.randint(0x00, 0xff)]
            random_mac = "-".join([f"{b:02X}" for b in mac_bytes])

            # 尝试点击自定义MAC
            try:
                custom_mac = page.wait_for_selector("#selOptsUlwanMacSel li:has-text('自定义')", timeout=1000)
                if custom_mac:
                    custom_mac.click()
                    time.sleep(1)

                    # 填写MAC地址
                    mac_input = page.wait_for_selector("#wanMac", timeout=5000)
                    if mac_input:
                        mac_input.fill("")
                        mac_input.fill(random_mac)
                        print(f"已填写随机MAC: {random_mac}")

                        # 保存MAC设置
                        save_high = page.query_selector("#saveHighSet")
                        if save_high:
                            save_high.click()
                            time.sleep(3)
                            print("已保存MAC设置")
            except Exception as e:
                print(f"设置MAC失败: {e}")
    except Exception as e:
        print(f"MAC设置流程失败: {e}")

    # 填写PPPoE账号密码
    print("\n正在填写PPPoE账号密码...")
    try:
        name_input = page.wait_for_selector("#name", timeout=5000)
        if name_input:
            name_input.fill("")
            name_input.fill(test_account)
            print(f"已填写账号: {test_account}")

        psw_input = page.wait_for_selector("#psw", timeout=5000)
        if psw_input:
            psw_input.fill("")
            psw_input.fill(test_password)
            print(f"已填写密码")

        # 触发失焦
        page.locator("#psw").blur()
        time.sleep(1)
    except Exception as e:
        print(f"填写账号密码失败: {e}")

    # 点击连接按钮
    print("\n正在点击连接按钮...")
    try:
        save_btn = page.wait_for_selector("#save", timeout=5000)
        if save_btn:
            save_btn.click()
            print("已点击连接按钮")
            time.sleep(3)
    except Exception as e:
        print(f"点击连接按钮失败: {e}")

    browser.close()

print("\n" + "=" * 60)
print(f"共捕获 {len(interesting_requests)} 个相关请求")
print("=" * 60)

# 保存结果
output = []
for i, req in enumerate(interesting_requests, 1):
    print(f"\n请求 #{i}:")
    print(f"  URL: {req['url']}")
    print(f"  Data: {req['post_data']}")

    # 判断请求类型
    data = req['post_data'] or ''
    if 'wanMac' in data or 'mac' in data.lower():
        req_type = 'set_mac'
        print("  >>> 类型: 设置MAC")
    elif 'pppoe' in data.lower() and test_account in data:
        req_type = 'set_pppoe'
        print("  >>> 类型: 设置PPPoE账号密码")
    elif 'connect' in data.lower():
        req_type = 'connect'
        print("  >>> 类型: 连接")
    elif 'save' in data.lower():
        req_type = 'save'
        print("  >>> 类型: 保存")
    else:
        req_type = 'unknown'
        print("  >>> 类型: 未知")

    output.append({
        'type': req_type,
        'url': req['url'],
        'data': req['post_data']
    })

# 保存到文件
with open("connection_apis.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 60)
print("结果已保存到 connection_apis.json")
print("=" * 60)
