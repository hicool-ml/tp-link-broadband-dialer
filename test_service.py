#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TP-Link宽带拨号服务 - 测试脚本

用于测试服务是否正常工作。
"""

import sys
import os
import time
import subprocess
from pathlib import Path


def test_service_installation():
    """测试服务是否已安装"""
    print("=" * 60)
    print("测试1: 检查服务安装状态")
    print("=" * 60)
    
    try:
        import win32service
        import win32serviceutil
        
        # 尝试查询服务状态
        status = win32serviceutil.QueryServiceStatus("TPLinkBroadbandDialer")
        
        state_map = {
            win32service.SERVICE_STOPPED: "已停止",
            win32service.SERVICE_START_PENDING: "正在启动",
            win32service.SERVICE_STOP_PENDING: "正在停止",
            win32service.SERVICE_RUNNING: "正在运行",
            win32service.SERVICE_CONTINUE_PENDING: "正在继续",
            win32service.SERVICE_PAUSE_PENDING: "正在暂停",
            win32service.SERVICE_PAUSED: "已暂停",
        }
        
        state = state_map.get(status[1], "未知状态")
        print(f"✓ 服务已安装")
        print(f"  当前状态: {state}")
        
        return True, status[1]
        
    except Exception as e:
        print(f"✗ 服务未安装")
        print(f"  错误信息: {e}")
        return False, None


def test_service_running(status):
    """测试服务是否正在运行"""
    print("\n" + "=" * 60)
    print("测试2: 检查服务运行状态")
    print("=" * 60)
    
    if status is None:
        print("✗ 服务未安装，无法测试运行状态")
        return False
    
    import win32service
    
    if status == win32service.SERVICE_RUNNING:
        print("✓ 服务正在运行")
        return True
    else:
        print("✗ 服务未运行")
        print("  提示: 使用 'net start TPLinkBroadbandDialer' 启动服务")
        return False


def test_service_log():
    """测试服务日志"""
    print("\n" + "=" * 60)
    print("测试3: 检查服务日志")
    print("=" * 60)
    
    log_dir = Path(os.environ.get('TEMP', '/tmp')) / 'tplink_dialer'
    log_file = log_dir / 'service.log'
    
    if log_file.exists():
        print(f"✓ 日志文件存在")
        print(f"  路径: {log_file}")
        print(f"  大小: {log_file.stat().st_size} 字节")
        
        # 读取最后几行
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    print(f"  总行数: {len(lines)}")
                    print("\n  最后10行日志:")
                    for line in lines[-10:]:
                        print(f"    {line.strip()}")
                else:
                    print("  ⚠ 日志文件为空")
        except Exception as e:
            print(f"  ⚠ 读取日志文件时出错: {e}")
        
        return True
    else:
        print(f"✗ 日志文件不存在")
        print(f"  预期路径: {log_file}")
        print(f"  提示: 服务运行后会自动创建日志文件")
        return False


def test_shutdown_capability():
    """测试关机拦截能力"""
    print("\n" + "=" * 60)
    print("测试4: 检查关机拦截能力")
    print("=" * 60)
    
    try:
        import win32service
        import win32serviceutil
        
        # 查询服务配置
        service_manager = win32service.OpenSCManager(
            None, None, win32service.SC_MANAGER_CONNECT
        )
        
        service = win32service.OpenService(
            service_manager,
            "TPLinkBroadbandDialer",
            win32service.SERVICE_QUERY_CONFIG
        )
        
        config = win32service.QueryServiceConfig(service)
        
        win32service.CloseServiceHandle(service)
        win32service.CloseServiceManager(service_manager)
        
        print("✓ 服务配置正常")
        print(f"  启动类型: {config['dwStartType']}")
        print(f"  服务类型: {config['dwServiceType']}")
        
        # 检查是否接受关机控制
        if config['dwControlsAccepted'] & win32service.SERVICE_ACCEPT_SHUTDOWN:
            print("  ✓ 服务接受关机控制")
        else:
            print("  ✗ 服务不接受关机控制")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ 无法查询服务配置")
        print(f"  错误信息: {e}")
        return False


def test_browser():
    """测试浏览器"""
    print("\n" + "=" * 60)
    print("测试5: 检查浏览器")
    print("=" * 60)
    
    browser_paths = [
        "chrome-win64/chrome.exe",
        "chromium-mini/chrome.exe",
        "ms-playwright/chromium_headless_shell-1208/chrome-headless-shell-win64/chrome.exe",
    ]
    
    for browser_path in browser_paths:
        if os.path.exists(browser_path):
            print(f"✓ 找到浏览器: {browser_path}")
            return True
    
    print("✗ 未找到浏览器")
    print("  提示: 请确保已下载浏览器或运行 prepare_browser.bat")
    return False


def test_dependencies():
    """测试依赖项"""
    print("\n" + "=" * 60)
    print("测试6: 检查依赖项")
    print("=" * 60)
    
    dependencies = [
        ("tkinter", "GUI库"),
        ("win32service", "Windows服务API"),
        ("win32serviceutil", "Windows服务工具"),
        ("playwright", "浏览器自动化"),
    ]
    
    all_ok = True
    for module, description in dependencies:
        try:
            __import__(module)
            print(f"✓ {description} ({module})")
        except ImportError:
            print(f"✗ {description} ({module}) 未安装")
            all_ok = False
    
    return all_ok


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("TP-Link宽带拨号服务 - 测试脚本")
    print("=" * 60)
    print()
    
    results = []
    
    # 测试1: 服务安装状态
    installed, status = test_service_installation()
    results.append(("服务安装", installed))
    
    # 测试2: 服务运行状态
    if installed:
        running = test_service_running(status)
        results.append(("服务运行", running))
    else:
        results.append(("服务运行", False))
    
    # 测试3: 服务日志
    log_ok = test_service_log()
    results.append(("服务日志", log_ok))
    
    # 测试4: 关机拦截能力
    if installed:
        shutdown_ok = test_shutdown_capability()
        results.append(("关机拦截", shutdown_ok))
    else:
        results.append(("关机拦截", False))
    
    # 测试5: 浏览器
    browser_ok = test_browser()
    results.append(("浏览器", browser_ok))
    
    # 测试6: 依赖项
    deps_ok = test_dependencies()
    results.append(("依赖项", deps_ok))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name:.<30} {status}")
    
    total = len(results)
    passed = sum(1 for _, result in results if result)
    
    print()
    print(f"总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！服务可以正常工作。")
        return 0
    else:
        print("\n⚠ 部分测试失败，请检查上述错误信息。")
        return 1


if __name__ == '__main__':
    sys.exit(main())
