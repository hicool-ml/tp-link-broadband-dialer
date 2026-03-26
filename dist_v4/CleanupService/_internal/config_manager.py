#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置管理模块

负责管理路由器配置，支持：
- 配置文件的读取和保存
- 密码加密存储
- 配置向导
- 配置验证
"""

import json
import os
import sys
import base64
import hashlib
from pathlib import Path


class ConfigManager:
    """配置管理器"""

    def __init__(self):
        # 配置文件路径（放在用户目录下，避免权限问题）
        if getattr(sys, 'frozen', False):
            # 打包后的环境，使用用户目录
            config_dir = Path.home() / '.tplink_dialer'
        else:
            # 开发环境，使用项目目录
            config_dir = Path(__file__).parent

        config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = config_dir / 'config.json'

        # 默认配置
        self.default_config = {
            'router_ip': '192.168.1.1',
            'router_password': '',
            'version': '1.0'
        }

    def load_config(self):
        """加载配置文件"""
        if not self.config_file.exists():
            return None

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 解密密码
            if 'router_password' in config and config['router_password']:
                config['router_password'] = self.decrypt_password(config['router_password'])

            return config
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return None

    def save_config(self, config):
        """保存配置文件"""
        try:
            # 加密密码
            config_to_save = config.copy()
            if 'router_password' in config_to_save and config_to_save['router_password']:
                config_to_save['router_password'] = self.encrypt_password(config_to_save['router_password'])

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False

    def encrypt_password(self, password):
        """简单的密码加密（Base64 + 混淆）"""
        # 注意：这不是强加密，只是为了防止明文存储
        # 生产环境建议使用 cryptography 库
        salt = "tplink_dialer_2026"
        combined = password + salt
        hashed = hashlib.sha256(combined.encode()).hexdigest()
        encoded = base64.b64encode((password + "|" + hashed).encode()).decode()
        return encoded

    def decrypt_password(self, encrypted):
        """解密密码"""
        try:
            decoded = base64.b64decode(encrypted.encode()).decode()
            password, _ = decoded.split("|")
            return password
        except:
            return ""

    def validate_config(self, config):
        """验证配置有效性"""
        if not config:
            return False, "配置为空"

        if 'router_ip' not in config or not config['router_ip']:
            return False, "路由器IP地址不能为空"

        if 'router_password' not in config or not config['router_password']:
            return False, "路由器管理密码不能为空"

        # 验证IP格式
        ip = config['router_ip'].strip()
        parts = ip.split('.')
        if len(parts) != 4:
            return False, "IP地址格式不正确"

        try:
            for part in parts:
                num = int(part)
                if num < 0 or num > 255:
                    return False, "IP地址格式不正确"
        except:
            return False, "IP地址格式不正确"

        return True, ""

    def is_configured(self):
        """检查是否已配置"""
        config = self.load_config()
        if not config:
            return False

        valid, _ = self.validate_config(config)
        return valid

    def get_config(self):
        """获取配置，如果未配置则返回默认配置"""
        config = self.load_config()
        if config:
            valid, _ = self.validate_config(config)
            if valid:
                return config

        # 返回默认配置
        return self.default_config.copy()


def get_router_config():
    """便捷函数：获取路由器配置"""
    manager = ConfigManager()
    return manager.get_config()


if __name__ == '__main__':
    # 测试代码
    manager = ConfigManager()

    print(f"配置文件路径: {manager.config_file}")
    print(f"已配置: {manager.is_configured()}")

    config = manager.get_config()
    print(f"当前配置: {config}")
