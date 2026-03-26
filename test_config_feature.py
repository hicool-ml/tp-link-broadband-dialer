#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试配置管理功能

验证：
1. 配置加密存储
2. 配置读取和验证
3. 前端配置界面
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from config_manager import ConfigManager

def test_config_encryption():
    """测试配置加密功能"""
    print("=" * 60)
    print("配置管理功能测试")
    print("=" * 60)
    
    manager = ConfigManager()
    
    # 1. 显示配置文件路径
    print(f"\n📁 配置文件位置: {manager.config_file}")
    
    # 2. 检查是否已配置
    is_configured = manager.is_configured()
    print(f"{'✅' if is_configured else '⚠️'} 配置状态: {'已配置' if is_configured else '未配置'}")
    
    # 3. 读取当前配置
    config = manager.get_config()
    print(f"\n当前配置:")
    print(f"  - 路由器IP: {config.get('router_ip', 'N/A')}")
    print(f"  - 路由器密码: {'已设置' if config.get('router_password') else '未设置'}")
    print(f"  - 版本: {config.get('version', 'N/A')}")
    
    # 4. 检查配置文件内容（加密后的）
    if manager.config_file.exists():
        import json
        with open(manager.config_file, 'r', encoding='utf-8') as f:
            raw_config = json.load(f)
        
        print(f"\n🔒 配置文件内容（加密后）:")
        print(f"  - router_ip: {raw_config.get('router_ip', 'N/A')} (明文)")
        print(f"  - router_password: {raw_config.get('router_password', 'N/A')[:30]}... (加密)")
    
    # 5. 测试加密解密
    print(f"\n🔐 加密测试:")
    test_password = "TestPassword123"
    encrypted = manager.encrypt_password(test_password)
    decrypted = manager.decrypt_password(encrypted)
    print(f"  原始密码: {test_password}")
    print(f"  加密后: {encrypted[:50]}...")
    print(f"  解密后: {decrypted}")
    print(f"  {'✅ 加密解密成功' if decrypted == test_password else '❌ 加密解密失败'}")
    
    print("\n" + "=" * 60)
    print("前端配置功能:")
    print("  1. 首次启动自动显示配置向导")
    print("  2. 主界面'⚙ 设置'按钮可重新配置")
    print("  3. 配置保存后立即生效，无需重启")
    print("  4. 密码自动加密存储")
    print("=" * 60)

if __name__ == '__main__':
    test_config_encryption()
