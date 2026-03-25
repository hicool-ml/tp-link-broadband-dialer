#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TP-Link 路由器 HTTP 接口清理器
不使用浏览器，直接通过 HTTP 请求操作 TP-Link 路由器
"""

import requests
import hashlib
import time
import re
import logging
import base64
import json
from typing import Optional, Dict, Any
from urllib.parse import unquote


def parse_config_password(config_password: str) -> str:
    """
    从配置文件格式中提取明文密码

    配置文件格式: Base64(明文|SHA256哈希)

    Args:
        config_password: 配置文件中的密码（可能是 Base64 编码的）

    Returns:
        str: 明文密码
    """
    # 尝试 Base64 解码
    try:
        decoded = base64.b64decode(config_password).decode('utf-8')
        if '|' in decoded:
            # 格式: 明文|哈希
            plaintext = decoded.split('|')[0]
            return plaintext
    except:
        pass

    # 如果解码失败或没有 | 分隔符，直接返回原始值
    return config_password


def encrypt_password(pwd: str) -> str:
    """
    TP-Link 密码加密算法

    Args:
        pwd: 明文密码

    Returns:
        str: 加密后的密码
    """
    key = "RDpbLfCPsJZ7fiv"
    char_map = ("yLwVl0zKqws7LgKPRQ84Mdt708T1qQ3Ha7xv3H7NyU84p21BriUWBU43odz3iP4rBL3cD02KZciXTysVXiV8ngg6vL48rPJyAUw0HurW20xqxv9aYb4M9wK1Ae0wlro510qXeU07kV57fQMc8L6aLgMLwygtc0F10a0Dg70TOoouyFhdysuRMO51yY5ZlOZZLEal1h0t9YQW0Ko7oBwmCAHoic4HYbUyVeU3sfQ1xtXcPcf1aT303wAQhv66qzW")

    result = ""
    k = 187
    l = 187

    f = len(pwd)
    g = len(key)
    h = len(char_map)
    e = max(f, g)

    for m in range(e):
        k = 187
        l = 187

        if m >= f:
            l = ord(key[m])
        elif m >= g:
            k = ord(pwd[m])
        else:
            k = ord(pwd[m])
            l = ord(key[m])

        index = (k ^ l) % h
        result += char_map[index]

    return result


class TPLinkHTTPCleaner:
    """TP-Link 路由器 HTTP 清理器"""

    def __init__(self, router_ip: str, router_password: str):
        """
        初始化清理器

        Args:
            router_ip: 路由器 IP 地址
            router_password: 路由器管理密码（可能是配置文件格式）
        """
        self.router_ip = router_ip
        # 解析配置文件格式的密码
        self.router_password = parse_config_password(router_password)
        self.base_url = f"http://{router_ip}"
        self.session = requests.Session()
        self.stok = None
        self.logger = logging.getLogger(__name__)

    def _log(self, message: str):
        """记录日志"""
        if self.logger:
            self.logger.info(message)
        else:
            print(message)

    def login(self) -> bool:
        """
        登录路由器并获取 stok token

        Returns:
            bool: 登录是否成功
        """
        self._log("[INFO] 正在登录路由器...")

        try:
            # 1. 访问首页获取 session
            url = f"{self.base_url}/"
            response = self.session.get(url, timeout=10)
            self._log(f"[DEBUG] 首页状态: {response.status_code}")

            # 2. 使用加密后的密码登录
            encrypted_pwd = encrypt_password(self.router_password)
            self._log(f"[DEBUG] 加密后密码: {encrypted_pwd}")

            login_data = {
                "method": "do",
                "login": {
                    "password": encrypted_pwd
                }
            }

            headers = {
                "Content-Type": "application/json",
                "Referer": url,
                "Origin": self.base_url
            }

            response = self.session.post(url, json=login_data, headers=headers, timeout=10)
            self._log(f"[DEBUG] 登录响应状态: {response.status_code}")
            self._log(f"[DEBUG] 登录响应内容: {response.text[:200]}")

            # 3. 从响应中提取 stok
            if response.status_code == 200:
                result = response.json()

                # 检查错误码
                if result.get("error_code") == 0:
                    # stok 可能在根级别或 data 字段中
                    if "stok" in result:
                        raw_stok = result["stok"]
                        self.stok = unquote(raw_stok)  # URL 解码
                        self._log(f"[DEBUG] 原始 stok: {raw_stok}")
                        self._log(f"[DEBUG] 解码 stok: {self.stok}")
                        self._log(f"[SUCCESS] 登录成功 (stok: {self.stok[:20]}...)")
                        return True
                    elif "data" in result and "stok" in result["data"]:
                        raw_stok = result["data"]["stok"]
                        self.stok = unquote(raw_stok)  # URL 解码
                        self._log(f"[DEBUG] 原始 stok: {raw_stok}")
                        self._log(f"[DEBUG] 解码 stok: {self.stok}")
                        self._log(f"[SUCCESS] 登录成功 (stok: {self.stok[:20]}...)")
                        return True
                    else:
                        self._log(f"[WARNING] 响应中未找到 stok 字段: {result}")
                        return False
                else:
                    error_msg = result.get("error_msg", "未知错误")
                    self._log(f"[ERROR] 登录失败: 错误码 {result.get('error_code')}, 消息: {error_msg}")
                    return False
            else:
                self._log(f"[ERROR] 登录失败: HTTP {response.status_code}")
                return False

        except requests.RequestException as e:
            self._log(f"[ERROR] 网络错误: {e}")
            return False
        except Exception as e:
            self._log(f"[ERROR] 登录异常: {e}")
            import traceback
            self._log(traceback.format_exc())
            return False

    def disconnect_pppoe(self) -> bool:
        """
        断开 PPPoE 连接

        Returns:
            bool: 是否成功
        """
        self._log("🔌 正在断开 PPPoE 连接...")

        if not self.stok:
            self._log("❌ 未登录，无法断开连接")
            return False

        try:
            url = f"{self.base_url}/stok={self.stok}/ds"
            self._log(f"[DEBUG] 断开 URL: {url}")

            # TP-Link 常见的断开连接接口
            data = {
                "network": {
                    "change_wan_status": {
                        "proto": "pppoe",
                        "operate": "disconnect"
                    }
                },
                "method": "do"
            }
            self._log(f"[DEBUG] 断开请求数据: {json.dumps(data, ensure_ascii=False)}")

            headers = {
                "Content-Type": "application/json",
                "Referer": f"{self.base_url}/",
                "Origin": self.base_url
            }

            response = self.session.post(url, json=data, headers=headers, timeout=10)
            self._log(f"[DEBUG] 断开响应状态: {response.status_code}")
            self._log(f"[DEBUG] 断开响应内容: {response.text}")

            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get("error_code") == 0:
                        self._log("✅ PPPoE 已断开")
                        time.sleep(1)
                        return True
                    else:
                        self._log(f"⚠️ 断开失败: 错误码 {result.get('error_code')}")
                        return False
                except:
                    self._log("✅ PPPoE 已断开（无响应内容）")
                    time.sleep(1)
                    return True
            else:
                self._log(f"⚠️ 断开失败 (HTTP {response.status_code})")
                return False

        except Exception as e:
            self._log(f"❌ 断开异常: {e}")
            return False

    def clear_account(self) -> bool:
        """
        清空 PPPoE 账号密码

        Returns:
            bool: 是否成功
        """
        self._log("🗑️ 正在清空账号密码...")

        if not self.stok:
            self._log("❌ 未登录，无法清空账号")
            return False

        try:
            url = f"{self.base_url}/stok={self.stok}/ds"
            self._log(f"[DEBUG] 清空 URL: {url}")

            # 正确的清空格式（从浏览器捕获）
            data = {
                "protocol": {
                    "wan": {
                        "wan_type": "pppoe"
                    },
                    "pppoe": {
                        "username": "",
                        "password": ""
                    }
                },
                "method": "set"
            }
            self._log(f"[DEBUG] 清空请求数据: {json.dumps(data, ensure_ascii=False)}")

            headers = {
                "Content-Type": "application/json",
                "Referer": f"{self.base_url}/",
                "Origin": self.base_url
            }

            response = self.session.post(url, json=data, headers=headers, timeout=10)
            self._log(f"[DEBUG] 清空响应状态: {response.status_code}")
            self._log(f"[DEBUG] 清空响应内容: {response.text}")

            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get("error_code") == 0:
                        self._log("✅ 账号密码已清空")
                        time.sleep(1)
                        return True
                    else:
                        self._log(f"⚠️ 清空失败: 错误码 {result.get('error_code')}")
                        return False
                except:
                    self._log("✅ 账号密码已清空（无响应内容）")
                    time.sleep(1)
                    return True
            else:
                self._log(f"⚠️ 清空失败 (HTTP {response.status_code})")
                return False

        except Exception as e:
            self._log(f"❌ 清空异常: {e}")
            return False

    def save_config(self) -> bool:
        """
        保存路由器配置

        Returns:
            bool: 是否成功
        """
        self._log("💾 正在保存配置...")

        if not self.stok:
            self._log("❌ 未登录，无法保存配置")
            return False

        try:
            url = f"{self.base_url}/stok={self.stok}/ds"

            data = {
                "method": "do",
                "system": {
                    "save": 1
                }
            }

            response = self.session.post(url, json=data, timeout=10)

            if response.status_code == 200:
                self._log("✅ 配置已保存")
                time.sleep(1)
                return True
            else:
                self._log(f"⚠️ 保存失败 (HTTP {response.status_code})")
                return False

        except Exception as e:
            self._log(f"❌ 保存异常: {e}")
            return False

    def run_cleanup(self) -> bool:
        """
        执行完整的清理流程

        Returns:
            bool: 整体是否成功
        """
        try:
            self._log("=" * 60)
            self._log("开始执行路由器账号清理...")
            self._log("=" * 60)

            # 1. 登录
            if not self.login():
                self._log("❌ 清理失败：登录失败")
                return False

            # 2. 断开连接
            if not self.disconnect_pppoe():
                self._log("⚠️ 断开失败，但继续清理...")

            # 3. 清空账号
            if not self.clear_account():
                self._log("❌ 清理失败：清空账号失败")
                return False

            # 4. 保存配置
            if not self.save_config():
                self._log("⚠️ 保存配置失败，但账号已清空")

            self._log("=" * 60)
            self._log("✅ 清理完成！")
            self._log("=" * 60)

            return True

        except Exception as e:
            self._log(f"❌ 清理异常: {e}")
            import traceback
            self._log(traceback.format_exc())
            return False


# 便捷函数
def cleanup_router_account(router_ip: str, router_password: str, logger=None) -> bool:
    """
    清理路由器账号的便捷函数

    Args:
        router_ip: 路由器 IP
        router_password: 路由器密码
        logger: 可选的日志记录器

    Returns:
        bool: 是否成功
    """
    if logger:
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()],
            force=True
        )

    cleaner = TPLinkHTTPCleaner(router_ip, router_password)
    return cleaner.run_cleanup()


if __name__ == '__main__':
    # 测试代码
    import sys

    if len(sys.argv) > 2:
        ip = sys.argv[1]
        password = sys.argv[2]
        cleanup_router_account(ip, password)
    else:
        print("用法: python tplink_http_cleaner.py <router_ip> <password>")
        print("示例: python tplink_http_cleaner.py 192.168.1.1 admin123")
