#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 HTTP 清理功能 - 调试版本
"""

import requests
import time
import json
import re
import hashlib
from pathlib import Path


def test_cleanup():
    """测试清理功能"""

    # 读取配置
    config_file = Path.home() / ".tplink_dialer" / "config.json"

    if not config_file.exists():
        print("[ERROR] 配置文件不存在")
        return

    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    router_ip = config.get("router_ip", "192.168.1.1")
    router_password = config.get("router_password", "")

    print(f"路由器IP: {router_ip}")
    print(f"路由器密码: {'***' if router_password else '(未设置)'}")
    print()

    session = requests.Session()
    base_url = f"http://{router_ip}"

    # 步骤1: 访问首页
    print("=" * 60)
    print("DEBUG: 步骤1 - 访问首页")
    print("=" * 60)

    try:
        r = session.get(base_url + "/", timeout=10)
        print(f"HTTP Status: {r.status_code}")
        print(f"URL: {r.url}")
        print()
        print("响应内容（前500字符）:")
        print(r.text[:500])
        print()

        # 检查是否包含stok
        if "stok=" in r.url:
            match = re.search(r"stok=([a-zA-Z0-9]+)", r.url)
            if match:
                stok = match.group(1)
                print(f"[FOUND] stok in URL: {stok}")

        if "stok=" in r.text:
            matches = re.findall(r"stok=([a-zA-Z0-9]+)", r.text)
            if matches:
                print(f"[FOUND] stok in HTML: {matches}")

    except Exception as e:
        print(f"[ERROR] {e}")

    print()

    # 步骤2: 尝试POST登录
    print("=" * 60)
    print("DEBUG: 步骤2 - 尝试POST登录")
    print("=" * 60)

    try:
        encoded_pwd = hashlib.md5(router_password.encode()).hexdigest()

        payload = {
            "method": "do",
            "login": {
                "password": encoded_pwd
            }
        }

        print(f"Payload: {json.dumps(payload, indent=2)}")
        print()

        r = session.post(base_url + "/", json=payload, timeout=10)
        print(f"HTTP Status: {r.status_code}")
        print(f"URL: {r.url}")
        print()
        print("响应内容:")
        print(r.text)
        print()

        # 尝试解析JSON
        try:
            result = r.json()
            print("JSON解析:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        except:
            print("无法解析为JSON")

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_cleanup()
