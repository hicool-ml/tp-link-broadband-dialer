#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
抓取登录请求并输出详细信息
"""

import sys
import json
import re
from pathlib import Path


def main():
    """主函数"""

    # 导入主程序模块
    sys.path.insert(0, str(Path(__file__).parent))

    print("=" * 60)
    print("TP-Link 登录请求抓取工具")
    print("=" * 60)
    print()
    print("此工具会:")
    print("1. 启动浏览器访问路由器")
    print("2. 监控所有网络请求")
    print("3. 您手动登录后，显示所有POST请求")
    print("4. 重点关注登录相关的请求")
    print()

    # 导入 Playwright
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[ERROR] 未安装 Playwright")
        print("请运行: pip install playwright")
        return

    # 读取配置
    config_file = Path.home() / ".tplink_dialer" / "config.json"

    if not config_file.exists():
        print("[ERROR] 配置文件不存在")
        return

    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    router_ip = config.get("router_ip", "192.168.1.1")
    router_password = "Cdu@123"

    print(f"路由器: {router_ip}")
    print(f"密码: {router_password}")
    print()

    captured_requests = []

    def capture_request(request):
        """捕获请求"""
        if request.method == "POST":
            url = request.url
            post_data = request.post_data

            print(f"\n{'=' * 60}")
            print(f"[POST 请求]")
            print(f"{'=' * 60}")
            print(f"URL: {url}")
            print(f"Method: {request.method}")
            print()

            # Headers
            print("Headers:")
            for key, value in request.headers.items():
                if key.lower() in ['content-type', 'referer', 'origin', 'cookie', 'x-requested-with']:
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
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # 有头模式
        context = browser.new_context()
        page = context.new_page()

        # 设置请求监听
        page.on("request", capture_request)

        print("=" * 60)
        print("浏览器已启动")
        print("=" * 60)
        print()
        print("请执行以下操作:")
        print("1. 在打开的浏览器中，输入密码: Cdu@123")
        print("2. 点击登录按钮")
        print("3. 登录成功后，回到这里，按回车键")
        print("=" * 60)

        # 访问路由器
        page.goto(f"http://{router_ip}/")

        # 等待用户登录
        input()

        print()
        print("=" * 60)
        print(f"共捕获 {len(captured_requests)} 个POST请求")
        print("=" * 60)
        print()

        # 保存到文件
        output_file = Path("login_requests.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(captured_requests, f, indent=2, ensure_ascii=False)

        print(f"请求已保存到: {output_file.absolute()}")
        print()

        # 分析可能的登录请求
        print("=" * 60)
        print("可能的登录请求分析:")
        print("=" * 60)

        for i, req in enumerate(captured_requests):
            url = req['url']
            post_data = req['post_data'] or ''

            is_login = False

            # 检查是否包含登录关键词
            login_keywords = ['login', 'password', 'auth', 'signin']
            url_lower = url.lower()
            data_lower = post_data.lower()

            if any(keyword in url_lower for keyword in login_keywords):
                is_login = True
            elif any(keyword in data_lower for keyword in login_keywords):
                is_login = True

            if is_login:
                print(f"\n>>> 请求 #{i+1} - 可能是登录请求:")
                print(f"    URL: {url}")
                print(f"    Data: {post_data}")

                # 保存到单独的文件
                login_request_file = Path("login_request.txt")
                with open(login_request_file, "w", encoding="utf-8") as f:
                    f.write(f"URL: {url}\n")
                    f.write(f"Method: POST\n")
                    f.write(f"Headers:\n")
                    for key, value in req['headers'].items():
                        if key.lower() in ['content-type', 'referer', 'origin', 'cookie']:
                            f.write(f"  {key}: {value}\n")
                    f.write(f"\nBody:\n{post_data}\n")

                print(f"    已保存到: {login_request_file.absolute()}")

        browser.close()

    print()
    print("=" * 60)
    print("下一步:")
    print("1. 查看 login_request.txt 文件")
    print("2. 重点关注密码字段的格式")
    print("3. 查看是否需要特殊的 headers（Cookie, Referer等）")
    print("4. 基于此格式实现纯 HTTP 版本")
    print("=" * 60)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
