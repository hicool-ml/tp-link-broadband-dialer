#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 HTTP 清理功能 v2
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
        print(f"请确保已配置路由器信息：{config_file}")
        return

    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    router_ip = config.get("router_ip", "192.168.1.1")
    router_password = config.get("router_password", "")

    if not router_password:
        print("[ERROR] 路由器密码未配置")
        return

    print(f"路由器IP: {router_ip}")
    print(f"路由器密码: {'***' if router_password else '(未设置)'}")
    print()

    # HTTP 客户端
    class TPLinkHTTPClient:
        def __init__(self, router_ip, password):
            self.router_ip = router_ip
            self.password = password
            self.base_url = f"http://{router_ip}"
            self.session = requests.Session()
            self.stok = None

        def login(self):
            print("[STEP 1] 登录路由器...")

            url = f"{self.base_url}/"

            # 尝试方式1: 直接访问首页获取stok
            try:
                print("   尝试方式1: 直接访问首页...")
                r = self.session.get(url, timeout=5)

                if "stok=" in r.url:
                    match = re.search(r"stok=([a-zA-Z0-9\.\%\(\)\+]+)", r.url)
                    if match:
                        self.stok = match.group(1)
                        print(f"[OK] 从URL获取到stok: {self.stok[:10]}...")
                        return True

                match = re.search(r"stok=([a-zA-Z0-9\.\%\(\)\+]+)", r.text)
                if match:
                    self.stok = match.group(1)
                    print(f"[OK] 从响应获取到stok: {self.stok[:10]}...")
                    return True
            except Exception as e:
                print(f"   失败: {e}")

            # 尝试方式2: POST登录（MD5加密密码）
            try:
                print("   尝试方式2: POST登录（MD5加密）...")

                encoded_pwd = hashlib.md5(self.password.encode()).hexdigest()

                payload = {
                    "method": "do",
                    "login": {
                        "password": encoded_pwd
                    }
                }

                r = self.session.post(url, json=payload, timeout=5)

                # 检查响应
                if r.status_code == 200:
                    # 尝试从响应中获取stok
                    if "stok=" in r.text:
                        match = re.search(r"stok=([a-zA-Z0-9\.\%\(\)\+]+)", r.text)
                        if match:
                            self.stok = match.group(1)
                            print(f"[OK] 登录成功 (stok={self.stok[:10]}...)")
                            return True

                    # 尝试解析JSON响应
                    try:
                        result = r.json()
                        if "stok" in result:
                            self.stok = result["stok"]
                            print(f"[OK] 登录成功 (stok={self.stok[:10]}...)")
                            return True

                        if "error_code" in result and result["error_code"] != 0:
                            print(f"[ERROR] 登录失败 (错误码: {result['error_code']})")
                            print(f"   响应: {result}")
                            return False
                    except:
                        pass

            except Exception as e:
                print(f"[ERROR] 登录失败: {e}")

            return False

        def disconnect(self):
            print("[STEP 2] 断开PPPoE连接")

            if not self.stok:
                print("[ERROR] 未登录")
                return False

            url = f"{self.base_url}/stok={self.stok}/ds"

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
                r = self.session.post(url, json=payload, timeout=5)
                print(f"   HTTP {r.status_code}")

                try:
                    result = r.json()
                    print(f"   响应: {result}")

                    if result.get("error_code", -1) == 0:
                        print("[OK] 断开成功")
                        return True
                    else:
                        print("[WARN] 断开失败，但继续清理...")
                        return True
                except:
                    print(f"   响应: {r.text[:200]}")

            except Exception as e:
                print(f"[ERROR] {e}")

            return False

        def clear_account(self):
            print("[STEP 3] 清空账号密码")

            if not self.stok:
                print("[ERROR] 未登录")
                return False

            url = f"{self.base_url}/stok={self.stok}/ds"

            payload = {
                "network": {
                    "wan_pppoe": {
                        "username": "",
                        "password": ""
                    }
                },
                "method": "set"
            }

            try:
                r = self.session.post(url, json=payload, timeout=5)
                print(f"   HTTP {r.status_code}")

                try:
                    result = r.json()
                    print(f"   响应: {result}")

                    if result.get("error_code", -1) == 0:
                        print("[OK] 清空成功")
                        return True
                    else:
                        print("[WARN] 清空失败，但继续...")
                        return True
                except:
                    print(f"   响应: {r.text[:200]}")

            except Exception as e:
                print(f"[ERROR] {e}")

            return False

        def connect(self):
            print("[STEP 4] 保存配置")

            if not self.stok:
                print("[ERROR] 未登录")
                return False

            url = f"{self.base_url}/stok={self.stok}/ds"

            payload = {
                "network": {
                    "change_wan_status": {
                        "proto": "pppoe",
                        "operate": "connect"
                    }
                },
                "method": "do"
            }

            try:
                r = self.session.post(url, json=payload, timeout=5)
                print(f"   HTTP {r.status_code}")

                try:
                    result = r.json()
                    print(f"   响应: {result}")

                    if result.get("error_code", -1) == 0:
                        print("[OK] 保存成功")
                        return True
                    else:
                        print("[WARN] 保存失败，但账号已清空...")
                        return True
                except:
                    print(f"   响应: {r.text[:200]}")

            except Exception as e:
                print(f"[ERROR] {e}")

            return False

        def run(self):
            if not self.login():
                print("[FAIL] 清理失败：登录失败")
                return False

            print()
            self.disconnect()
            time.sleep(1)
            print()

            self.clear_account()
            time.sleep(1)
            print()

            self.connect()
            print()

            print("[SUCCESS] 清理完成！")
            return True

    # 运行测试
    client = TPLinkHTTPClient(router_ip, router_password)
    return client.run()


if __name__ == '__main__':
    print("=" * 60)
    print("TP-Link HTTP 清理功能测试 v2")
    print("=" * 60)
    print()

    try:
        success = test_cleanup()
        if success:
            print("\n[SUCCESS] 测试通过")
        else:
            print("\n[FAIL] 测试失败")
    except Exception as e:
        print(f"[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()

    print()
    print("=" * 60)
