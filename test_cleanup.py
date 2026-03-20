#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试路由器账号清理功能

此脚本用于测试清理服务是否能正常清除路由器账号密码。
"""

import sys
import os
from pathlib import Path

# 添加项目目录到Python路径
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

from shutdown_cleanup_service import RouterAccountCleaner

def test_cleanup():
    """测试清理功能"""
    print("=" * 60)
    print("TP-Link路由器账号清理测试")
    print("=" * 60)
    print()
    print("此测试将连接到路由器并清除账号密码。")
    print("请确保：")
    print("  1. 路由器IP地址为 192.168.1.1")
    print("  2. 路由器管理员密码为 Cdu@123")
    print("  3. 路由器中已配置了宽带账号密码")
    print()

    response = input("是否继续测试？(y/n): ").lower()
    if response != 'y':
        print("测试已取消")
        return

    print()
    print("正在初始化清理器...")

    try:
        # 添加site-packages路径
        site_packages = r"C:\Program Files\Python311\Lib\site-packages"
        if site_packages not in sys.path:
            sys.path.insert(0, site_packages)

        # 创建清理器实例（从配置文件读取）
        cleaner = RouterAccountCleaner()

        print("清理器初始化完成")
        print(f"路由器地址: {cleaner.router_ip}")
        print()
        print("开始清理测试...")
        print("=" * 60)

        # 执行清理
        success = cleaner.clear_account()

        print()
        print("=" * 60)
        if success:
            print("✅ 测试成功！账号密码已清除")
        else:
            print("❌ 测试失败！请检查日志")
        print("=" * 60)

        # 查看日志位置
        import tempfile
        log_dir = Path(tempfile.gettempdir()) / 'tplink_cleanup'
        log_file = log_dir / 'cleanup_service.log'

        print()
        print(f"日志文件位置: {log_file}")
        print()
        response = input("是否查看日志？(y/n): ").lower()
        if response == 'y':
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    print(f.read())
            else:
                print("日志文件不存在")

    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_cleanup()
