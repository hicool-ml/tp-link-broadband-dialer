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
        self.root.title("TP-Link 宽带拨号助手")

        # 窗口居中
        window_width = 600
        window_height = 500
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # 禁止调整窗口大小
        self.root.resizable(False, False)

        # 设置窗口图标
        try:
            icon_path = get_resource_path("app.ico")
            if Path(icon_path).exists():
                self.root.iconbitmap(icon_path)
        except:
            pass

        # 日志队列（用于线程间通信）
        self.log_queue = queue.Queue()

        # 保存的账号密码
        self.saved_account = ""
        self.saved_password = ""

        # 加载配置
        self.config_manager = ConfigManager()
        config = self.config_manager.get_config()
        self.router_ip = config.get("router_ip", "192.168.1.1")
        self.router_password = config.get("router_password", "")

        # HTTP 清理器
        self.cleaner = None

        # 关闭标志
        self.is_closing = False

        # 初始化界面
        self.setup_ui()

        # 启动日志处理
        self.process_log_queue()

        # 显示欢迎信息
        self.log("=" * 60)
        self.log("TP-Link 宽带拨号助手 (HTTP API 版本)")
        self.log("=" * 60)
        self.log(f"路由器IP: {self.router_ip}")
        self.log(f"版本特点: 不使用浏览器，直接通过HTTP API操作")
        self.log("=" * 60)

    def setup_ui(self):
        """初始化界面"""
        # 顶部状态栏
        status_frame = ttk.Frame(self.root, padding="10")
        status_frame.pack(fill=tk.X)

        ttk.Label(status_frame, text="当前状态:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.status_label = ttk.Label(status_frame, text="就绪", foreground="green", cursor="hand2")
        self.status_label.pack(side=tk.LEFT, padx=5)

        # 状态标签右键菜单（隐藏功能入口）
        status_menu = tk.Menu(self.root, tearoff=0)
        status_menu.add_command(label="路由器设置 (Ctrl+R)", command=lambda: self.root.event_generate('<Control-r>'))
        status_menu.add_command(label="查看日志 (Ctrl+L)", command=lambda: self.root.event_generate('<Control-l>'))
        status_menu.add_separator()
        status_menu.add_command(label="关于", command=self.show_about)

        def show_status_menu(event):
            status_menu.post(event.x_root, event.y_root)

        self.status_label.bind("<Button-3>", show_status_menu)

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            status_frame,
            variable=self.progress_var,
            maximum=100,
            length=200,
            mode='determinate'
        )
        self.progress_bar.pack(side=tk.RIGHT, padx=5)

        # 按钮区域
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.pack(fill=tk.X)

        self.disconnect_button = ttk.Button(
            button_frame,
            text="断开并清除",
            command=self.disconnect_and_clear,
            width=20
        )
        self.disconnect_button.pack(side=tk.LEFT, padx=5)

        self.reconnect_button = ttk.Button(
            button_frame,
            text="开始连接",
            command=self.reconnect,
            width=20
        )
        self.reconnect_button.pack(side=tk.LEFT, padx=5)

        # 日志区域
        log_frame = ttk.LabelFrame(self.root, text="操作日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=20,
            width=70,
            font=("Consolas", 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 配置日志标签颜色
        self.log_text.tag_config("INFO", foreground="black")
        self.log_text.tag_config("SUCCESS", foreground="green")
        self.log_text.tag_config("ERROR", foreground="red")
        self.log_text.tag_config("WARNING", foreground="orange")

        # 底部按钮
        bottom_frame = ttk.Frame(self.root, padding="10")
        bottom_frame.pack(fill=tk.X)

        ttk.Button(bottom_frame, text="清空日志", command=self.clear_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="退出", command=self.quit_app).pack(side=tk.RIGHT, padx=5)

    def log(self, message, level="INFO"):
        """记录日志到队列"""
        self.log_queue.put((message, level))

    def process_log_queue(self):
        """处理日志队列（从队列中取出日志并显示）"""
        try:
            while True:
                message, level = self.log_queue.get_nowait()

                # 显示到日志框
                self.log_text.insert(tk.END, message + "\n", level)
                self.log_text.see(tk.END)

                # 同时输出到控制台
                print(message)
        except queue.Empty:
            pass

        # 100ms后再次检查
        self.root.after(100, self.process_log_queue)

    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)

    def update_status(self, status, color="green"):
        """更新状态栏"""
        self.status_label.config(text=status, foreground=color)

    def update_progress(self, value, text=None):
        """更新进度条"""
        self.progress_var.set(value)
        if text:
            self.log(f"[进度] {text}")

    def stop_progress(self):
        """停止进度条"""
        self.progress_var.set(0)

    def update_button(self, button_name, state, text=None):
        """更新按钮状态"""
        if button_name == "disconnect":
            if text:
                self.disconnect_button.config(text=text, state=state)
            else:
                self.disconnect_button.config(state=state)
        elif button_name == "connect":
            if text:
                self.reconnect_button.config(text=text, state=state)
            else:
                self.reconnect_button.config(state=state)

    def disconnect_and_clear(self):
        """断开并清除账号密码"""
        # 禁用按钮
        self.update_button("disconnect", tk.DISABLED, "正在断开...")
        self.update_button("connect", tk.DISABLED)

        # 在新线程中执行断开操作
        thread = threading.Thread(target=self.run_disconnect)
        thread.daemon = True
        thread.start()

    def run_disconnect(self):
        """执行断开逻辑（HTTP API 版本）"""
        disconnect_success = False
        try:
            self.log("[INFO] 开始执行断开和清除流程...")

            # 更新进度：初始化
            self.update_progress(10, "正在连接路由器...")

            # 创建 HTTP 清理器
            self.cleaner = TPLinkHTTPCleaner(self.router_ip, self.router_password)

            # 替换日志方法
            self.cleaner._log = lambda msg: self.log(msg)

            # 执行清理流程
            disconnect_success = self.cleaner.run_cleanup()

            if disconnect_success:
                self.log("[SUCCESS] 断开并清除成功！")
                self.update_status("已断开并清除", "green")
                self.update_progress(100, "完成！")
            else:
                self.log("[ERROR] 断开并清除失败")
                self.update_status("操作失败", "red")

        except Exception as e:
            self.log(f"[ERROR] 断开时发生错误: {e}")
            import traceback
            self.log(traceback.format_exc())
            disconnect_success = False

        # 恢复按钮状态
        self.log("[INFO] 正在恢复按钮状态...")
        self.update_button("disconnect", tk.NORMAL, "断开并清除")
        self.update_button("connect", tk.NORMAL)
        self.stop_progress()

        # 清除保存的账号密码
        self.saved_account = ""
        self.saved_password = ""

        return disconnect_success

    def reconnect(self):
        """重新连接"""
        # 弹出对话框获取宽带账号密码
        dialog = tk.Toplevel(self.root)
        dialog.title("宽带账号")
        dialog.geometry("400x250")
        dialog.resizable(False, False)

        # 居中显示
        dialog.transient(self.root)
        dialog.grab_set()

        # 账号输入
        ttk.Label(dialog, text="宽带账号:").pack(pady=(20, 5))
        account_entry = ttk.Entry(dialog, width=40)
        account_entry.pack(pady=5)
        if self.saved_account:
            account_entry.insert(0, self.saved_account)

        # 密码输入
        ttk.Label(dialog, text="宽带密码:").pack(pady=(10, 5))
        password_entry = ttk.Entry(dialog, width=40, show="*")
        password_entry.pack(pady=5)
        if self.saved_password:
            password_entry.insert(0, self.saved_password)

        # 结果变量
        result = {'confirmed': False, 'account': '', 'password': ''}

        def on_confirm():
            result['account'] = account_entry.get().strip()
            result['password'] = password_entry.get().strip()
            result['confirmed'] = True
            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        # 按钮
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="连接", command=on_confirm, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=on_cancel, width=10).pack(side=tk.LEFT, padx=5)

        # 等待对话框关闭
        self.root.wait_window(dialog)

        if result['confirmed'] and result['account'] and result['password']:
            # 保存账号密码
            self.saved_account = result['account']
            self.saved_password = result['password']

            # 禁用按钮
            self.update_button("disconnect", tk.DISABLED)
            self.update_button("connect", tk.DISABLED, "正在连接...")

            # 在新线程中执行连接
            thread = threading.Thread(target=self.run_connection, args=(result['account'], result['password']))
            thread.daemon = True
            thread.start()
        else:
            self.log("[INFO] 连接已取消")

    def run_connection(self, broadband_user, broadband_pass):
        """执行连接逻辑"""
        connection_success = False
        try:
            self.log("=" * 60)
            self.log("开始执行路由器连接流程...")
            self.log(f"账号: {broadband_user}")
            self.log(f"密码: {'*' * len(broadband_pass)}")
            self.log("=" * 60)

            # 更新进度：初始化
            self.update_progress(10, "正在连接路由器...")
            self.update_status("正在连接...")

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

            # 2. 设置MAC地址（如果配置了）
            mac_mode = self.config_manager.get_config().get("mac_mode", "router")
            self.update_progress(30, "正在设置MAC地址...")

            if mac_mode == 'random':
                self.log("[INFO] MAC模式: 随机MAC")
                self.cleaner.set_mac_address('random')
            elif mac_mode == 'pc':
                self.log("[INFO] MAC模式: PC MAC")
                self.cleaner.set_mac_address('pc')
            else:
                self.log("[INFO] MAC模式: 路由器默认")

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

            # 5. 等待连接建立（检查IP地址）
            self.update_progress(80, "正在等待IP分配...")
            self.log("[INFO] 等待IP地址分配（15秒）...")
            import time as time_module
            time_module.sleep(15)

            # 6. 检查连接状态
            self.update_progress(90, "正在验证连接...")
            self.log("[INFO] 正在检查连接状态...")
            wan_status = self.cleaner.get_wan_status()

            if wan_status:
                ip_address = wan_status.get("network", {}).get("wan_status", {}).get("ipaddr", "")
                self.log(f"[INFO] WAN IP地址: {ip_address}")

                if ip_address and ip_address != "0.0.0.0" and ip_address != "":
                    self.log("=" * 60)
                    self.log("[SUCCESS] 连接成功！")
                    self.log(f"已获取IP地址: {ip_address}")
                    self.log("=" * 60)
                    connection_success = True
                    self.update_status(f"已连接 IP: {ip_address}", "green")
                    self.update_progress(100, "连接成功！")
                else:
                    self.log("[WARNING] 未获取到有效IP地址")
                    self.update_status("连接失败", "orange")
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
            self.update_button("disconnect", tk.NORMAL, "断开并清除")
            self.update_button("connect", tk.DISABLED, "已连接")
        else:
            self.update_button("disconnect", tk.NORMAL, "断开并清除")
            self.update_button("connect", tk.NORMAL, "重新连接")
        self.stop_progress()

        return connection_success

    def show_reconfig_dialog(self):
        """显示重新配置对话框（隐藏功能）"""
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

        # 结果存储
        result = {'saved': False}

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

        # MAC地址模式
        mac_frame = tk.Frame(dialog)
        mac_frame.pack(pady=5, padx=30, fill=tk.X)
        tk.Label(mac_frame, text="MAC地址模式:", font=("Arial", 10)).pack(anchor=tk.W, pady=(0, 5))

        mac_mode_value = current_config.get('mac_mode', 'router')
        mac_mode_mapping = {
            'router': "使用路由器的MAC地址",
            'pc': "使用当前管理PC的MAC地址",
            'random': "使用随机MAC地址"
        }
        mac_mode_var = tk.StringVar(value=mac_mode_mapping.get(mac_mode_value, "使用路由器的MAC地址"))
        mac_mode_combobox = ttk.Combobox(
            mac_frame,
            textvariable=mac_mode_var,
            values=list(mac_mode_mapping.values()),
            state="readonly",
            width=40
        )
        mac_mode_combobox.pack(fill=tk.X, pady=(0, 10))

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
                'mac_mode': 'router',
                'version': '1.0'
            }

            # 转换MAC模式
            mac_mode_text = mac_mode_var.get()
            for mode, text in mac_mode_mapping.items():
                if text == mac_mode_text:
                    new_config['mac_mode'] = mode
                    break

            if self.config_manager.save_config(new_config):
                result['saved'] = True
                messagebox.showinfo("成功", "配置保存成功！", parent=dialog)
                dialog.destroy()
                # 更新配置
                self.router_ip = router_ip
                self.router_password = router_password
            else:
                error_label.config(text="保存配置失败")

        # 按钮
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="保存", command=validate_and_save, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="取消", command=dialog.destroy, width=10).pack(side=tk.LEFT, padx=5)

    def show_about(self):
        """显示关于对话框"""
        about_text = """
TP-Link 宽带拨号助手 (HTTP API 版本)

版本: 2.0
特点: 不使用浏览器，直接通过HTTP API操作路由器

功能:
- 宽带拨号连接
- 自动清理账号（关机时）
- MAC地址随机化
- 操作日志记录

隐藏功能（右键点击状态栏）:
- 路由器设置 (Ctrl+R)
- 查看日志 (Ctrl+L)

提示:
- 首次运行会显示配置向导
- 配置保存在: ~/.tplink_dialer/config.json
"""
        messagebox.showinfo("关于", about_text.strip())

    def show_log_window(self):
        """显示日志窗口（隐藏功能）"""
        log_window = tk.Toplevel(self.root)
        log_window.title("操作日志")
        log_window.geometry("700x500")

        # 居中显示
        log_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (700 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (500 // 2)
        log_window.geometry(f"+{x}+{y}")

        # 工具栏
        toolbar = tk.Frame(log_window)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(toolbar, text="清空日志", command=self.clear_log).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="关闭", command=log_window.destroy).pack(side=tk.RIGHT, padx=2)

        # 日志文本框
        log_text = scrolledtext.ScrolledText(
            log_window,
            height=20,
            font=("Consolas", 9)
        )
        log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 复制当前日志
        current_log = self.log_text.get(1.0, tk.END)
        log_text.insert(1.0, current_log)
        log_text.config(state=tk.DISABLED)

    def quit_app(self):
        """退出应用"""
        if messagebox.askyesno("确认退出", "确定要退出吗？"):
            self.root.destroy()


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

    # MAC地址模式说明
    mac_frame = tk.Frame(wizard_root)
    mac_frame.pack(pady=5, padx=40, fill=tk.X)

    mac_label = tk.Label(
        mac_frame,
        text="💡 MAC地址模式：使用路由器默认MAC（可在设置中修改）",
        font=("Arial", 8),
        fg="#999999"
    )
    mac_label.pack()

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
            'mac_mode': 'router',
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
        text="提示：配置可在程序设置中随时修改",
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
        if messagebox.askyesno("确认退出", "确定要退出吗？"):
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # 绑定隐藏功能的快捷键
    # Ctrl+R: 重新配置路由器
    def show_reconfig(event=None):
        app.show_reconfig_dialog()

    root.bind('<Control-r>', show_reconfig)

    # Ctrl+L: 显示日志窗口
    def show_log(event=None):
        app.show_log_window()

    root.bind('<Control-l>', show_log)

    # Ctrl+Shift+R: 隐藏的配置重置功能
    def reset_config(event=None):
        if messagebox.askyesno("重置配置", "确定要重置所有配置吗？\n\n这将清除路由器信息并退出程序。"):
            import os
            config_file = Path(os.environ.get("USERPROFILE", ".")) / ".tplink_dialer" / "config.json"
            if config_file.exists():
                config_file.unlink()
            messagebox.showinfo("重置成功", "配置已重置，下次启动将显示配置向导。")
            root.destroy()

    root.bind('<Control-Shift-R>', reset_config)

    # 运行主循环
    root.mainloop()


if __name__ == '__main__':
    main()
