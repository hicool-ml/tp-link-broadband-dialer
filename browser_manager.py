#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
共享浏览器管理模块

负责管理 Playwright 浏览器的安装路径，让多个程序共享同一个浏览器。
"""

import os
import sys
import subprocess
from pathlib import Path


class BrowserManager:
    """浏览器管理器"""

    def __init__(self):
        # 共享浏览器安装路径
        if getattr(sys, 'frozen', False):
            # 打包后的环境，安装在程序目录
            self.install_dir = Path(sys.executable).parent
        else:
            # 开发环境，使用项目目录
            self.install_dir = Path(__file__).parent

        # 浏览器目录名称
        self.browser_dir_name = "chrome-win64"
        self.browser_path = self.install_dir / self.browser_dir_name
        self.chrome_exe = self.browser_path / "chrome.exe"

    def get_browser_path(self):
        """获取浏览器可执行文件路径"""
        # 首先检查默认路径
        if self.chrome_exe.exists():
            return str(self.chrome_exe)

        # 尝试其他可能的路径
        possible_paths = [
            self.install_dir / "chrome-win64" / "chrome.exe",
            self.install_dir / "_internal" / "chrome-win64" / "chrome.exe",
            self.install_dir / "ms-playwright" / "chromium-1208" / "chrome-win64" / "chrome.exe",
            self.install_dir / "chromium-mini" / "chrome.exe",
        ]

        # 如果是打包环境，尝试从sys._MEIPASS查找
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            meipass_path = Path(sys._MEIPASS)
            possible_paths.extend([
                meipass_path / "chrome-win64" / "chrome.exe",
                meipass_path / "_internal" / "chrome-win64" / "chrome.exe",
            ])

        for path in possible_paths:
            if path.exists():
                return str(path)

        # 如果还是找不到，打印调试信息
        print(f"DEBUG: install_dir={self.install_dir}")
        print(f"DEBUG: chrome_exe={self.chrome_exe}")
        print(f"DEBUG: chrome_exe exists={self.chrome_exe.exists()}")
        if hasattr(sys, '_MEIPASS'):
            print(f"DEBUG: _MEIPASS={sys._MEIPASS}")

        return None

    def is_browser_installed(self):
        """检查浏览器是否已安装"""
        return self.chrome_exe.exists()

    def install_browser(self):
        """安装 Playwright 浏览器"""
        print("正在安装 Playwright 浏览器...")
        print(f"安装位置: {self.browser_path}")

        try:
            # 使用 playwright 安装 chromium
            subprocess.run(
                [sys.executable, "-m", "playwright", "install", "chromium"],
                check=True,
                capture_output=True,
                text=True
            )

            # 检查是否安装成功
            if self.is_browser_installed():
                print("✓ 浏览器安装成功！")
                return True
            else:
                print("✗ 浏览器安装失败，未找到浏览器文件")
                return False

        except subprocess.CalledProcessError as e:
            print(f"✗ 安装失败: {e}")
            if e.stderr:
                print(f"错误信息: {e.stderr}")
            return False
        except Exception as e:
            print(f"✗ 安装出错: {e}")
            return False

    def check_and_install(self):
        """检查并安装浏览器（如果需要）"""
        if self.is_browser_installed():
            print(f"✓ 浏览器已安装: {self.chrome_exe}")
            return True

        print("浏览器未安装，正在准备安装...")

        # 询问是否安装
        try:
            response = input("是否现在安装浏览器？(y/n): ").lower()
            if response == 'y':
                return self.install_browser()
            else:
                print("浏览器未安装，程序可能无法正常运行")
                return False
        except:
            # 非交互模式，自动安装
            return self.install_browser()


def get_browser_executable():
    """便捷函数：获取浏览器可执行文件路径"""
    manager = BrowserManager()
    return manager.get_browser_path()


def ensure_browser_installed():
    """便捷函数：确保浏览器已安装"""
    manager = BrowserManager()
    if manager.is_browser_installed():
        return True
    return manager.check_and_install()


if __name__ == '__main__':
    # 测试代码
    print("=== Playwright 浏览器管理器 ===")

    manager = BrowserManager()

    print(f"安装目录: {manager.install_dir}")
    print(f"浏览器路径: {manager.chrome_exe}")
    print(f"已安装: {manager.is_browser_installed()}")

    if not manager.is_browser_installed():
        print("\n浏览器未安装，正在安装...")
        if manager.install_browser():
            print("\n安装成功！")
        else:
            print("\n安装失败！")
    else:
        browser_path = manager.get_browser_path()
        print(f"\n浏览器位置: {browser_path}")
