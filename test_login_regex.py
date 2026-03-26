#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试路由器登录 - 使用正则表达式
"""

import requests
import json
import re
from pathlib import Path


def test_login():
    """测试登录"""

    # 读取配置
    config_file = Path.home() / ".tplink_dialer" / "config.json"

    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    router_ip = config.get("router_ip", "192.168.1.1")
    router_password = "Cdu@123"

    print(f"路由器: {router_ip}")
    print(f"密码: {router_password}")
    print()

    session = requests.Session()
    base_url = f"http://{router_ip}"

    # 步骤1: 获取首页
    print("=" * 60)
    print("步骤1: 获取首页")
    print("=" * 60)

    r = session.get(base_url + "/", timeout=10)
    html = r.text

    # 提取所有input
    inputs = re.findall(r'<input[^>]*name=["\']?([^"\'\s>]+)["\']?[^>]*>', html)
    print(f"\n找到 {len(inputs)} 个input标签")

    # 查找hidden字段
    hidden_fields = re.findall(r'<input[^>]*type=["\']?hidden["\']?[^>]*value=["\']?([^"\'\s>]+)["\']?[^>]*name=["\']?([^"\'\s>]+)', html, re.IGNORECASE)
    if hidden_fields:
        print("\n隐藏字段:")
        for value, name in hidden_fields:
            print(f"  {name} = {value}")

    # 查找form action
    form_action = re.search(r'<form[^>]*action=["\']?([^"\'\s>]+)["\']?', html, re.IGNORECASE)
    if form_action:
        print(f"\n表单action: {form_action.group(1)}")

    # 步骤2: 尝试登录
    print("\n" + "=" * 60)
    print("步骤2: 尝试登录")
    print("=" * 60)

    # 方式1: POST明文密码到根路径
    print("\n方式1: POST到 /")

    payload1 = {
        "method": "do",
        "login": {
            "password": router_password
        }
    }

    try:
        r = session.post(base_url + "/", json=payload1, timeout=10)
        print(f"Status: {r.status_code}")

        # 检查响应
        if r.status_code == 200:
            print(f"Response preview: {r.text[:200]}")

            # 尝试从响应中获取stok
            if "stok=" in r.url:
                match = re.search(r"stok=([a-zA-Z0-9]+)", r.url)
                if match:
                    stok = match.group(1)
                    print(f"[SUCCESS] 从URL获取stok: {stok}")
                    test_with_stok(base_url, stok, session)
                    return
            elif "stok=" in r.text:
                matches = re.findall(r"stok=([a-zA-Z0-9]+)", r.text)
                if matches:
                    print(f"[SUCCESS] 从响应获取stok: {matches}")
                    test_with_stok(base_url, matches[0], session)
                    return

            # 尝试解析JSON
            try:
                result = r.json()
                print(f"JSON响应: {json.dumps(result, indent=2, ensure_ascii=False)}")

                if result.get("error_code") == 0:
                    print("[SUCCESS] 登录成功")
                else:
                    print(f"[FAIL] 登录失败，错误码: {result.get('error_code')}")
            except:
                pass

    except Exception as e:
        print(f"[ERROR] {e}")

    # 方式2: 查找特殊的登录端点
    print("\n方式2: 查找登录端点")

    # 检查常见的登录API
    login_endpoints = [
        "/",
        "/login",
        "/user/login",
        "/api/login",
        "/web",
        "/data/login"
    ]

    for endpoint in login_endpoints:
        try:
            print(f"\n  测试: {endpoint}")
            r = session.post(base_url + endpoint, json=payload1, timeout=5)
            print(f"    Status: {r.status_code}")

            if r.status_code == 200 and "stok=" in r.text:
                matches = re.findall(r"stok=([a-zA-Z0-9]+)", r.text)
                if matches:
                    print(f"    [SUCCESS] 找到stok: {matches[0]}")
                    test_with_stok(base_url, matches[0], session)
                    return

        except Exception as e:
            print(f"    [FAIL] {e}")


def test_with_stok(base_url, stok, session):
    """使用stok测试清理功能"""

    print("\n" + "=" * 60)
    print("使用stok测试清理功能")
    print("=" * 60)

    # 测试断开连接
    print("\n测试: 断开连接")
    url = f"{base_url}/stok={stok}/ds"

    payload = {
        "network": {
            "change_wan_status": {
                "proto": "pppoe",
                "operate": "disconnect"
            }
        },
        "method": "do"
    }

    try:
        r = session.post(url, json=payload, timeout=10)
        print(f"Status: {r.status_code}")

        try:
            result = r.json()
            print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")

            if result.get("error_code", -1) == 0:
                print("[OK] 断开成功")

                # 测试清空账号
                print("\n测试: 清空账号")
                payload2 = {
                    "network": {
                        "wan_pppoe": {
                            "username": "",
                            "password": ""
                        }
                    },
                    "method": "set"
                }

                r2 = session.post(url, json=payload2, timeout=10)
                print(f"Status: {r2.status_code}")

                try:
                    result2 = r2.json()
                    print(f"Response: {json.dumps(result2, indent=2, ensure_ascii=False)}")

                    if result2.get("error_code", -1) == 0:
                        print("[OK] 清空成功")
                        print("\n[SUCCESS] HTTP方案可行！")
                    else:
                        print(f"[WARN] 清空失败，错误码: {result2.get('error_code')}")

                except Exception as e:
                    print(f"[ERROR] {e}")

        except Exception as e:
            print(f"Response: {r.text[:200]}")

    except Exception as e:
        print(f"[ERROR] {e}")


if __name__ == '__main__':
    test_login()
