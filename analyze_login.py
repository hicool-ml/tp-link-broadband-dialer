#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试路由器登录 - 详细分析
"""

import requests
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup


def analyze_login():
    """分析登录流程"""

    # 读取配置
    config_file = Path.home() / ".tplink_dialer" / "config.json"

    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    router_ip = config.get("router_ip", "192.168.1.1")
    router_password = "Cdu@123"  # 明码密码

    print(f"路由器: {router_ip}")
    print(f"密码: {router_password}")
    print()

    session = requests.Session()
    base_url = f"http://{router_ip}"

    # 步骤1: 访问首页，分析HTML
    print("=" * 60)
    print("步骤1: 分析首页HTML")
    print("=" * 60)

    r = session.get(base_url + "/", timeout=10)

    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(r.text, 'html.parser')

    # 查找所有input标签
    print("\n所有表单输入:")
    for inp in soup.find_all('input'):
        print(f"  name={inp.get('name')}, type={inp.get('type')}, id={inp.get('id')}, value={inp.get('value')}")

    # 查找所有script标签中的JS变量
    print("\nJavaScript变量（可能包含token）:")
    scripts = soup.find_all('script')
    for script in scripts:
        if script.string:
            # 查找可能包含token或密钥的变量
            matches = re.findall(r'var\s+(\w+)\s*=\s*["\']([^"\']+)["\']', script.string)
            for match in matches:
                var_name, var_value = match
                if len(var_value) > 8 and 'token' in var_name.lower() or 'key' in var_name.lower():
                    print(f"  {var_name} = {var_value}")

    # 查找form标签
    print("\n所有表单:")
    for form in soup.find_all('form'):
        print(f"  action={form.get('action')}, method={form.get('method')}")

    # 查找隐藏字段
    print("\n隐藏字段:")
    for inp in soup.find_all('input', type='hidden'):
        print(f"  name={inp.get('name')}, value={inp.get('value')}")

    # 步骤2: 尝试不同的登录方式
    print("\n" + "=" * 60)
    print("步骤2: 尝试登录")
    print("=" * 60)

    # 方式1: 直接POST密码（明文）
    print("\n尝试方式1: POST明文密码")

    payload1 = {
        "method": "do",
        "login": {
            "password": router_password
        }
    }

    try:
        r = session.post(base_url + "/", json=payload1, timeout=10)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text[:200]}")

        if "stok=" in r.url:
            match = re.search(r"stok=([a-zA-Z0-9]+)", r.url)
            if match:
                print(f"[SUCCESS] 获取到stok: {match.group(1)}")
                return match.group(1)
    except Exception as e:
        print(f"[ERROR] {e}")

    # 方式2: 从HTML中提取登录表单的action
    print("\n尝试方式2: 查找登录表单action")

    login_form = soup.find('form')
    if login_form:
        action = login_form.get('action', '')
        print(f"登录表单action: {action}")

        # 收集表单数据
        form_data = {}
        for inp in login_form.find_all('input'):
            name = inp.get('name')
            value = inp.get('value', '')
            if name:
                if inp.get('type') != 'password' or value:
                    form_data[name] = value
                else:
                    form_data[name] = router_password

        print(f"表单数据: {form_data}")

        try:
            if action:
                url = base_url + action if not action.startswith('http') else action
            else:
                url = base_url + "/"

            # 尝试POST
            r = session.post(url, data=form_data, timeout=10)
            print(f"Status: {r.status_code}")
            print(f"Response: {r.text[:200]}")

            if "stok=" in r.url:
                match = re.search(r"stok=([a-zA-Z0-9]+)", r.url)
                if match:
                    print(f"[SUCCESS] 获取到stok: {match.group(1)}")
                    return match.group(1)
        except Exception as e:
            print(f"[ERROR] {e}")

    # 方式3: 查看是否有特殊的API端点
    print("\n尝试方式3: 查找API端点")

    # 查找所有可能的API端点
    api_patterns = [
        "/web",
        "/api",
        "/datas",
        "/user",
        "/login",
    ]

    for pattern in api_patterns:
        try:
            print(f"  尝试: {base_url}{pattern}")
            r = session.get(base_url + pattern, timeout=5)
            print(f"    Status: {r.status_code}")
            if r.status_code == 200:
                print(f"    [OK] 端点存在")
        except:
            print(f"    [FAIL] 不存在")


if __name__ == '__main__':
    analyze_login()
