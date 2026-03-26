#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TP-Link 宽带拨号助手 - HTTP API 版本
不使用浏览器，直接通过 HTTP API 操作路由器
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import sys
import os
import subprocess
import ctypes
import atexit
import time
import logging
from pathlib import Path
import io

# ========== 修复Windows控制台编码问题 ==========
if sys.platform == 'win32':
    try:
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

# 导入配置管理模块
from config_manager import ConfigManager

# 导入HTTP清理模块
from tplink_http_cleaner import TPLinkHTTPCleaner

# 尝试导入PIL和pystray（可选依赖）
try:
    from PIL import Image, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None
    ImageDraw = None

try:
    import pystray
    from pystray import Menu, MenuItem
    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False
    pystray = None
    Menu = None
    MenuItem = None

# 检查托盘功能是否可用
TRAY_AVAILABLE = PYSTRAY_AVAILABLE and PIL_AVAILABLE
if not TRAY_AVAILABLE:
    missing = []
    if not PYSTRAY_AVAILABLE:
        missing.append("pystray")
    if not PIL_AVAILABLE:
        missing.append("PIL")
    print(f"警告: 未安装 {', '.join(missing)} 库，系统托盘功能不可用")
    print("如需系统托盘功能，请运行: pip install pystray pillow")


# ========== 核心：强制程序只使用内置资源 ==========
def get_resource_path(relative_path):
    """获取PyInstaller打包后的内置资源路径"""
    if hasattr(sys, '_MEIPASS'):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent
    return str(base_path / relative_path)


# ========== GUI 主类 ==========
class RouterLoginGUI:
    """路由器登录和清理 GUI（HTTP API 版本）"""

    def __init__(self, root):
        self.root = root
        self.root.title("宽带拨号")
        self.root.geometry("400x320")
        self.root.resizable(False, False)

        # 路由器配置
        self.config_manager = ConfigManager()
        config = self.config_manager.get_config()
        self.router_ip = config.get("router_ip", "192.168.1.1")
        self.router_password = config.get("router_password", "")

        # 保存的账号密码
        self.saved_account = ""
        self.saved_password = ""

        # HTTP 清理器
        self.cleaner = None

        # 关闭标志
        self.is_closing = False

        # 日志队列
        self.log_queue = queue.Queue()

        # 调试窗口
        self.debug_window = None
        self.debug_text = None

        # 系统托盘图标
        self.tray_icon = None

        # 托盘图标状态
        self.tray_icon_status = "offline"  # offline, online, connecting, error

        # 托盘图标双击检测
        self._last_click_time = 0
        self._click_count = 0

        # 创建界面
        self.create_widgets()

        # 启动日志处理
        self.process_log_queue()

        # 创建系统托盘图标（如果可用）
        if TRAY_AVAILABLE:
            self.create_tray_icon()

        # 欢迎信息
        self.log("=" * 50)
        self.log("TP-Link 宽带拨号助手 (HTTP API 版本)")
        self.log(f"路由器: {self.router_ip}")
        self.log("=" * 50)

    def create_widgets(self):
        """创建界面组件"""
        # 标题（双击标题可打开设置）
        title_label = tk.Label(
            self.root,
            text="宽带拨号",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=15)
        # 绑定双击标题打开设置
        title_label.bind("<Double-Button-1>", lambda e: self.show_settings())

        # 账号输入框
        account_frame = tk.Frame(self.root)
        account_frame.pack(pady=8, padx=30, fill=tk.X)

        tk.Label(account_frame, text="宽带账号:", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        self.account_entry = tk.Entry(account_frame, font=("Arial", 10), width=25)
        self.account_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        # 绑定回车键
        self.account_entry.bind("<Return>", lambda e: self.password_entry.focus())

        # 密码输入框
        password_frame = tk.Frame(self.root)
        password_frame.pack(pady=8, padx=30, fill=tk.X)

        tk.Label(password_frame, text="宽带密码:", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        self.password_entry = tk.Entry(password_frame, font=("Arial", 10), width=25, show="*")
        self.password_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        # 绑定回车键到连接
        self.password_entry.bind("<Return>", lambda e: self.start_connection())

        # 按钮区域
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=15)

        self.connect_button = tk.Button(
            button_frame,
            text="开始连接",
            command=self.start_connection,
            font=("Arial", 11, "bold"),
            bg="#4CAF50",
            fg="white",
            width=12,
            height=2,
            cursor="hand2"
        )
        self.connect_button.pack(side=tk.LEFT, padx=8)

        self.disconnect_button = tk.Button(
            button_frame,
            text="断开连接",
            command=self.disconnect_and_clear,
            font=("Arial", 11, "bold"),
            bg="#f44336",
            fg="white",
            width=12,
            height=2,
            cursor="hand2"
        )
        self.disconnect_button.pack(side=tk.LEFT, padx=8)

        # 提示文字
        hint_label = tk.Label(
            self.root,
            text="提示：使用完成后可点击断开按钮清除账号\n系统关机时后台服务会自动清理路由器账号",
            font=("Arial", 9, "bold"),
            fg="#0066CC",
            justify=tk.CENTER
        )
        hint_label.pack(pady=(5, 0))

        # 进度条（双击可查看日志）
        progress_frame = tk.Frame(self.root)
        progress_frame.pack(pady=15, padx=30, fill=tk.X)

        self.progress_label = tk.Label(
            progress_frame,
            text="",
            font=("Arial", 9)
        )
        self.progress_label.pack(anchor=tk.W)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            orient=tk.HORIZONTAL,
            mode='determinate',
            maximum=100
        )
        self.progress_bar.pack(fill=tk.X)

        # 绑定双击事件打开调试窗口
        self.progress_bar.bind("<Double-Button-1>", lambda e: self.toggle_debug_window())
        self.progress_label.bind("<Double-Button-1>", lambda e: self.toggle_debug_window())

        # 状态栏（左下角，双击查看日志）
        status_frame = tk.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_label = tk.Label(
            status_frame,
            text="就绪 | 双击进度条可查看运行日志",
            font=("Arial", 9),
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        # 绑定双击打开日志
        self.status_label.bind("<Double-Button-1>", lambda e: self.toggle_debug_window())

    def log(self, message, level="INFO"):
        """记录日志到队列"""
        self.log_queue.put((message, level))

    def process_log_queue(self):
        """处理日志队列"""
        try:
            while True:
                message, level = self.log_queue.get_nowait()

                # 显示到日志框（如果存在）
                if self.debug_text and self.debug_window and self.debug_window.winfo_exists():
                    self.debug_text.config(state=tk.NORMAL)
                    self.debug_text.insert(tk.END, message + "\n")
                    self.debug_text.see(tk.END)
                    self.debug_text.config(state=tk.DISABLED)

                # 同时输出到控制台
                print(message)
        except queue.Empty:
            pass

        # 100ms后再次检查
        self.root.after(100, self.process_log_queue)

    def clear_debug_log(self):
        """清空调试日志"""
        self.debug_text.config(state=tk.NORMAL)
        self.debug_text.delete(1.0, tk.END)
        self.debug_text.config(state=tk.DISABLED)

    def toggle_debug_window(self):
        """切换调试窗口显示/隐藏"""
        if self.debug_window is None or not self.debug_window.winfo_exists():
            self.create_debug_window()
        else:
            if self.debug_window.state() == 'withdrawn':
                self.debug_window.deiconify()
                self.debug_window.lift()
                self.debug_window.focus_force()
            else:
                self.debug_window.withdraw()

    def create_debug_window(self):
        """创建调试窗口"""
        if self.debug_window is None or not self.debug_window.winfo_exists():
            self.debug_window = tk.Toplevel(self.root)
            self.debug_window.title("运行日志 - 宽带拨号")
            self.debug_window.geometry("600x400")

            # 设置为非模态窗口
            self.debug_window.transient(self.root)

            # 调试信息显示区域
            debug_label = tk.Label(self.debug_window, text="运行日志:", font=("Arial", 10, "bold"))
            debug_label.pack(pady=(10, 5), padx=10, anchor=tk.W)

            self.debug_text = scrolledtext.ScrolledText(
                self.debug_window,
                height=20,
                font=("Consolas", 9),
                state=tk.DISABLED
            )
            self.debug_text.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

            # 清空按钮
            clear_button = tk.Button(
                self.debug_window,
                text="清空日志",
                command=self.clear_debug_log,
                font=("Arial", 9)
            )
            clear_button.pack(pady=5)

            # 关闭按钮
            close_button = tk.Button(
                self.debug_window,
                text="关闭",
                command=self.debug_window.destroy,
                font=("Arial", 9)
            )
            close_button.pack(pady=5)

            # 窗口关闭事件
            self.debug_window.protocol("WM_DELETE_WINDOW", lambda: self.debug_window.withdraw())

    def update_progress(self, value, text=None):
        """更新进度条"""
        self.progress_var.set(value)
        if text:
            self.progress_label.config(text=text)

    def update_status(self, status, color="black"):
        """更新状态栏"""
        self.status_label.config(text=f"{status} | 双击进度条可查看运行日志", fg=color)

    def update_button(self, button_name, state, text=None):
        """更新按钮状态"""
        if button_name == "connect":
            if text:
                self.connect_button.config(text=text, state=state)
            else:
                self.connect_button.config(state=state)
        elif button_name == "disconnect":
            if text:
                self.disconnect_button.config(text=text, state=state)
            else:
                self.disconnect_button.config(state=state)

    def create_tray_icon(self):
        """创建系统托盘图标"""
        if not TRAY_AVAILABLE:
            return

        try:
            # 创建图标 - 加载offline.ico作为默认图标
            icon_image = self.load_status_icon('offline')

            # 创建菜单
            menu = Menu(
                MenuItem('显示窗口', self.show_window),
                MenuItem('隐藏窗口', self.hide_to_tray),
                MenuItem('断开并清除', self.disconnect_from_tray),
                MenuItem('退出', self.quit_app),
            )

            # 创建托盘图标
            self.tray_icon = pystray.Icon(
                "宽带拨号",
                icon_image,
                "宽带拨号 - 未连接",
                menu
            )

            # 设置点击事件
            def on_click(icon, button, time):
                """处理托盘图标点击事件"""
                if button == pystray.MouseButton.LEFT:
                    # 双击检测
                    current_time = time
                    if current_time - self._last_click_time < 500:  # 500ms内双击
                        self._click_count += 1
                        if self._click_count == 2:
                            # 双击：显示窗口
                            self.show_window()
                            self._click_count = 0
                    else:
                        self._click_count = 1
                    self._last_click_time = current_time

            # 设置点击事件
            self.tray_icon.on_click = on_click

            # 在单独的线程中运行托盘图标
            def run_tray():
                self.tray_icon.run()

            tray_thread = threading.Thread(target=run_tray, daemon=True)
            tray_thread.start()

            self.log("✅ 系统托盘图标已创建")
            self.log("💡 双击托盘图标可显示窗口")

        except Exception as e:
            self.log(f"⚠️ 创建系统托盘图标失败: {e}")
            self.tray_icon = None

    def load_status_icon(self, status):
        """加载指定状态的图标文件

        Args:
            status: 状态名称

        Returns:
            PIL.Image对象或None
        """
        if not PIL_AVAILABLE:
            return None

        try:
            # 尝试从多个可能的路径加载图标
            icon_filename = f"{status}.ico"
            possible_paths = [
                # 当前目录
                icon_filename,
                # PyInstaller打包后的_internal目录
                os.path.join(sys._MEIPASS, '_internal', icon_filename) if getattr(sys, 'frozen', False) else None,
                os.path.join(sys._MEIPASS, icon_filename) if getattr(sys, 'frozen', False) else None,
                # 项目根目录（开发环境）
                os.path.join(Path(__file__).parent, icon_filename),
            ]

            for path in possible_paths:
                if path and os.path.exists(path):
                    try:
                        img = Image.open(path)
                        self.log(f"✅ 加载状态图标: {status} ({path})")
                        return img
                    except Exception as e:
                        self.log(f"⚠️ 加载图标失败 {path}: {e}")
                        continue

            # 如果找不到图标文件，使用默认图标
            self.log(f"⚠️ 未找到图标文件: {icon_filename}，使用默认图标")
            return self.create_default_icon()

        except Exception as e:
            self.log(f"⚠️ 加载状态图标时出错: {e}")
            return self.create_default_icon()

    def create_default_icon(self):
        """创建默认的网络图标"""
        if not PIL_AVAILABLE:
            return None

        # 创建一个64x64的图标
        img = Image.new('RGB', (64, 64), (0, 120, 215))  # Windows蓝色背景
        draw = ImageDraw.Draw(img)

        # 绘制网络图标（两个电脑连接的形状）
        # 左边电脑
        draw.rectangle([4, 24, 20, 40], fill='white')
        draw.rectangle([6, 20, 18, 24], fill='white')

        # 右边电脑
        draw.rectangle([44, 24, 60, 40], fill='white')
        draw.rectangle([46, 20, 58, 24], fill='white')

        # 连接线
        draw.line([20, 32, 44, 32], fill='white', width=2)

        # 中间节点
        draw.ellipse([28, 28, 36, 36], fill='white')

        return img

    def create_status_icon(self, status):
        """创建指定状态的图标"""
        if not PIL_AVAILABLE:
            return None

        # 颜色映射
        colors = {
            'offline': (117, 117, 117),  # 灰色 #757575
            'online': (76, 175, 80),     # 绿色 #4CAF50
            'connecting': (33, 150, 243),  # 蓝色 #2196F3
            'error': (244, 67, 54)       # 红色 #f44336
        }

        color = colors.get(status, (33, 150, 243))

        # 创建一个64x64的图标
        img = Image.new('RGB', (64, 64), color)
        draw = ImageDraw.Draw(img)

        # 绘制网络图标（两个电脑连接的形状）
        # 左边电脑
        draw.rectangle([4, 24, 20, 40], fill='white')
        draw.rectangle([6, 20, 18, 24], fill='white')

        # 右边电脑
        draw.rectangle([44, 24, 60, 40], fill='white')
        draw.rectangle([46, 20, 58, 24], fill='white')

        # 连接线
        draw.line([20, 32, 44, 32], fill='white', width=2)

        # 中间节点
        draw.ellipse([28, 28, 36, 36], fill='white')

        return img

    def update_tray_icon(self, status, ip_address=None):
        """更新托盘图标

        Args:
            status: 状态名称
            ip_address: IP地址（可选，用于显示）
        """
        if not TRAY_AVAILABLE or not self.tray_icon:
            return

        try:
            # 加载对应状态的图标文件
            new_icon = self.load_status_icon(status)
            if new_icon:
                # 更新托盘图标
                self.tray_icon.icon = new_icon

                # 更新托盘提示文字
                status_texts = {
                    'offline': '宽带拨号 - 未连接',
                    'online': '宽带拨号 - 已连接',
                    'connecting': '宽带拨号 - 连接中...',
                    'error': '宽带拨号 - 连接失败'
                }

                if status == 'online' and ip_address:
                    self.tray_icon.title = f'宽带拨号 - 已连接 ({ip_address})'
                else:
                    self.tray_icon.title = status_texts.get(status, '宽带拨号')

                self.tray_icon_status = status
                self.log(f"✅ 托盘图标已更新: {status}")
        except Exception as e:
            self.log(f"⚠️ 更新托盘图标失败: {e}")

    def show_window(self, icon=None, item=None):
        """显示窗口"""
        self.root.deiconify()  # 显示窗口
        self.root.lift()  # 提升到前台
        self.root.focus_force()  # 强制获取焦点

    def hide_to_tray(self, icon=None, item=None):
        """隐藏窗口到系统托盘"""
        if self.tray_icon and TRAY_AVAILABLE:
            self.root.withdraw()  # 隐藏窗口
            self.log("窗口已隐藏到系统托盘")
            self.log("双击托盘图标可重新显示窗口")

    def disconnect_from_tray(self, icon=None, item=None):
        """从托盘菜单断开连接"""
        self.show_window()
        self.disconnect_and_clear()

    def quit_app(self, icon=None, item=None):
        """从托盘菜单退出应用"""
        # 如果有保存的账号，需要先断开并清除
        if self.saved_account:
            # 防止重复触发关闭事件
            if self.is_closing:
                return

            # 设置关闭标志
            self.is_closing = True

            # 停止进度条（如果正在运行）
            self.stop_progress()

            self.log("=" * 50)
            self.log("检测到退出请求，自动执行断开并清除...")
            self.log("=" * 50)

            # 强制更新UI
            if self.debug_text:
                self.debug_text.update()
            self.root.update_idletasks()

            # 创建断开完成的标志
            disconnect_complete = threading.Event()

            # 包装断开函数，完成后设置标志
            def disconnect_with_callback():
                try:
                    self.run_disconnect()
                finally:
                    disconnect_complete.set()

            # 在新线程中执行断开，避免阻塞GUI关闭
            thread = threading.Thread(target=disconnect_with_callback)
            thread.daemon = True
            thread.start()

            # 轮询等待断开完成（最多10秒）
            def wait_disconnect():
                if disconnect_complete.is_set():
                    # 断开成功，停止托盘图标并退出
                    self.log("[OK] 断开并清除成功，退出程序...")
                    if self.tray_icon:
                        self.tray_icon.stop()
                    self.root.after(50, self.root.destroy)
                else:
                    # 继续等待，使用after避免阻塞
                    self.root.after(100, wait_disconnect)

            # 开始等待
            self.root.after(100, wait_disconnect)
        else:
            # 没有保存的账号，直接退出
            if self.tray_icon:
                self.tray_icon.stop()
            self.root.destroy()

    def start_connection(self):
        """开始连接"""
        broadband_user = self.account_entry.get().strip()
        broadband_pass = self.password_entry.get().strip()

        if not broadband_user or not broadband_pass:
            messagebox.showwarning("提示", "请输入宽带账号和密码")
            return

        # 保存账号密码
        self.saved_account = broadband_user
        self.saved_password = broadband_pass

        # 禁用按钮
        self.update_button("connect", tk.DISABLED, "正在连接...")
        self.update_button("disconnect", tk.DISABLED)

        # 在新线程中执行连接
        thread = threading.Thread(target=self.run_connection, args=(broadband_user, broadband_pass))
        thread.daemon = True
        thread.start()

        # 更新托盘图标为"连接中"
        self.update_tray_icon("connecting")

    def run_connection(self, broadband_user, broadband_pass):
        """执行连接逻辑"""
        connection_success = False
        ip_address = None  # 声明IP地址变量
        try:
            self.log("=" * 50)
            self.log("开始执行路由器连接流程...")
            self.log(f"账号: {broadband_user}")
            self.log(f"密码: {'*' * len(broadband_pass)}")
            self.log("=" * 50)

            # 更新进度：初始化
            self.update_progress(10, "正在连接路由器...")
            self.update_status("正在连接...", "#4CAF50")

            # 创建 HTTP 清理器
            self.cleaner = TPLinkHTTPCleaner(self.router_ip, self.router_password)

            # 替换日志方法
            self.cleaner._log = lambda msg: self.log(msg)

            # 1. 登录
            self.update_progress(20, "正在登录...")
            if not self.cleaner.login():
                self.log("[ERROR] 登录失败")
                self.update_status("登录失败", "red")
                return

            # 2. 设置随机MAC地址
            self.update_progress(30, "正在设置随机MAC地址...")
            if not self.cleaner.set_mac_address():
                self.log("[ERROR] 设置MAC地址失败")
                self.update_status("设置失败", "red")
                return

            # 3. 设置PPPoE账号密码
            self.update_progress(50, "正在设置账号密码...")
            if not self.cleaner.set_pppoe_account(broadband_user, broadband_pass):
                self.log("[ERROR] 设置账号密码失败")
                self.update_status("设置失败", "red")
                return

            # 4. 连接PPPoE
            self.update_progress(70, "正在拨号连接...")
            if not self.cleaner.connect_pppoe():
                self.log("[ERROR] 连接失败")
                self.update_status("连接失败", "red")
                return

            # 5. 等待连接建立
            self.update_progress(80, "正在等待IP分配...")
            self.log("[INFO] 等待IP地址分配（15秒）...")
            time.sleep(15)

            # 6. 检查连接状态
            self.update_progress(90, "正在验证连接...")
            self.log("[INFO] 正在检查连接状态...")
            wan_status = self.cleaner.get_wan_status()

            if wan_status:
                ip_address = wan_status.get("network", {}).get("wan_status", {}).get("ipaddr", "")
                self.log(f"[INFO] WAN IP地址: {ip_address}")

                if ip_address and ip_address != "0.0.0.0" and ip_address != "":
                    self.log("=" * 50)
                    self.log("[SUCCESS] 连接成功！")
                    self.log(f"已获取IP地址: {ip_address}")
                    self.log("=" * 50)
                    connection_success = True
                    self.update_status(f"已连接 IP: {ip_address}", "#4CAF50")
                    self.update_progress(100, "连接成功！")
                else:
                    self.log("[WARNING] 未获取到有效IP地址")
                    self.update_status("连接失败", "orange")
                    ip_address = None  # 重置IP地址
            else:
                self.log("[WARNING] 无法获取连接状态")
                self.update_status("状态未知", "orange")

        except Exception as e:
            self.log(f"[ERROR] 连接时发生错误: {e}")
            import traceback
            self.log(traceback.format_exc())
            connection_success = False

        # 恢复按钮状态
        self.log("[INFO] 正在恢复按钮状态...")
        if connection_success:
            self.update_button("disconnect", tk.NORMAL, "断开连接")
            self.update_button("connect", tk.DISABLED, "已连接")

            # 更新托盘图标为"在线"（带IP地址）
            self.update_tray_icon("online", ip_address)
        else:
            self.update_button("disconnect", tk.NORMAL, "断开连接")
            self.update_button("connect", tk.NORMAL, "开始连接")

            # 更新托盘图标为"错误"（连接失败）
            self.update_tray_icon("error")
        self.stop_progress()

        return connection_success

    def disconnect_and_clear(self):
        """断开并清除账号密码"""
        # 禁用按钮
        self.update_button("connect", tk.DISABLED)
        self.update_button("disconnect", tk.DISABLED, "正在断开...")

        # 在新线程中执行断开操作
        thread = threading.Thread(target=self.run_disconnect)
        thread.daemon = True
        thread.start()

        # 更新托盘图标为"连接中"
        self.update_tray_icon("connecting")

    def run_disconnect(self):
        """执行断开逻辑"""
        disconnect_success = False
        try:
            self.log("=" * 50)
            self.log("开始执行路由器账号清理...")
            self.log("=" * 50)

            # 更新进度：初始化
            self.update_progress(10, "正在连接路由器...")
            self.update_status("正在清理...", "#FF9800")

            # 创建 HTTP 清理器
            self.cleaner = TPLinkHTTPCleaner(self.router_ip, self.router_password)

            # 替换日志方法
            self.cleaner._log = lambda msg: self.log(msg)

            # 执行清理流程
            disconnect_success = self.cleaner.run_cleanup()

            if disconnect_success:
                self.log("[SUCCESS] 清理完成！")
                self.update_status("已断开并清除", "#4CAF50")
                self.update_progress(100, "完成！")
            else:
                self.log("[ERROR] 清理失败")
                self.update_status("操作失败", "red")

        except Exception as e:
            self.log(f"[ERROR] 断开时发生错误: {e}")
            import traceback
            self.log(traceback.format_exc())
            disconnect_success = False

        # 恢复按钮状态
        self.log("[INFO] 正在恢复按钮状态...")
        self.update_button("connect", tk.NORMAL, "开始连接")
        self.update_button("disconnect", tk.NORMAL, "断开连接")

        # 更新托盘图标为"离线"（断开成功）
        if disconnect_success:
            self.update_tray_icon("offline")

        self.stop_progress()

        # 清除保存的账号密码
        self.saved_account = ""
        self.saved_password = ""

        return disconnect_success

    def stop_progress(self):
        """停止进度条"""
        self.progress_var.set(0)
        self.progress_label.config(text="")

    def show_settings(self):
        """显示设置对话框（双击标题触发）"""
        dialog = tk.Toplevel(self.root)
        dialog.title("路由器设置")
        dialog.geometry("500x500")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        # 居中显示
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (500 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (500 // 2)
        dialog.geometry(f"+{x}+{y}")

        # 标题
        title_label = tk.Label(dialog, text="路由器配置", font=("Arial", 14, "bold"))
        title_label.pack(pady=15)

        # 当前配置
        current_config = self.config_manager.get_config()

        # 路由器IP
        ip_frame = tk.Frame(dialog)
        ip_frame.pack(pady=10, padx=30, fill=tk.X)
        tk.Label(ip_frame, text="路由器IP地址:", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        ip_entry = tk.Entry(ip_frame, font=("Arial", 10), width=20)
        ip_entry.insert(0, current_config.get('router_ip', '192.168.1.1'))
        ip_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # 路由器密码
        password_frame = tk.Frame(dialog)
        password_frame.pack(pady=10, padx=30, fill=tk.X)
        tk.Label(password_frame, text="路由器管理密码:", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        password_entry = tk.Entry(password_frame, font=("Arial", 10), width=20, show="*")
        password_entry.insert(0, current_config.get('router_password', ''))
        password_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # 分隔线
        separator_frame = tk.Frame(dialog, height=2, bg="#CCCCCC")
        separator_frame.pack(pady=10, padx=30, fill=tk.X)

        # 说明文字
        info_label = tk.Label(
            dialog,
            text="提示：程序将自动使用随机MAC地址",
            font=("Arial", 9),
            fg="#666666"
        )
        info_label.pack(pady=10)

        # 错误提示
        error_label = tk.Label(dialog, text="", font=("Arial", 9), fg="red")
        error_label.pack(pady=5)

        def validate_and_save():
            router_ip = ip_entry.get().strip()
            router_password = password_entry.get().strip()

            # 验证IP
            parts = router_ip.split('.')
            if len(parts) != 4:
                error_label.config(text="IP地址格式不正确")
                return
            try:
                for part in parts:
                    num = int(part)
                    if num < 0 or num > 255:
                        error_label.config(text="IP地址格式不正确")
                        return
            except:
                error_label.config(text="IP地址格式不正确")
                return

            if not router_password:
                error_label.config(text="请输入路由器管理密码")
                return

            # 保存配置
            new_config = {
                'router_ip': router_ip,
                'router_password': router_password,
                'version': '1.0'
            }

            if self.config_manager.save_config(new_config):
                # 更新配置
                self.router_ip = router_ip
                self.router_password = router_password
                messagebox.showinfo("成功", "配置保存成功！", parent=dialog)
                dialog.destroy()
            else:
                error_label.config(text="保存配置失败")

        # 按钮
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="保存", command=validate_and_save, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="取消", command=dialog.destroy, width=10).pack(side=tk.LEFT, padx=5)


# ========== 配置向导 ==========
def show_config_wizard():
    """显示配置向导（首次运行时）"""
    wizard_root = tk.Tk()
    wizard_root.title("路由器配置向导")
    wizard_root.geometry("500x400")
    wizard_root.resizable(False, False)

    # 居中显示
    wizard_root.update_idletasks()
    width = wizard_root.winfo_width()
    height = wizard_root.winfo_height()
    x = (wizard_root.winfo_screenwidth() // 2) - (width // 2)
    y = (wizard_root.winfo_screenheight() // 2) - (height // 2)
    wizard_root.geometry(f'{width}x{height}+{x}+{y}')

    # 标题
    title_label = tk.Label(
        wizard_root,
        text="欢迎使用宽带拨号工具",
        font=("Arial", 18, "bold"),
        fg="#333333"
    )
    title_label.pack(pady=(20, 10))

    # 副标题
    subtitle_label = tk.Label(
        wizard_root,
        text="首次使用需要配置路由器信息",
        font=("Arial", 11),
        fg="#666666"
    )
    subtitle_label.pack(pady=(0, 15))

    # 说明框
    info_frame = tk.Frame(wizard_root, bg="#E3F2FD", bd=1, relief=tk.SOLID)
    info_frame.pack(pady=10, padx=40, fill=tk.X)

    info_label = tk.Label(
        info_frame,
        text="配置说明\n\n程序需要在关机时自动清理路由器账号\n请输入路由器的管理地址和管理员密码\n此信息将加密保存在本地",
        font=("Arial", 9),
        bg="#E3F2FD",
        fg="#1565C0",
        justify=tk.LEFT,
        padx=15,
        pady=10
    )
    info_label.pack(fill=tk.BOTH, expand=True)

    # 路由器IP输入框
    ip_frame = tk.Frame(wizard_root)
    ip_frame.pack(pady=10, padx=40, fill=tk.X)

    tk.Label(ip_frame, text="路由器IP地址：", font=("Arial", 10, "bold"), width=15, anchor=tk.W).pack(side=tk.LEFT, padx=5)
    ip_entry = tk.Entry(ip_frame, font=("Arial", 10), width=25)
    ip_entry.insert(0, "192.168.1.1")
    ip_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

    # 路由器密码输入框
    password_frame = tk.Frame(wizard_root)
    password_frame.pack(pady=10, padx=40, fill=tk.X)

    tk.Label(password_frame, text="路由器管理密码：", font=("Arial", 10, "bold"), width=15, anchor=tk.W).pack(side=tk.LEFT, padx=5)
    password_entry = tk.Entry(password_frame, font=("Arial", 10), width=25, show="●")
    password_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

    # 说明文字
    info_frame = tk.Frame(wizard_root)
    info_frame.pack(pady=10, padx=40, fill=tk.X)

    info_label = tk.Label(
        info_frame,
        text="说明：程序将自动使用随机MAC地址连接网络",
        font=("Arial", 9),
        fg="#666666"
    )
    info_label.pack()

    # 状态提示
    status_label = tk.Label(
        wizard_root,
        text="",
        font=("Arial", 9),
        fg="#4CAF50",
        wraplength=400
    )
    status_label.pack(pady=5)

    # 错误提示
    error_label = tk.Label(
        wizard_root,
        text="",
        font=("Arial", 9),
        fg="red",
        wraplength=400
    )
    error_label.pack(pady=5)

    # 结果存储
    result = {'config': None, 'save': False}

    def validate_and_save():
        """验证并保存配置"""
        # 清除之前的提示
        error_label.config(text="")
        status_label.config(text="")

        router_ip = ip_entry.get().strip()
        router_password = password_entry.get().strip()

        # 验证IP
        parts = router_ip.split('.')
        if len(parts) != 4:
            error_label.config(text="❌ IP地址格式不正确，应为：xxx.xxx.xxx.xxx")
            return

        try:
            for part in parts:
                num = int(part)
                if num < 0 or num > 255:
                    error_label.config(text="❌ IP地址格式不正确，每个数字应在0-255之间")
                    return
        except:
            error_label.config(text="❌ IP地址格式不正确，只能包含数字和点号")
            return

        # 验证密码
        if not router_password:
            error_label.config(text="❌ 请输入路由器管理密码")
            password_entry.focus()
            return

        # 显示保存中状态
        status_label.config(text="💾 正在保存配置...")
        wizard_root.update()

        # 保存配置
        config_manager = ConfigManager()
        config = {
            'router_ip': router_ip,
            'router_password': router_password,
            'version': '1.0'
        }

        if config_manager.save_config(config):
            result['config'] = config
            result['save'] = True

            # 显示成功消息
            status_label.config(text="✅ 配置保存成功！正在启动程序...", fg="#4CAF50")
            wizard_root.update()

            # 延迟关闭
            wizard_root.after(1000, wizard_root.destroy)
        else:
            error_label.config(text="❌ 保存配置失败，请检查是否有写入权限")
            status_label.config(text="")

    def on_exit():
        """退出程序"""
        if result['save']:
            wizard_root.destroy()
        else:
            if messagebox.askyesno("确认退出", "未保存配置，程序将无法使用。\n\n确定要退出吗？"):
                wizard_root.destroy()

    # 绑定回车键
    wizard_root.bind('<Return>', lambda e: validate_and_save())

    # 按钮区域
    button_frame = tk.Frame(wizard_root)
    button_frame.pack(pady=20)

    save_button = tk.Button(
        button_frame,
        text="✓ 保存并启动",
        command=validate_and_save,
        font=("Arial", 11, "bold"),
        bg="#4CAF50",
        fg="white",
        width=18,
        height=2,
        cursor="hand2"
    )
    save_button.pack(side=tk.LEFT, padx=8)

    cancel_button = tk.Button(
        button_frame,
        text="✗ 退出",
        command=on_exit,
        font=("Arial", 10),
        bg="#757575",
        fg="white",
        width=12,
        height=2,
        cursor="hand2"
    )
    cancel_button.pack(side=tk.LEFT, padx=8)

    # 底部提示
    footer_label = tk.Label(
        wizard_root,
        text="提示：配置可在程序设置中随时修改（双击标题打开设置）",
        font=("Arial", 8),
        fg="#999999"
    )
    footer_label.pack(side=tk.BOTTOM, pady=10)

    # 设置焦点
    ip_entry.focus()
    ip_entry.select_range(0, tk.END)

    wizard_root.mainloop()
    return result


# ========== 单实例检查 ==========
class SingleInstanceChecker:
    """单实例检查器"""

    def __init__(self):
        self.mutex = None
        self.is_running = False

        if sys.platform == 'win32':
            try:
                # 创建互斥对象
                self.mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "TP-Link_Broadband_Dialer_Single_Instance")
                # 检查是否已存在
                if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
                    self.is_running = True
            except:
                pass

    def is_already_running(self):
        """检查是否已有实例在运行"""
        return self.is_running

    def __del__(self):
        """释放互斥对象"""
        if self.mutex:
            try:
                ctypes.windll.kernel32.CloseHandle(self.mutex)
            except:
                pass


# ========== 主函数 ==========
def main():
    """主函数"""

    # 检查是否已配置
    config_manager = ConfigManager()
    if not config_manager.is_configured():
        # 首次运行，显示配置向导
        result = show_config_wizard()
        if not result or not result['save']:
            # 用户未保存配置，退出
            sys.exit(0)

    # 单实例检查
    single_instance = SingleInstanceChecker()
    if single_instance.is_already_running():
        print("程序已在运行中！")
        messagebox.showwarning("警告", "程序已在运行中！")
        return

    # 创建主窗口
    root = tk.Tk()
    app = RouterLoginGUI(root)

    # 窗口关闭事件
    def on_closing():
        # 如果有托盘图标，隐藏到托盘
        if TRAY_AVAILABLE and app.tray_icon:
            app.hide_to_tray()
            return

        # 直接关闭窗口
        if app.saved_account:
            if messagebox.askyesno("确认退出", "检测到已保存的宽带账号。\n\n确定要退出吗？"):
                # 停止托盘图标
                if app.tray_icon:
                    app.tray_icon.stop()
                root.destroy()
        else:
            # 停止托盘图标
            if app.tray_icon:
                app.tray_icon.stop()
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # 监听窗口最小化事件
    def on_iconify():
        # 如果窗口被最小化，隐藏到托盘
        if root.state() == 'iconic':
            if TRAY_AVAILABLE and app.tray_icon:
                # 延迟一小段时间后隐藏窗口，确保最小化动画完成
                root.after(100, app.hide_to_tray)
            else:
                app.log("提示: 系统托盘功能不可用，窗口保持可见")

    root.bind('<Unmap>', lambda e: on_iconify())

    # 运行主循环
    root.mainloop()


if __name__ == '__main__':
    main()
