#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动捕获浏览器操作时的 API 请求
"""
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from playwright.sync_api import sync_playwright
import time

router_ip = "192.168.1.1"
router_password = "Cdu@123"

# 检查浏览器
def check_browser():
    try:
        from browser_manager import BrowserManager
        browser_manager = BrowserManager()
        return browser_manager.get_browser_path()
    except:
        return None

captured_requests = []

def log_request(request):
    """记录 POST 请求"""
    if request.method == "POST":
        url = request.url
        post_data = request.post_data
        captured_requests.append({
            'url': url,
            'post_data': post_data,
            'response': None  # 稍后填充
        })

def log_response(response):
    """记录响应"""
    request = response.request
    if request.method == "POST":
        url = request.url
        post_data = request.post_data
        for req in captured_requests:
            if req['url'] == url and req['post_data'] == post_data:
                req['response'] = response.text
                break

print("=" * 60)
print("自动捕获路由器 API 请求")
print("=" * 60)
print(f"路由器: {router_ip}")
print()

try:
    executable_path = check_browser()
    if executable_path:
        print(f"使用浏览器: {executable_path}")
except:
    executable_path = None

with sync_playwright() as p:
    launch_options = {
        'headless': True,  # 无头模式
        'args': ["--no-sandbox", "--disable-gpu"],
    }
    if executable_path:
        launch_options['executable_path'] = executable_path

    browser = p.chromium.launch(**launch_options)
    context = browser.new_context()
    page = context.new_page()

    page.on("request", log_request)
    page.on("response", log_response)

    print("正在访问路由器...")
    page.goto(f"http://{router_ip}/")

    print("正在登录...")
    try:
        page.wait_for_selector("input[type='password']", timeout=10000)
        page.fill("input[type='password']", router_password)
        page.keyboard.press("Enter")
        time.sleep(3)
        print("登录成功")
    except Exception as e:
        print(f"登录失败: {e}")
        browser.close()
        sys.exit(1)

    # 尝试导航到网络设置页面
    print("\n正在导航到网络设置...")

    # 尝试不同的方式导航
    try:
        # 点击路由设置
        page.goto(f"http://{router_ip}/")
        time.sleep(2)
        try:
            router_set_btn = page.wait_for_selector("#routerSetMbtn", timeout=3000)
            if router_set_btn:
                router_set_btn.click()
                time.sleep(2)
                print("已点击路由设置")
        except:
            pass

        try:
            network_menu = page.wait_for_selector("#network_rsMenu", timeout=3000)
            if network_menu:
                network_menu.click()
                time.sleep(2)
                print("已点击网络菜单")
        except:
            pass
    except Exception as e:
        print(f"导航失败: {e}")

    # 尝试断开连接
    print("\n正在尝试断开连接...")
    try:
        disconnect_btn = page.wait_for_selector("#disconnect", timeout=5000)
        if disconnect_btn:
            disconnect_btn.click()
            time.sleep(2)
            print("已点击断开按钮")
    except Exception as e:
        print(f"断开失败: {e}")

    # 尝试清空账号密码
    print("\n正在尝试清空账号密码...")
    try:
        name_input = page.wait_for_selector("#name", timeout=5000)
        if name_input:
            name_input.fill("")
            print("已清空账号")

        psw_input = page.wait_for_selector("#psw", timeout=5000)
        if psw_input:
            psw_input.fill("")
            print("已清空密码")
    except Exception as e:
        print(f"清空失败: {e}")

    # 尝试保存
    print("\n正在尝试保存...")
    try:
        save_btn = page.wait_for_selector("#save", timeout=5000)
        if save_btn:
            save_btn.click()
            time.sleep(2)
            print("已点击保存按钮")
    except Exception as e:
        print(f"保存失败: {e}")

    browser.close()

print("\n" + "=" * 60)
print(f"共捕获 {len(captured_requests)} 个 POST 请求")
print("=" * 60)

# 保存结果
output = []
for i, req in enumerate(captured_requests, 1):
    print(f"\n请求 #{i}:")
    print(f"  URL: {req['url']}")
    print(f"  Data: {req['post_data']}")

    if req['response']:
        print(f"  Response: {req['response']}")

    # 判断请求类型
    url = req['url']
    data = req['post_data'] or ''

    request_info = {
        'url': url,
        'data': data,
        'response': req['response']
    }

    if 'disconnect' in data.lower() or 'change_wan_status' in data.lower():
        request_info['type'] = 'disconnect'
        print("  >>> 类型: 断开连接")
    elif 'name' in data and 'psw' in data:
        request_info['type'] = 'clear_account'
        print("  >>> 类型: 清空账号密码")
    elif 'save' in data.lower() or 'apply' in data.lower():
        request_info['type'] = 'save'
        print("  >>> 类型: 保存配置")
    else:
        request_info['type'] = 'unknown'
        print("  >>> 类型: 未知")

    output.append(request_info)

# 保存到文件
with open("captured_apis.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 60)
print("结果已保存到 captured_apis.json")
print("=" * 60)
