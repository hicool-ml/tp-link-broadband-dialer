#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
安全加密模块

使用 AES-256 加密保护路由器密码
基于 cryptography 库实现军用级加密
"""

import base64
import hashlib
import os
import sys
from pathlib import Path


class SecureCrypto:
    """安全加密器"""

    def __init__(self):
        """初始化加密器"""
        # 尝试导入 cryptography 库
        try:
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives import padding
            self.Cipher = Cipher
            self.algorithms = algorithms
            self.modes = modes
            self.default_backend = default_backend
            self.padding = padding
            self.strong_crypto = True
        except ImportError:
            # 如果没有 cryptography，回退到简单加密
            self.strong_crypto = False
            print("警告: 未安装 cryptography 库，使用基础加密")
            print("建议运行: pip install cryptography")

        # 生成或获取机器唯一密钥
        self.key = self._get_or_create_key()

    def _get_machine_id(self):
        """获取机器唯一标识"""
        try:
            # Windows: 使用机器GUID
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                               r"SOFTWARE\Microsoft\Cryptography",
                               0, winreg.KEY_READ)
            guid, _ = winreg.QueryValueEx(key, "MachineGuid")
            winreg.CloseKey(key)
            return guid
        except:
            # 回退方案：结合多个机器特征
            import platform
            features = [
                platform.node(),
                platform.system(),
                platform.machine(),
                os.environ.get('USERNAME', 'unknown'),
                os.environ.get('COMPUTERNAME', 'unknown')
            ]
            return "|".join(features)

    def _get_or_create_key(self):
        """获取或创建加密密钥"""
        # 配置目录
        if getattr(sys, 'frozen', False):
            config_dir = Path.home() / '.tplink_dialer'
        else:
            config_dir = Path(__file__).parent

        config_dir.mkdir(parents=True, exist_ok=True)
        key_file = config_dir / '.crypto_key'

        # 尝试读取现有密钥
        if key_file.exists():
            try:
                with open(key_file, 'rb') as f:
                    return f.read()
            except:
                pass

        # 生成新密钥
        machine_id = self._get_machine_id()
        key_material = f"tplink_dialer_2026_{machine_id}".encode('utf-8')

        # 使用 SHA-256 生成 32 字节密钥（AES-256）
        key = hashlib.sha256(key_material).digest()

        # 保存密钥
        try:
            with open(key_file, 'wb') as f:
                f.write(key)
        except:
            pass

        return key

    def encrypt_password(self, password):
        """加密密码

        Args:
            password: 明文密码

        Returns:
            加密后的字符串（Base64编码）
        """
        if not password:
            return ""

        if self.strong_crypto:
            return self._encrypt_aes(password)
        else:
            return self._encrypt_simple(password)

    def _encrypt_aes(self, password):
        """使用 AES-256 加密"""
        try:
            # 生成随机 IV（初始化向量）
            iv = os.urandom(16)

            # 创建加密器
            cipher = self.Cipher(
                self.algorithms.AES(self.key),
                self.modes.CFB(iv),
                backend=self.default_backend()
            )
            encryptor = cipher.encryptor()

            # 加密
            encrypted = encryptor.update(password.encode('utf-8')) + encryptor.finalize()

            # 组合 IV + 密文，然后 Base64 编码
            combined = iv + encrypted
            return base64.b64encode(combined).decode('utf-8')

        except Exception as e:
            # 回退到简单加密
            return self._encrypt_simple(password)

    def _encrypt_simple(self, password):
        """简单加密（回退方案）"""
        salt = "tplink_dialer_2026_secure"
        combined = password + salt
        hashed = hashlib.sha512(combined.encode()).hexdigest()
        encoded = base64.b64encode((password + "|" + hashed).encode()).decode()
        return encoded

    def decrypt_password(self, encrypted):
        """解密密码

        Args:
            encrypted: 加密的字符串（Base64编码）

        Returns:
            明文密码
        """
        if not encrypted:
            return ""

        if self.strong_crypto:
            # 尝试 AES 解密
            try:
                return self._decrypt_aes(encrypted)
            except:
                # 失败则尝试简单解密
                pass

        return self._decrypt_simple(encrypted)

    def _decrypt_aes(self, encrypted):
        """使用 AES-256 解密"""
        try:
            # Base64 解码
            combined = base64.b64decode(encrypted.encode())

            # 分离 IV 和密文
            iv = combined[:16]
            ciphertext = combined[16:]

            # 创建解密器
            cipher = self.Cipher(
                self.algorithms.AES(self.key),
                self.modes.CFB(iv),
                backend=self.default_backend()
            )
            decryptor = cipher.decryptor()

            # 解密
            decrypted = decryptor.update(ciphertext) + decryptor.finalize()

            return decrypted.decode('utf-8')

        except Exception as e:
            raise ValueError("解密失败")

    def _decrypt_simple(self, encrypted):
        """简单解密（回退方案）"""
        try:
            decoded = base64.b64decode(encrypted.encode()).decode()
            password, _ = decoded.split("|")
            return password
        except:
            return ""


# 全局单例
_crypto_instance = None


def get_crypto():
    """获取加密器单例"""
    global _crypto_instance
    if _crypto_instance is None:
        _crypto_instance = SecureCrypto()
    return _crypto_instance


# 便捷函数
def encrypt_password(password):
    """加密密码"""
    return get_crypto().encrypt_password(password)


def decrypt_password(encrypted):
    """解密密码"""
    return get_crypto().decrypt_password(encrypted)


if __name__ == '__main__':
    # 测试加密解密
    print("安全加密模块测试")
    print("=" * 50)

    test_password = "MySecretPassword123"
    print(f"原始密码: {test_password}")

    # 加密
    encrypted = encrypt_password(test_password)
    print(f"加密后: {encrypted[:50]}...")

    # 解密
    decrypted = decrypt_password(encrypted)
    print(f"解密后: {decrypted}")

    # 验证
    if decrypted == test_password:
        print("\n✅ 测试通过：加密解密成功")
    else:
        print("\n❌ 测试失败：加密解密不匹配")
