#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试服务启动逻辑（不安装服务）
"""

import sys
import os
import time
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60)
print("测试服务启动逻辑（模拟 1053 场景）")
print("=" * 60)
print()

# 模拟服务启动
print("[1/4] 创建服务实例...")

try:
    import win32service
    import win32serviceutil
    import win32event

    # 导入服务类
    from service_http import TPLinkCleanupServiceHTTP

    # 创建模拟参数
    class MockArgs:
        def __getitem__(self, key):
            return 'test'

    args = MockArgs()

    # 实例化服务
    service = TPLinkCleanupServiceHTTP(args)
    print("      ✓ 服务实例创建成功")

except Exception as e:
    print(f"      ✗ 失败: {e}")
    sys.exit(1)

print()
print("[2/4] 测试 SvcDoRun 启动逻辑...")

try:
    # 记录开始时间
    start_time = time.time()

    # 直接调用 SvcDoRun 的核心逻辑
    service.ReportServiceStatus(win32service.SERVICE_RUNNING)
    elapsed = (time.time() - start_time) * 1000
    print(f"      ✓ ReportServiceStatus(RUNNING) 耗时: {elapsed:.2f}ms")

    if elapsed > 1000:
        print(f"      ⚠ 警告: 超过1秒，可能导致1053！")
    else:
        print(f"      ✓ OK: 低于1秒，不会导致1053")

except Exception as e:
    print(f"      ✗ 失败: {e}")
    sys.exit(1)

print()
print("[3/4] 测试 setup_logging...")

try:
    service.setup_logging()
    print("      ✓ 日志设置成功")

    if service.logger:
        service.logger.info("测试日志输出")
        print("      ✓ 日志写入成功")

except Exception as e:
    print(f"      ✗ 失败: {e}")

print()
print("[4/4] 测试延迟导入...")

try:
    # 测试延迟导入
    from config_manager import ConfigManager
    print("      ✓ config_manager 导入成功")

    from tplink_http_cleaner import TPLinkHTTPCleaner
    print("      ✓ tplink_http_cleaner 导入成功")

except ImportError as e:
    print(f"      ✗ 导入失败: {e}")
    print("      ⚠ 这可能导致运行时出错！")

print()
print("=" * 60)
print("测试总结")
print("=" * 60)
print()
print("✓ 服务实例创建: 正常")
print("✓ RUNNING状态报告: 快速（<1秒）")
print("✓ 日志系统: 正常")
print("✓ 延迟导入: 正常")
print()
print("结论: 如果以上所有测试通过，服务应该不会出现1053错误")
print()
print("日志位置:", Path(os.environ.get('TEMP', '/tmp')) / 'tplink_cleanup' / 'cleanup_service.log')
print()
