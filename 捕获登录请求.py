#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
捕获真实的登录请求
使用 Playwright 访问路由器，记录所有网络请求
"""

import sys
import json
from playwright.sync_api import sync_playwright
from pathlib import Path


def capture_login_request():
    """捕获登录请求"""

    # 读取配置
    config_file = Path.home() / ".tplink_dialer" / "config.json"

    if not config_file.exists():
        print("[ERROR] 配置文件不存在")
        return

    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    router_ip = config.get("router_ip", "192.168.1.1")
    router_password = "Cdu@123"  # 明文密码

    print(f"路由器: {router_ip}")
    print(f"密码: {router_password}")
    print()
    print("=" * 60)
    print("正在启动浏览器并捕获请求...")
    print("=" * 60)

    captured_requests = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # 有头模式，便于观察
        context = browser.new_context()
        page = context.new_page()

        # 监听所有请求
        def log_request(request):
            url = request.url
            method = request.method
            headers = request.headers

            # 只记录 POST 请求
            if method == "POST":
                print(f"\n[捕获到 POST 请求]")
                print(f"URL: {url}")
                print(f"Method: {method}")
                print(f"\nHeaders:")
                for key, value in headers.items():
                    if key.lower() in ['content-type', 'referer', 'origin', 'cookie', 'x-requested-with']:
                        print(f"  {key}: {value}")

                # 获取 POST body
                try:
                    post_data = request.post_data
                    if post_data:
                        print(f"\nPOST Body:")
                        print(f"  {post_data}")

                        # 尝试解析 JSON
                        try:
                            data = json.loads(post_data)
                            print(f"\n解析后的 JSON:")
                            print(json.dumps(data, indent=2, ensure_ascii=False))
                        except:
                            pass

                except Exception as e:
                    pass

                captured_requests.append({
                    'url': url,
                    'method': method,
                    'headers': dict(headers),
                    'post_data': getattr(request, 'post_data', None)
                })

        page.on("request", log_request)

        # 访问路由器页面
        print(f"\n正在访问: http://{router_ip}/")
        page.goto(f"http://{router_ip}/", timeout=30000)

        print("\n页面加载完成")
        print("=" * 60)
        print("请在浏览器中：")
        print("1. 输入密码: Cdu@123")
        print("2. 点击登录按钮")
        print("3. 等待登录成功")
        print("=" * 60)

        # 等待用户手动登录
        input("\n按回车键继续...")

        # 保存捕获的请求到文件
        output_file = Path("captured_requests.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(captured_requests, f, indent=2, ensure_ascii=False)

        print(f"\n[SUCCESS] 已捕获 {len(captured_requests)} 个POST请求")
        print(f"已保存到: {output_file.absolute()}")

        # 分析登录请求
        print("\n" + "=" * 60)
        print("分析登录请求...")
        print("=" * 60)

        for i, req in enumerate(captured_requests):
            print(f"\n请求 #{i+1}:")
            print(f"  URL: {req['url']}")
            print(f"  Body: {req['post_data']}")

            if 'login' in req['post_data'].lower() or 'password' in req['post_data'].lower():
                print(f"  >>> 这可能是登录请求！")

        browser.close()

    return captured_requests


if __name__ == '__main__':
    print("=" * 60)
    print("TP-Link 登录请求捕获工具")
    print("=" * 60)
    print()

    try:
        capture_login_request()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

    print()
    print("=" * 60)
    print("提示：")
    print("1. 捕获的请求已保存到 captured_requests.json")
    print("2. 请查看 'login' 相关的请求")
    print("3. 特别注意 password 字段的格式（加密/明文）")
    print("4. 注意 Cookie 和 Referer 等头部信息")
    print("=" * 60)
