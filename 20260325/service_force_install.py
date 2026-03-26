#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
强制清理并重新安装服务
"""

import win32service
import win32serviceutil
import win32api
import win32con
import winerror

try:
    import win32service
    import win32serviceutil

    service_name = "TPLinkShutdownCleanup"

    print("=" * 60)
    print("强制清理服务")
    print("=" * 60)
    print()

    # 尝试打开服务
    try:
        hscm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)
        print("[OK] 已连接到服务管理器")

        # 尝试打开服务
        try:
            hs = win32service.OpenService(hscm, service_name, win32service.SERVICE_ALL_ACCESS)
            print("[OK] 已打开服务")

            # 尝试删除服务
            try:
                win32service.DeleteService(hs)
                print("[OK] 服务删除标记已设置")
                win32service.CloseServiceHandle(hs)
            except Exception as e:
                print(f"[WARN] 删除服务失败: {e}")
                win32service.CloseServiceHandle(hs)

        except win32service.error as e:
            if e.winerror == winerror.ERROR_SERVICE_DOES_NOT_EXIST:
                print("[OK] 服务不存在（已清理）")
            else:
                print(f"[ERROR] 打开服务失败: {e}")

        win32service.CloseServiceHandle(hscm)

    except Exception as e:
        print(f"[ERROR] 连接服务管理器失败: {e}")

    print()
    print("=" * 60)
    print("结论")
    print("=" * 60)
    print()
    print("服务已被标记为删除，系统需要重启才能完全清除。")
    print()
    print("解决方案：")
    print("  1. 重启电脑（推荐）")
    print("  2. 重启后运行: dist\\TPLinkCleanupService.exe install")
    print()
    print("或者使用临时服务名测试：")
    print("  1. 修改 service_http.py 中的 _svc_name_")
    print("  2. 改为 'TPLinkCleanupTest'")
    print("  3. 重新编译并安装")
    print()

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
