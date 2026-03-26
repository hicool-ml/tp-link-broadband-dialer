#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 HTTP 清理功能
"""

import requests
import time
import json
import re
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

            self.headers = {
                "Content-Type": "application/json; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": f"http://{router_ip}/",
                "Origin": f"http://{router_ip}",
            }

        def login(self):
            print("[STEP 1] 登录路由器...")

            url = f"{self.base_url}/"
            payload = {
                "method": "do",
                "login": {
                    "password": self.password
                }
            }

            try:
                r = self.session.post(url, json=payload, timeout=5)

                match = re.search(r"stok=([a-zA-Z0-9\.\%\(\)\+]+)", r.text)
                if match:
                    self.stok = match.group(1)

                if not self.stok:
                    print("[ERROR] 未获取到stok")
                    print(f"响应: {r.text[:200]}")
                    return False

                print(f"[OK] 登录成功 (stok={self.stok[:10]}...)")
                return True

            except Exception as e:
                print(f"[ERROR] 登录失败: {e}")
                return False

        def post(self, data):
            url = f"{self.base_url}/stok={self.stok}/ds"
            r = self.session.post(url, json=data, headers=self.headers, timeout=5)
            print(f"   HTTP {r.status_code}")
            try:
                result = r.json()
                print(f"   响应: {result}")
            except:
                print(f"   响应: {r.text[:200]}")
            return r

        def disconnect(self):
            print("[STEP 2] 断开PPPoE连接")

            payload = {
                "network": {
                    "change_wan_status": {
                        "proto": "pppoe",
                        "operate": "disconnect"
                    }
                },
                "method": "do"
            }

            return self.post(payload)

        def clear_account(self):
            print("[STEP 3] 清空账号密码")

            payload = {
                "network": {
                    "wan_pppoe": {
                        "username": "",
                        "password": ""
                    }
                },
                "method": "set"
            }

            return self.post(payload)

        def connect(self):
            print("[STEP 4] 保存配置")

            payload = {
                "network": {
                    "change_wan_status": {
                        "proto": "pppoe",
                        "operate": "connect"
                    }
                },
                "method": "do"
            }

            return self.post(payload)

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
    client.run()


if __name__ == '__main__':
    print("=" * 60)
    print("TP-Link HTTP 清理功能测试")
    print("=" * 60)
    print()

    try:
        test_cleanup()
    except Exception as e:
        print(f"[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()

    print()
    print("=" * 60)
