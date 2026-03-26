#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
服务安装脚本

安装CleanupService为Windows服务
"""

import sys
import os
import win32service
import win32serviceutil
import win32event
import win32con
import servicemanager
import time

# 获取脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))

# 导入服务类
sys.path.insert(0, script_dir)
from shutdown_cleanup_service import ShutdownCleanupService

def install_service():
    """安装服务"""
    try:
        print("正在安装TP-Link路由器账号清理服务...")

        # 检查是否已安装
        try:
            win32serviceutil.QueryServiceStatus(ShutdownCleanupService._svc_name_)
            print("服务已安装，正在卸载旧版本...")
            win32serviceutil.RemoveService(ShutdownCleanupService._svc_name_)
            time.sleep(2)
        except:
            pass

        # 使用Python解释器安装服务
        python_exe = sys.executable
        service_script = os.path.join(script_dir, 'shutdown_cleanup_service.py')

        print(f"Python解释器: {python_exe}")
        print(f"服务脚本: {service_script}")

        # 安装服务（使用当前Python环境）
        win32serviceutil.InstallService(
            None,  # 使用None表示使用当前Python环境
            ShutdownCleanupService._svc_name_,
            ShutdownCleanupService._svc_display_name_,
            startType=win32service.SERVICE_AUTO_START,
            description=ShutdownCleanupService._svc_description_
        )

        # 配置服务：接受关机控制码
        hscm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)
        hs = win32service.OpenService(hscm, ShutdownCleanupService._svc_name_, win32service.SERVICE_ALL_ACCESS)

        # 设置服务描述
        win32service.ChangeServiceConfig2(hs, win32service.SERVICE_CONFIG_DESCRIPTION, ShutdownCleanupService._svc_description_)

        # 设置Python路径（让pythonservice.exe能找到我们的模块）
        try:
            import win32con
            # 添加PythonPath到服务注册表
            python_path = f"{script_dir};{os.path.join(script_dir, 'dist')}"
            win32service.ChangeServiceConfig2(
                hs,
                win32service.SERVICE_CONFIG_DESCRIPTION,
                ShutdownCleanupService._svc_description_
            )

            # 设置注册表PythonPath
            import win32api
            import win32con
            key_path = f"SYSTEM\\CurrentControlSet\\Services\\{ShutdownCleanupService._svc_name_}\\Parameters"
            try:
                key = win32api.RegCreateKeyEx(win32con.HKEY_LOCAL_MACHINE, key_path, 0, None, win32con.REG_OPTION_NON_VOLATILE, win32con.KEY_ALL_ACCESS, None, 0)
                win32api.RegSetValueEx(key, "PythonPath", 0, win32con.REG_SZ, script_dir)
                win32api.RegCloseKey(key)
                print(f"设置Python路径: {script_dir}")
            except Exception as e:
                print(f"设置Python路径时出错（可忽略）: {e}")
        except Exception as e:
            print(f"配置服务路径时出错（可忽略）: {e}")

        # 设置接受关机控制
        try:
            info = win32service.QueryServiceConfig(hs)
            win32service.ChangeServiceConfig(
                hs,
                win32service.SERVICE_AUTO_START,
                win32service.SERVICE_ERROR_IGNORE,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                ShutdownCleanupService._svc_display_name_
            )
        except Exception as e:
            print(f"配置服务时出现警告（可忽略）: {e}")

        try:
            win32service.CloseServiceHandle(hs)
        except:
            pass
        try:
            win32service.CloseServiceManagerHandle(hscm)
        except:
            pass

        print("服务安装成功！")
        print(f"\n服务名称: {ShutdownCleanupService._svc_name_}")
        print(f"显示名称: {ShutdownCleanupService._svc_display_name_}")
        print("启动类型: 自动")
        print("功能: 关机时自动清除路由器账号密码")
        print("\n管理命令:")
        print(f"  启动服务: net start {ShutdownCleanupService._svc_name_}")
        print(f"  停止服务: net stop {ShutdownCleanupService._svc_name_}")
        print(f"  查看状态: sc query {ShutdownCleanupService._svc_name_}")

        # 询问是否立即启动
        try:
            response = input("\n是否立即启动服务？(y/n): ").lower()
            if response == 'y':
                print("\n正在启动服务...")
                import subprocess
                subprocess.run(['net', 'start', ShutdownCleanupService._svc_name_], check=False)
                print("\n服务已启动！")
        except:
            pass

    except Exception as e:
        print(f"安装失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == '__main__':
    install_service()
