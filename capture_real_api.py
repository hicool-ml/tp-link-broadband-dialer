#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
捕获真实的路由器 API 请求
"""
import sys
import json
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from playwright.sync_api import sync_playwright
import time

# 配置
router_ip = "192.168.1.1"
router_password = "Cdu@123"

# 检查浏览器
def check_browser():
    from browser_manager import BrowserManager
    browser_manager = BrowserManager()
    return browser_manager.get_browser_path()

print("=" * 60)
print("路由器 API 捕获工具")
print("=" * 60)
print(f"路由器: {router_ip}")
print(f"密码: {router_password}")
print()
print("此工具会:")
print("1. 启动浏览器访问路由器")
print("2. 登录")
print("3. 手动操作断开连接")
print("4. 手动操作清空账号密码")
print("5. 手动操作保存")
print("6. 显示所有捕获的 API 请求")
print()

captured_requests = []

def capture_request(request):
    """捕获所有 POST 请求"""
    if request.method == "POST":
        url = request.url
        post_data = request.post_data

        print(f"\n{'=' * 60}")
        print(f"[POST 请求]")
        print(f"{'=' * 60}")
        print(f"URL: {url}")
        print()

        # Headers
        print("Headers:")
        for key, value in request.headers.items():
            if key.lower() in ['content-type', 'referer', 'origin', 'cookie']:
                print(f"  {key}: {value}")
        print()

        # POST body
        if post_data:
            print("POST Body:")
            print(f"  {post_data}")
            print()

            # 尝试解析并美化 JSON
            try:
                data = json.loads(post_data)
                print("解析后的 JSON:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
            except:
                pass

        captured_requests.append({
            'url': url,
            'method': request.method,
            'headers': dict(request.headers),
            'post_data': post_data
        })

# 启动浏览器
try:
    executable_path = check_browser()
    print(f"使用浏览器: {executable_path}")
except:
    executable_path = None
    print("使用系统默认浏览器")

with sync_playwright() as p:
    launch_options = {
        'headless': False,
        'slow_mo': 500,
        'args': ["--no-sandbox", "--disable-gpu"],
    }

    if executable_path:
        launch_options['executable_path'] = executable_path

    browser = p.chromium.launch(**launch_options)
    context = browser.new_context()
    page = context.new_page()

    # 设置请求监听
    page.on("request", capture_request)

    print("=" * 60)
    print("浏览器已启动")
    print("=" * 60)
    print()
    print("请执行以下操作:")
    print("1. 等待路由器页面加载")
    print("2. 输入密码并登录")
    print("3. 点击'路由设置'")
    print("4. 点击'上网设置'")
    print("5. 点击'断开'按钮")
    print("6. 清空账号密码输入框")
    print("7. 点击'保存'按钮")
    print("8. 回到这里按回车键")
    print("=" * 60)

    # 访问路由器
    page.goto(f"http://{router_ip}/")

    # 等待用户操作
    input()

    print()
    print("=" * 60)
    print(f"共捕获 {len(captured_requests)} 个POST请求")
    print("=" * 60)
    print()

    # 保存到文件
    output_file = Path("real_api_requests.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(captured_requests, f, indent=2, ensure_ascii=False)

    print(f"请求已保存到: {output_file.absolute()}")
    print()

    # 分析关键请求
    print("=" * 60)
    print("关键 API 请求分析:")
    print("=" * 60)

    for i, req in enumerate(captured_requests):
        url = req['url']
        post_data = req['post_data'] or ''

        print(f"\n>>> 请求 #{i+1}")
        print(f"    URL: {url}")
        print(f"    Data: {post_data}")

        # 判断请求类型
        if '/stok=' in url:
            if 'disconnect' in post_data.lower():
                print("    >>> 类型: 断开连接")
            elif 'network' in post_data.lower() and ('wan' in post_data.lower() or 'pppoe' in post_data.lower()):
                print("    >>> 类型: 网络设置/WAN配置")
            elif 'save' in post_data.lower() or 'apply' in post_data.lower():
                print("    >>> 类型: 保存配置")

    browser.close()

print()
print("=" * 60)
print("下一步:")
print("1. 查看 real_api_requests.json 文件")
print("2. 根据真实请求格式更新 tplink_http_cleaner.py")
print("=" * 60)
