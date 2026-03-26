#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
综合功能测试脚本

测试项目：
1. 配置加密存储
2. 主程序启动
3. 路由器连接
4. 账号清除
5. 清理服务
6. 服务安装器
"""

import sys
import os
import subprocess
import time
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

def print_header(title):
    """打印测试标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_1_config_encryption():
    """测试1: 配置加密存储"""
    print_header("测试1: 配置加密存储")

    try:
        from config_manager import ConfigManager

        manager = ConfigManager()
        print(f"[OK] 配置文件位置: {manager.config_file}")

        # 读取配置
        config = manager.get_config()
        print(f"[OK] 路由器IP: {config.get('router_ip')}")
        print(f"[OK] 路由器密码: {'已设置' if config.get('router_password') else '未设置'}")

        # 测试加密
        test_pwd = "TestPassword123"
        encrypted = manager.encrypt_password(test_pwd)
        decrypted = manager.decrypt_password(encrypted)

        if decrypted == test_pwd:
            print("[OK] 加密解密测试通过")
            return True
        else:
            print("[FAIL] 加密解密测试失败")
            return False

    except Exception as e:
        print(f"[FAIL] 配置测试失败: {e}")
        return False

def test_2_browser_check():
    """测试2: 浏览器检查"""
    print_header("测试2: 浏览器检查")

    try:
        from browser_manager import BrowserManager

        browser_manager = BrowserManager()
        browser_path = browser_manager.get_browser_path()

        if browser_path and os.path.exists(browser_path):
            print(f"[OK] 浏览器路径: {browser_path}")
            print(f"[OK] 浏览器存在")
            return True
        else:
            print("[FAIL] 浏览器未找到")
            return False

    except Exception as e:
        print(f"[FAIL] 浏览器检查失败: {e}")
        return False

def test_3_service_status():
    """测试3: 清理服务状态"""
    print_header("测试3: 清理服务状态")

    try:
        result = subprocess.run(
            ['sc', 'query', 'TPLinkShutdownCleanup'],
            capture_output=True,
            text=True,
            encoding='gbk',
            errors='ignore'
        )

        if 'RUNNING' in result.stdout:
            print("[OK] 清理服务正在运行")
            print(f"[OK] 服务接受关机事件: {'ACCEPTS_SHUTDOWN' in result.stdout}")
            return True
        else:
            print("[FAIL] 清理服务未运行")
            print(result.stdout)
            return False

    except Exception as e:
        print(f"[FAIL] 服务状态检查失败: {e}")
        return False

def test_4_exe_files():
    """测试4: 检查生成的exe文件"""
    print_header("测试4: 检查生成的exe文件")

    files_to_check = [
        ("主程序", "dist/TP-Link_Dialer/TP-Link_Dialer.exe"),
        ("清理服务", "dist/CleanupService/CleanupService.exe"),
        ("服务安装器", "dist/ServiceInstaller.exe"),
        ("安装包", "Release/Setup.exe"),
    ]

    all_ok = True
    for name, path in files_to_check:
        if os.path.exists(path):
            size = os.path.getsize(path) / (1024 * 1024)
            print(f"[OK] {name}: {path} ({size:.1f} MB)")
        else:
            print(f"[FAIL] {name}: {path} (不存在)")
            all_ok = False

    return all_ok

def test_5_router_config():
    """测试5: 路由器配置"""
    print_header("测试5: 路由器配置")

    try:
        from config_manager import ConfigManager

        manager = ConfigManager()
        is_configured = manager.is_configured()

        if is_configured:
            config = manager.get_config()
            print(f"[OK] 已配置路由器")
            print(f"  IP: {config.get('router_ip')}")
            print(f"  密码: {'已设置' if config.get('router_password') else '未设置'}")

            # 检查配置文件内容
            if manager.config_file.exists():
                import json
                with open(manager.config_file, 'r', encoding='utf-8') as f:
                    raw = json.load(f)
                encrypted_pwd = raw.get('router_password', '')
                if encrypted_pwd != config.get('router_password', ''):
                    print(f"[OK] 密码已加密存储")
                else:
                    print(f"[WARN] 密码未加密")
            return True
        else:
            print("[WARN] 未配置路由器（首次运行时会显示配置向导）")
            return True

    except Exception as e:
        print(f"[FAIL] 路由器配置检查失败: {e}")
        return False

def test_6_cleanup_service_code():
    """测试6: 清理服务代码完整性"""
    print_header("测试6: 清理服务代码完整性")

    try:
        # 检查清理服务是否包含必要的类和方法
        with open('shutdown_cleanup_service.py', 'r', encoding='utf-8') as f:
            code = f.read()

        checks = [
            ('RouterAccountCleaner类', 'class RouterAccountCleaner'),
            ('clear_account方法', 'def clear_account'),
            ('SvcShutdown方法', 'def SvcShutdown'),
            ('关机清理', 'perform_shutdown_cleanup'),
        ]

        all_ok = True
        for name, pattern in checks:
            if pattern in code:
                print(f"[OK] {name}")
            else:
                print(f"[FAIL] {name} (缺失)")
                all_ok = False

        return all_ok

    except Exception as e:
        print(f"[FAIL] 代码检查失败: {e}")
        return False

def main():
    """主测试函数"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "宽带拨号工具 - 综合功能测试" + " " * 16 + "║")
    print("╚" + "═" * 58 + "╝")

    tests = [
        ("配置加密存储", test_1_config_encryption),
        ("浏览器检查", test_2_browser_check),
        ("清理服务状态", test_3_service_status),
        ("生成的exe文件", test_4_exe_files),
        ("路由器配置", test_5_router_config),
        ("清理服务代码", test_6_cleanup_service_code),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n[FAIL] 测试 '{name}' 出错: {e}")
            results.append((name, False))

    # 打印总结
    print_header("测试总结")

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "[OK] 通过" if result else "[FAIL] 失败"
        print(f"{status} - {name}")

    print("\n" + "=" * 60)
    print(f"测试结果: {passed}/{total} 通过")
    print("=" * 60)

    if passed == total:
        print("\n[SUCCESS] 所有测试通过！程序已准备就绪。")
        return 0
    else:
        print(f"\n[WARN]️ 有 {total - passed} 个测试失败，请检查。")
        return 1

if __name__ == '__main__':
    exit(main())
