from playwright.sync_api import sync_playwright
import re
import time
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import sys
import os
import subprocess
import ctypes
import atexit
from pathlib import Path

# 设置 Playwright 浏览器路径（用于 PyInstaller 打包后的环境）
def resource_path(relative_path):
    """获取 PyInstaller 打包后的资源绝对路径"""
    try:
        # PyInstaller 创建临时文件夹，将路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    except Exception:
        # 如果不是打包环境，使用当前文件所在目录
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# 强制 Playwright 使用打包后的本地浏览器
if getattr(sys, 'frozen', False):
    # PyInstaller 打包后的环境
    browsers_path = resource_path("ms-playwright")
    if os.path.exists(browsers_path):
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = browsers_path
        print(f"Set PLAYWRIGHT_BROWSERS_PATH to: {browsers_path}")
    else:
        print(f"Warning: Playwright browsers not found at: {browsers_path}")
        print(f"Available directories in {resource_path('')}:")
        try:
            for item in os.listdir(resource_path('')):
                item_path = os.path.join(resource_path(''), item)
                if os.path.isdir(item_path):
                    print(f"  - {item}")
        except:
            pass

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

# 检查系统托盘功能是否可用
TRAY_AVAILABLE = PYSTRAY_AVAILABLE and PIL_AVAILABLE

if not TRAY_AVAILABLE:
    missing = []
    if not PYSTRAY_AVAILABLE:
        missing.append("pystray")
    if not PIL_AVAILABLE:
        missing.append("PIL")
    print(f"警告: 未安装 {', '.join(missing)} 库，系统托盘功能不可用")
    print("如需系统托盘功能，请运行: pip install pystray pillow")


class RouterLoginGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("宽带拨号")
        self.root.geometry("400x320")

        # 禁用最大化按钮，允许最小化
        self.root.resizable(False, False)

        # 禁用窗口关闭按钮（X按钮）
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 监听窗口最小化事件
        self.root.bind("<Unmap>", self.on_minimize)
        
        # 监听系统关机事件
        self.root.protocol("WM_QUERYENDSESSION", self.on_shutdown_query)
        
        # 路由器配置
        self.router_password = "Cdu@123"
        self.router_ip = "192.168.1.1"
        
        # 保存的账号密码
        self.saved_account = ""
        self.saved_password = ""
        
        # 关闭标志，防止重复触发关闭事件
        self.is_closing = False
        
        # 日志队列，用于线程安全的日志传递
        self.log_queue = queue.Queue()
        
        # 系统托盘图标
        self.tray_icon = None
        
        # 托盘图标状态
        self.tray_icon_status = "offline"  # offline, online, connecting, error
        
        # 托盘图标双击检测
        self._last_click_time = 0
        self._click_count = 0
        
        # 调试窗口
        self.debug_window = None
        self.debug_text = None
        
        # 创建界面
        self.create_widgets()

        # 启动日志处理定时器
        self.process_log_queue()

        # 创建系统托盘图标（如果可用）
        if TRAY_AVAILABLE:
            self.create_tray_icon()
        
        # 注册Windows关机拦截
        self.register_shutdown_block()
        
        # 设置焦点到账号输入框
        self.account_entry.focus()
        
    def on_closing(self):
        """窗口关闭事件处理"""
        # 如果有托盘图标，隐藏到托盘
        if TRAY_AVAILABLE and self.tray_icon:
            self.hide_to_tray()
            return

        # 如果没有托盘图标，执行正常的关闭流程
        # 防止重复触发关闭事件
        if self.is_closing:
            self.log("⚠️ 关闭操作正在进行中，请稍候...")
            return

        # 如果有保存的账号，自动执行断开并清除
        if self.saved_account:
            # 设置关闭标志
            self.is_closing = True

            # 停止进度条（如果正在运行）
            self.stop_progress()

            self.log("=" * 50)
            self.log("检测到窗口关闭，自动执行断开并清除...")
            self.log("=" * 50)

            # 创建断开完成的标志和结果
            disconnect_complete = threading.Event()
            disconnect_result = [False]  # 使用列表来在闭包中修改值

            # 包装断开函数，完成后设置标志和结果
            def disconnect_with_callback():
                result = self.run_disconnect(close_on_success=False)
                disconnect_result[0] = result
                disconnect_complete.set()

            # 在新线程中执行断开，避免阻塞GUI关闭
            thread = threading.Thread(target=disconnect_with_callback)
            thread.daemon = False  # 改为非守护线程，确保执行完成
            thread.start()

            # 等待断开完成，最多等待30秒
            def wait_for_disconnect():
                if disconnect_complete.wait(timeout=30):
                    # 检查断开是否成功
                    if disconnect_result[0]:
                        self.log("✅ 断开并清除成功，关闭窗口...")
                        self.root.destroy()
                    else:
                        self.log("=" * 50)
                        self.log("❌ 验证失败：账号密码未完全清除")
                        self.log("⚠️ 窗口将保持打开，请手动检查或重试")
                        self.log("=" * 50)
                        # 恢复按钮状态，允许用户重试
                        self.update_button("disconnect", tk.NORMAL, "断开并清除")
                        self.update_button("connect", tk.NORMAL)
                        # 重置关闭标志
                        self.is_closing = False
                else:
                    self.log("⚠️ 断开操作超时，强制关闭窗口...")
                    self.root.destroy()

            # 在100ms后开始检查（给GUI一点时间更新日志）
            self.root.after(100, wait_for_disconnect)
        else:
            # 没有保存的账号，直接关闭
            self.root.destroy()

    def on_minimize(self, event):
        """窗口最小化事件处理"""
        # 如果窗口被最小化，隐藏到托盘
        if self.root.state() == 'iconic':
            if TRAY_AVAILABLE and self.tray_icon:
                # 延迟一小段时间后隐藏窗口，确保最小化动画完成
                self.root.after(100, self.hide_to_tray)
            else:
                self.log("提示: 系统托盘功能不可用，窗口保持可见")
    
    def register_shutdown_block(self):
        """注册Windows关机拦截"""
        try:
            if sys.platform == "win32":
                # 定义Windows API函数
                # SetProcessShutdownParameters - 设置关机参数
                # 使应用程序在关机时获得更多时间来清理
                SHUTDOWN_NORETRY = 0x1
                
                # 定义函数原型
                ctypes.windll.kernel32.SetProcessShutdownParameters.argtypes = [
                    ctypes.c_ulong,  # dwLevel
                    ctypes.c_ulong   # dwFlags
                ]
                ctypes.windll.kernel32.SetProcessShutdownParameters.restype = ctypes.c_bool
                
                # 调用API
                result = ctypes.windll.kernel32.SetProcessShutdownParameters(
                    0x3FF,  # dwLevel - 最高优先级
                    SHUTDOWN_NORETRY  # dwFlags - 不重试
                )
                
                if result:
                    self.log("✅ 已注册Windows关机拦截（高优先级）")
                else:
                    self.log("⚠️ 关机拦截注册失败")
                    
        except Exception as e:
            self.log(f"⚠️ 注册关机拦截失败: {e}")
    
    def on_shutdown_query(self):
        """系统关机事件处理"""
        # 如果有保存的账号，需要先断开并清除
        if self.saved_account:
            self.log("=" * 50)
            self.log("检测到系统关机事件，账号未断开！")
            self.log("=" * 50)
            
            # 防止重复触发关闭事件
            if self.is_closing:
                self.log("⚠️ 关闭操作正在进行中，请稍候...")
                # 返回False阻止关机
                return False
            
            # 设置关闭标志
            self.is_closing = True
            
            # 显示提醒对话框
            warning_message = (
                "⚠️ 警告：检测到系统关机！\n\n"
                "您的宽带账号密码仍保存在路由器中！\n\n"
                "为了账号安全，请先断开连接并清除账号密码。\n\n"
                "是否立即执行断开并清除操作？"
            )
            
            # 使用消息框询问用户
            response = messagebox.askyesno(
                "安全警告",
                warning_message,
                icon=messagebox.WARNING,
                default=messagebox.YES
            )
            
            if response:
                # 用户选择执行断开操作
                self.log("用户选择执行断开并清除操作")
                
                # 停止进度条（如果正在运行）
                self.stop_progress()
                
                self.log("=" * 50)
                self.log("正在执行断开并清除...")
                self.log("=" * 50)
                
                # 创建断开完成的标志和结果
                disconnect_complete = threading.Event()
                disconnect_result = [False]  # 使用列表来在闭包中修改值
                
                # 包装断开函数，完成后设置标志和结果
                def disconnect_with_callback():
                    try:
                        result = self.run_disconnect(close_on_success=False)
                        disconnect_result[0] = result
                    except Exception as e:
                        self.log(f"❌ 断开操作出错: {e}")
                    finally:
                        disconnect_complete.set()
                
                # 在新线程中执行断开
                thread = threading.Thread(target=disconnect_with_callback)
                thread.daemon = False  # 改为非守护线程，确保执行完成
                thread.start()
                
                # 等待断开完成，最多等待30秒
                if disconnect_complete.wait(timeout=30):
                    # 检查断开是否成功
                    if disconnect_result[0]:
                        self.log("✅ 断开并清除成功")
                        # 显示成功消息
                        messagebox.showinfo(
                            "清理完成",
                            "✅ 账号密码已成功清除！\n\n现在可以安全关机了。"
                        )
                        # 重置关闭标志
                        self.is_closing = False
                        # 返回True允许关机
                        return True
                    else:
                        self.log("=" * 50)
                        self.log("❌ 验证失败：账号密码未完全清除")
                        self.log("=" * 50)
                        # 显示失败消息
                        messagebox.showwarning(
                            "清理失败",
                            "❌ 账号密码清除失败！\n\n"
                            "请手动检查路由器配置，或点击【断开连接】按钮重试。"
                        )
                        # 重置关闭标志
                        self.is_closing = False
                        # 返回True允许关机
                        return True
                else:
                    self.log("⚠️ 断开操作超时")
                    # 显示超时消息
                    messagebox.showwarning(
                        "操作超时",
                        "⚠️ 断开操作超时（30秒）！\n\n"
                        "请检查路由器是否正常工作。"
                    )
                    # 重置关闭标志
                    self.is_closing = False
                    # 返回True允许关机
                    return True
            else:
                # 用户选择不执行断开操作
                self.log("用户取消断开操作")
                # 显示警告消息
                messagebox.showwarning(
                    "安全警告",
                    "⚠️ 您选择不清除账号密码！\n\n"
                    "账号密码可能仍保存在路由器中，存在泄露风险！\n\n"
                    "建议您在关机前手动点击【断开连接】按钮清除账号。"
                )
                # 重置关闭标志
                self.is_closing = False
                # 返回False阻止关机（用户已知晓风险但仍需阻止）
                return False
        else:
            # 没有保存的账号，直接允许关机
            self.log("系统关机：无保存的账号，允许关机")
            return True
        
    def create_widgets(self):
        # 标题
        title_label = tk.Label(
            self.root,
            text="宽带拨号",
            font=("Microsoft YaHei", 16, "bold")
        )
        title_label.pack(pady=15)
        
        # 账号输入框
        account_frame = tk.Frame(self.root)
        account_frame.pack(pady=8, padx=30, fill=tk.X)
        
        tk.Label(account_frame, text="宽带账号:", font=("Microsoft YaHei", 10)).pack(side=tk.LEFT, padx=5)
        self.account_entry = tk.Entry(account_frame, font=("Microsoft YaHei", 10), width=25)
        self.account_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        # 绑定回车键
        self.account_entry.bind("<Return>", lambda e: self.password_entry.focus())
        
        # 密码输入框
        password_frame = tk.Frame(self.root)
        password_frame.pack(pady=8, padx=30, fill=tk.X)
        
        tk.Label(password_frame, text="宽带密码:", font=("Microsoft YaHei", 10)).pack(side=tk.LEFT, padx=5)
        self.password_entry = tk.Entry(password_frame, font=("Microsoft YaHei", 10), width=25, show="*")
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
            font=("Microsoft YaHei", 11, "bold"),
            bg="#4CAF50",
            fg="white",
            width=12,
            height=2
        )
        self.connect_button.pack(side=tk.LEFT, padx=8)
        
        self.disconnect_button = tk.Button(
            button_frame,
            text="断开连接",
            command=self.disconnect_and_clear,
            font=("Microsoft YaHei", 11, "bold"),
            bg="#f44336",
            fg="white",
            width=12,
            height=2
        )
        self.disconnect_button.pack(side=tk.LEFT, padx=8)
        
        # 断开连接提示文字（红色，在两个按钮下方，居中显示）
        disconnect_hint_label = tk.Label(
            self.root,
            text="为了您的账户安全，使用完成后请点击断开，系统会清除账号\n请耐心等待程序正常退出......",
            font=("Microsoft YaHei", 9, "bold"),
            fg="#FF0000",
            justify=tk.CENTER
        )
        disconnect_hint_label.pack(pady=(5, 0))
        
        # 进度条（双击可查看日志）
        progress_frame = tk.Frame(self.root)
        progress_frame.pack(pady=15, padx=30, fill=tk.X)

        self.progress_label = tk.Label(
            progress_frame,
            text="",
            font=("Microsoft YaHei", 9)
        )
        self.progress_label.pack(anchor=tk.W)

        self.progress_bar = ttk.Progressbar(
            progress_frame,
            orient=tk.HORIZONTAL,
            mode='determinate',
            maximum=100
        )
        self.progress_bar.pack(fill=tk.X)

        # 绑定双击事件打开调试窗口
        self.progress_bar.bind("<Double-Button-1>", lambda e: self.toggle_debug_window())
        self.progress_label.bind("<Double-Button-1>", lambda e: self.toggle_debug_window())

        # 状态栏
        self.status_label = tk.Label(
            self.root,
            text="就绪 | 双击进度条可查看运行日志",
            font=("Microsoft YaHei", 9),
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
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
        """创建调试窗口（非模态窗口）"""
        if self.debug_window is None or not self.debug_window.winfo_exists():
            self.debug_window = tk.Toplevel(self.root)
            self.debug_window.title("运行日志 - 宽带拨号")
            self.debug_window.geometry("600x400")
            
            # 设置为非模态窗口，不强制置顶
            self.debug_window.transient(self.root)
            
            # 调试信息显示区域
            debug_label = tk.Label(self.debug_window, text="运行日志:", font=("Microsoft YaHei", 10, "bold"))
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
                font=("Microsoft YaHei", 9)
            )
            clear_button.pack(pady=5)
            
            # 监听窗口关闭事件 - 销毁窗口而不是隐藏
            self.debug_window.protocol("WM_DELETE_WINDOW", self.close_debug_window)
    
    def close_debug_window(self):
        """关闭调试窗口"""
        if self.debug_window and self.debug_window.winfo_exists():
            self.debug_window.destroy()
            self.debug_window = None
            self.debug_text = None
    
    def clear_debug_log(self):
        """清空调试日志"""
        if self.debug_text:
            self.debug_text.config(state=tk.NORMAL)
            self.debug_text.delete(1.0, tk.END)
            self.debug_text.config(state=tk.DISABLED)
    
    def process_log_queue(self):
        """处理日志队列（在主线程中执行）"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                # 检查是否是特殊消息
                if message == "[CLOSE_WINDOW]":
                    # 关闭窗口消息
                    self.root.destroy()
                    return
                elif message == "[HIDE_TO_TRAY]":
                    # 隐藏到托盘消息
                    self.hide_to_tray()
                elif message.startswith("[PROGRESS]"):
                    # 进度更新消息
                    # 格式: [PROGRESS]value|text
                    parts = message[10:].split("|")
                    if len(parts) >= 1:
                        value = int(parts[0])
                        text = parts[1] if len(parts) > 1 else ""
                        self.progress_bar['value'] = value
                        self.progress_label.config(text=text)
                elif message == "[STOP_PROGRESS]":
                    # 停止进度条
                    self.progress_bar['value'] = 0
                    self.progress_label.config(text="")
                elif message.startswith("[SHOW_ERROR]"):
                    # 显示错误弹窗
                    error_msg = message[11:]  # 移除[SHOW_ERROR]前缀
                    messagebox.showerror("连接失败", error_msg)
                elif message.startswith("[STATUS]"):
                    # 状态更新消息
                    status = message[8:]  # 移除[STATUS]前缀
                    self.status_label.config(text=status)
                elif message.startswith("[BUTTON]"):
                    # 按钮状态更新消息
                    # 格式: [BUTTON]button_name|state|text
                    parts = message[8:].split("|")
                    if len(parts) >= 2:
                        button_name = parts[0]
                        state = parts[1]
                        text = parts[2] if len(parts) > 2 else None

                        if button_name == "connect":
                            if text:
                                self.connect_button.config(state=state, text=text)
                            else:
                                self.connect_button.config(state=state)
                        elif button_name == "disconnect":
                            if text:
                                self.disconnect_button.config(state=state, text=text)
                            else:
                                self.disconnect_button.config(state=state)
                else:
                    # 普通日志消息 - 添加到调试窗口
                    if self.debug_text and self.debug_window and self.debug_window.winfo_exists():
                        self.debug_text.config(state=tk.NORMAL)
                        self.debug_text.insert(tk.END, message + "\n")
                        self.debug_text.see(tk.END)
                        self.debug_text.config(state=tk.DISABLED)
        except queue.Empty:
            pass
        # 每100ms检查一次队列
        self.root.after(100, self.process_log_queue)
    
    def log(self, message):
        """添加日志信息（线程安全）"""
        # 将消息放入队列，由主线程处理
        self.log_queue.put(message)

    def update_progress(self, value, text=""):
        """更新进度条（线程安全）"""
        self.log_queue.put(f"[PROGRESS]{value}|{text}")

    def stop_progress(self):
        """停止进度条（线程安全）"""
        self.log_queue.put("[STOP_PROGRESS]")
        
    def update_status(self, status):
        """更新状态栏（线程安全）"""
        # 使用队列传递状态更新
        self.log_queue.put(f"[STATUS]{status}")
    
    def update_button(self, button_name, state, text=None):
        """更新按钮状态（线程安全）"""
        # 格式: [BUTTON]button_name|state|text
        msg = f"[BUTTON]{button_name}|{state}"
        if text:
            msg += f"|{text}"
        self.log_queue.put(msg)
    
    def create_tray_icon(self):
        """创建系统托盘图标"""
        if not TRAY_AVAILABLE:
            return
            
        try:
            # 尝试加载Windows网络图标
            icon_image = self.get_network_icon()
            
            if icon_image is None:
                # 如果无法加载系统图标，创建一个简单的图标
                icon_image = self.create_default_icon()
            
            # 创建菜单
            menu = Menu(
                MenuItem('显示窗口', self.show_window),
                MenuItem('隐藏窗口', self.hide_to_tray),
                MenuItem('断开并清除', self.disconnect_from_tray),
            )
            
            # 创建托盘图标
            self.tray_icon = pystray.Icon(
                "宽带拨号",
                icon_image,
                "宽带拨号",
                menu
            )
            
            # 设置点击事件处理（用于检测双击）
            def on_click(icon, button, time):
                import time as time_module
                current_time = time_module.time()
                
                # 检查是否是双击（两次点击间隔小于500ms）
                if current_time - self._last_click_time < 0.5:
                    self._click_count += 1
                    if self._click_count >= 2:
                        # 双击检测成功
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
            status: 状态名称 (offline, online, connecting, error)
        
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
    
    def update_tray_icon(self, status):
        """更新托盘图标
        
        Args:
            status: 状态名称 (offline, online, connecting, error)
        """
        if not TRAY_AVAILABLE or not self.tray_icon:
            return
        
        try:
            # 加载新的图标
            new_icon = self.load_status_icon(status)
            
            if new_icon:
                # 更新托盘图标
                self.tray_icon.icon = new_icon
                self.tray_icon_status = status
                self.log(f"✅ 托盘图标已更新: {status}")
        except Exception as e:
            self.log(f"⚠️ 更新托盘图标失败: {e}")
    
    def get_network_icon(self):
        """尝试从Windows系统获取网络图标"""
        try:
            # Windows系统中的网络图标路径
            system_root = os.environ.get('SystemRoot', r'C:\Windows')
            icon_paths = [
                os.path.join(system_root, r'System32\netshell.dll'),
                os.path.join(system_root, r'System32\shell32.dll'),
            ]
            
            # 尝试从DLL中提取图标
            import ctypes
            from ctypes import wintypes
            
            for dll_path in icon_paths:
                if os.path.exists(dll_path):
                    try:
                        # 使用Windows API加载图标
                        user32 = ctypes.windll.user32
                        user32.LoadImageW.argtypes = [
                            wintypes.HINSTANCE,
                            wintypes.LPCWSTR,
                            wintypes.UINT,
                            wintypes.INT,
                            wintypes.INT,
                            wintypes.UINT
                        ]
                        user32.LoadImageW.restype = wintypes.HANDLE
                        
                        # 加载图标（尝试不同的索引）
                        for icon_index in [0, 1, 2, 3, 4, 5]:
                            h_icon = user32.LoadImageW(
                                None,
                                dll_path,
                                1,  # IMAGE_ICON
                                64,  # 宽度
                                64,  # 高度
                                0  # LR_LOADFROMFILE
                            )
                            
                            if h_icon:
                                # 转换为PIL Image
                                from PIL import ImageDraw
                                img = Image.new('RGB', (64, 64), (0, 120, 215))  # Windows蓝色
                                draw = ImageDraw.Draw(img)
                                draw.ellipse([16, 16, 48, 48], fill='white')
                                return img
                    except:
                        continue
        except Exception as e:
            pass
        
        return None
    
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
    
    def show_window(self, icon=None, item=None):
        """显示窗口"""
        self.root.deiconify()  # 显示窗口
        self.root.lift()  # 提升到前台
        self.root.focus_force()  # 强制获取焦点
    
    def disconnect_from_tray(self, icon=None, item=None):
        """从托盘菜单断开连接"""
        self.show_window()
        self.disconnect_and_clear()
    
    def quit_app(self, icon=None, item=None):
        """退出应用（安全退出，确保执行断开和清除）"""
        # 如果有保存的账号，需要先断开并清除
        if self.saved_account:
            # 防止重复触发关闭事件
            if self.is_closing:
                self.log("⚠️ 关闭操作正在进行中，请稍候...")
                return

            # 设置关闭标志
            self.is_closing = True

            # 停止进度条（如果正在运行）
            self.stop_progress()

            self.log("=" * 50)
            self.log("检测到退出请求，自动执行断开并清除...")
            self.log("=" * 50)

            # 创建断开完成的标志和结果
            disconnect_complete = threading.Event()
            disconnect_result = [False]  # 使用列表来在闭包中修改值

            # 包装断开函数，完成后设置标志和结果
            def disconnect_with_callback():
                result = self.run_disconnect(close_on_success=False)
                disconnect_result[0] = result
                disconnect_complete.set()

            # 在新线程中执行断开，避免阻塞GUI关闭
            thread = threading.Thread(target=disconnect_with_callback)
            thread.daemon = False  # 改为非守护线程，确保执行完成
            thread.start()

            # 等待断开完成，最多等待30秒
            def wait_for_disconnect():
                if disconnect_complete.wait(timeout=30):
                    # 检查断开是否成功
                    if disconnect_result[0]:
                        self.log("✅ 断开并清除成功，退出程序...")
                        # 停止托盘图标
                        if self.tray_icon:
                            self.tray_icon.stop()
                        # 关闭窗口
                        self.root.destroy()
                    else:
                        self.log("=" * 50)
                        self.log("❌ 验证失败：账号密码未完全清除")
                        self.log("⚠️ 程序将保持运行，请手动检查或重试")
                        self.log("=" * 50)
                        # 恢复按钮状态，允许用户重试
                        self.update_button("disconnect", tk.NORMAL, "断开并清除")
                        self.update_button("connect", tk.NORMAL)
                        # 重置关闭标志
                        self.is_closing = False
                else:
                    self.log("⚠️ 断开操作超时，强制退出...")
                    # 停止托盘图标
                    if self.tray_icon:
                        self.tray_icon.stop()
                    # 关闭窗口
                    self.root.destroy()

            # 在100ms后开始检查（给GUI一点时间更新日志）
            self.root.after(100, wait_for_disconnect)
        else:
            # 没有保存的账号，直接退出
            # 停止托盘图标
            if self.tray_icon:
                self.tray_icon.stop()
            # 关闭窗口
            self.root.destroy()
    
    def hide_to_tray(self):
        """隐藏窗口到系统托盘"""
        if self.tray_icon and TRAY_AVAILABLE:
            self.root.withdraw()  # 隐藏窗口
            self.log("窗口已隐藏到系统托盘")
            self.log("双击托盘图标可重新显示窗口")
        else:
            self.log("提示: 系统托盘功能不可用，窗口保持可见")
        
    def start_connection(self):
        """开始连接"""
        # 检查是否正在关闭
        if self.is_closing:
            self.log("⚠️ 程序正在关闭，无法执行连接")
            return
        
        broadband_user = self.account_entry.get().strip()
        broadband_pass = self.password_entry.get().strip()
        
        if not broadband_user or not broadband_pass:
            self.log("❌ 请输入账号和密码")
            return
        
        # 保存账号密码，用于后续断开时清除
        self.saved_account = broadband_user
        self.saved_password = broadband_pass
        
        self.log("=" * 50)
        self.log("🔵 开始连接流程...")
        self.log(f"账号: {broadband_user}")
        self.log(f"密码: {'*' * len(broadband_pass)}")
        self.log("=" * 50)
        
        # 禁用按钮（使用线程安全的方式）
        self.update_button("connect", tk.DISABLED, "连接中...")
        self.update_button("disconnect", tk.DISABLED, None)
        self.update_status("正在连接...")

        # 更新托盘图标为"连接中"
        self.update_tray_icon("connecting")

        # 初始化进度条
        self.update_progress(0, "正在连接......")

        # 在新线程中执行连接，避免阻塞GUI
        thread = threading.Thread(
            target=self.run_connection,
            args=(broadband_user, broadband_pass)
        )
        thread.daemon = True
        thread.start()
        
    def disconnect_and_clear(self):
        """断开连接并清除账号"""
        # 检查是否正在关闭
        if self.is_closing:
            self.log("⚠️ 程序正在关闭，断开操作已在执行中")
            return
        
        self.log("=" * 50)
        self.log("🔴 开始断开流程...")
        self.log("=" * 50)
        
        # 禁用按钮（使用线程安全的方式）
        self.update_button("disconnect", tk.DISABLED, "断开中...")
        self.update_button("connect", tk.DISABLED, None)
        self.update_status("正在断开...")

        # 更新托盘图标为"连接中"
        self.update_tray_icon("connecting")

        # 初始化进度条
        self.update_progress(0, "正在断开......")

        # 在新线程中执行断开，避免阻塞GUI
        thread = threading.Thread(target=self.run_disconnect, args=(True,))
        thread.daemon = True
        thread.start()
        
    def run_disconnect(self, close_on_success=False):
        """执行断开逻辑，返回是否成功清除账号密码

        Args:
            close_on_success: 是否在验证成功后关闭窗口（用于手动点击断开按钮）
        """
        disconnect_success = False
        try:
            self.log("📝 正在启动浏览器...")

            # 更新进度：启动浏览器
            self.update_progress(10, "正在启动浏览器......")

            # 用于存储捕获的 stok
            captured_stok = []

            def capture_stok(route, request):
                """捕获包含 stok 的请求"""
                url = request.url
                if "stok=" in url:
                    match = re.search(r"stok=([^/&?#]+)", url)
                    if match and not captured_stok:
                        stok_value = match.group(1)
                        captured_stok.append(stok_value)
                        self.log(f"✅ 捕获到 stok: {stok_value}")
                route.continue_()

            with sync_playwright() as p:
                self.log("🌐 正在启动 Chromium 浏览器（无头模式）...")
                
                # 尝试找到打包的 Chromium 可执行文件
                executable_path = None
                if getattr(sys, 'frozen', False):
                    # PyInstaller 打包后的环境
                    possible_paths = [
                        # 尝试多个可能的路径
                        os.path.join(sys._MEIPASS, '_internal', 'ms-playwright', 'chromium-1208', 'chrome-win64', 'chrome.exe'),
                        os.path.join(sys._MEIPASS, '_internal', 'ms-playwright', 'chromium-1208', 'chrome-win64', 'ch.exe'),
                        os.path.join(sys._MEIPASS, 'ms-playwright', 'chromium-1208', 'chrome-win64', 'chrome.exe'),
                    ]
                    
                    for path in possible_paths:
                        if os.path.exists(path):
                            executable_path = path
                            self.log(f"找到 Chromium 可执行文件: {executable_path}")
                            break
                
                # 启动浏览器
                launch_options = {
                    'headless': True,
                    'slow_mo': 300
                }
                
                if executable_path:
                    launch_options['executable_path'] = executable_path
                    self.log(f"使用打包的 Chromium: {executable_path}")
                else:
                    self.log("使用系统默认 Chromium")
                
                browser = p.chromium.launch(**launch_options)
                context = browser.new_context()
                page = context.new_page()

                # 设置路由来监听所有请求
                page.route("**/*", capture_stok)

                self.log("🔌 正在访问路由器管理页面...")
                page.goto(f"http://{self.router_ip}/")

                # ===== 登录 =====
                page.wait_for_selector("input[type='password']", timeout=10000)
                page.fill("input[type='password']", self.router_password)
                page.keyboard.press("Enter")

                self.log("正在验证登录...")
                
                # 等待捕获到 stok
                for i in range(15):
                    time.sleep(1)
                    if captured_stok:
                        break
                
                # 停止监听
                page.unroute("**/*", capture_stok)
                
                if not captured_stok:
                    self.log("❌ 登录失败")
                    browser.close()
                    self.update_button("disconnect", tk.NORMAL, "断开并清除")
                    self.update_button("connect", tk.NORMAL)
                    self.update_status("断开失败")
                    self.stop_progress()
                    return

                stok = captured_stok[0]
                self.log("✅ 登录成功")

                # 更新进度：登录成功
                self.update_progress(30, "正在断开连接......")

                # 等待页面加载
                time.sleep(3)
                
                # 导航到上网设置
                self.log("正在进入路由设置...")
                try:
                    router_set_btn = page.wait_for_selector("#routerSetMbtn", timeout=5000)
                    if router_set_btn:
                        router_set_btn.click()
                        time.sleep(2)
                except:
                    pass
                
                try:
                    network_menu = page.wait_for_selector("#network_rsMenu", timeout=5000)
                    if network_menu:
                        network_menu.click()
                        time.sleep(2)
                except:
                    pass
                
                # 断开连接
                self.log("正在断开网络连接...")
                try:
                    disconnect_btn = page.wait_for_selector("#disconnect", timeout=5000)
                    if disconnect_btn:
                        disconnect_btn.click()
                        time.sleep(2)
                except:
                    self.log("⚠️ 未找到断开按钮")

                # 更新进度：断开完成，正在清除
                self.update_progress(60, "正在清除账号密码......")

                # 清除账号密码
                self.log("🗑️ 正在清除账号密码...")
                try:
                    # 清空账号
                    self.log("📝 正在清空账号输入框...")
                    name_input = page.wait_for_selector("#name", timeout=5000)
                    if name_input:
                        name_input.fill("")
                        self.log("✅ 账号输入框已清空")

                    # 清空密码
                    self.log("📝 正在清空密码输入框...")
                    psw_input = page.wait_for_selector("#psw", timeout=5000)
                    if psw_input:
                        psw_input.fill("")
                        self.log("✅ 密码输入框已清空")

                    # 验证账号密码是否真的被清除了
                    self.log("🔍 正在验证账号密码是否已清除...")
                    time.sleep(1)
                    name_value = name_input.input_value()
                    psw_value = psw_input.input_value()
                    self.log(f"📋 验证结果：账号=[{name_value}], 密码=[{psw_value}]")

                    if not name_value and not psw_value:
                        self.log("✅ 账号密码已清除")
                        disconnect_success = True
                    else:
                        self.log(f"❌ 清除失败：账号=[{name_value}], 密码=[{psw_value}]")
                        disconnect_success = False
                except Exception as e:
                    self.log(f"⚠️ 清除账号密码时出错: {e}")
                    disconnect_success = False

                # 更新进度：清除完成，正在保存
                self.update_progress(90, "正在保存配置......")

                # 保存（保存空账号密码）
                self.log("正在保存配置...")
                try:
                    save_btn = page.wait_for_selector("#save", timeout=5000)
                    if save_btn:
                        save_btn.click()
                        time.sleep(2)
                except:
                    self.log("⚠️ 保存配置时出错")
                
                self.log("=" * 50)
                if disconnect_success:
                    self.log("✅ 断开并清除完成")
                    # 更新进度：断开成功
                    self.update_progress(100, "断开成功！")
                else:
                    self.log("❌ 清除验证失败")
                self.log("=" * 50)
                
                time.sleep(2)
                browser.close()
                
                # 如果验证成功且需要关闭窗口，则关闭
                if disconnect_success and close_on_success:
                    self.log("程序即将关闭...")
                    time.sleep(2)
                    self.log_queue.put("[CLOSE_WINDOW]")
                
        except Exception as e:
            self.log(f"❌ 断开时发生错误: {e}")
            disconnect_success = False

        # 恢复按钮状态
        self.log("🔄 正在恢复按钮状态...")
        self.update_button("disconnect", tk.NORMAL, "断开并清除")
        self.update_button("connect", tk.NORMAL, "开始连接")
        self.update_status("已断开并清除")
        self.stop_progress()
        self.log("✅ 按钮状态已恢复")

        # 更新托盘图标为"离线"（断开成功）
        if disconnect_success:
            self.update_tray_icon("offline")

        # 清除保存的账号密码
        self.saved_account = ""
        self.saved_password = ""

        # 返回是否成功清除
        return disconnect_success
        
    def run_connection(self, broadband_user, broadband_pass):
        """执行连接逻辑"""
        try:
            self.log("📝 正在启动浏览器...")
            self.log("=" * 50)
            self.log("开始执行路由器登录流程...")
            self.log(f"账号: {broadband_user}")
            self.log(f"密码: {'*' * len(broadband_pass)}")
            self.log("=" * 50)

            # 更新进度：启动浏览器
            self.update_progress(10, "正在启动浏览器......")
            
            # 用于存储捕获的 stok
            captured_stok = []

            def capture_stok(route, request):
                """捕获包含 stok 的请求"""
                url = request.url
                if "stok=" in url:
                    match = re.search(r"stok=([^/&?#]+)", url)
                    if match and not captured_stok:
                        stok_value = match.group(1)
                        captured_stok.append(stok_value)
                        self.log(f"✅ 从网络请求中捕获到 stok: {stok_value}")
                route.continue_()

            with sync_playwright() as p:
                # 使用 headless=True 静默执行，不显示浏览器窗口
                self.log("🌐 正在启动 Chromium 浏览器（无头模式）...")
                
                # 尝试找到打包的 Chromium 可执行文件
                executable_path = None
                if getattr(sys, 'frozen', False):
                    # PyInstaller 打包后的环境
                    possible_paths = [
                        # 尝试多个可能的路径
                        os.path.join(sys._MEIPASS, '_internal', 'ms-playwright', 'chromium-1208', 'chrome-win64', 'chrome.exe'),
                        os.path.join(sys._MEIPASS, '_internal', 'ms-playwright', 'chromium-1208', 'chrome-win64', 'ch.exe'),
                        os.path.join(sys._MEIPASS, 'ms-playwright', 'chromium-1208', 'chrome-win64', 'chrome.exe'),
                    ]
                    
                    for path in possible_paths:
                        if os.path.exists(path):
                            executable_path = path
                            self.log(f"找到 Chromium 可执行文件: {executable_path}")
                            break
                
                # 启动浏览器
                launch_options = {
                    'headless': True,
                    'slow_mo': 300
                }
                
                if executable_path:
                    launch_options['executable_path'] = executable_path
                    self.log(f"使用打包的 Chromium: {executable_path}")
                else:
                    self.log("使用系统默认 Chromium")
                
                browser = p.chromium.launch(**launch_options)
                context = browser.new_context()
                page = context.new_page()

                # 设置路由来监听所有请求
                page.route("**/*", capture_stok)

                self.log("🔌 正在访问路由器管理页面...")
                self.update_status("正在登录路由器...")
                page.goto(f"http://{self.router_ip}/")

                # ===== 登录 =====
                page.wait_for_selector("input[type='password']", timeout=10000)
                page.fill("input[type='password']", self.router_password)
                page.keyboard.press("Enter")

                self.log("正在验证登录...")
                
                # 等待捕获到 stok
                for i in range(15):
                    time.sleep(1)
                    if captured_stok:
                        break
                
                # 停止监听
                page.unroute("**/*", capture_stok)
                
                if not captured_stok:
                    self.log("❌ 登录失败，请检查管理员密码")
                    browser.close()
                    self.update_button("connect", tk.NORMAL, "开始连接")
                    self.update_status("登录失败")
                    self.stop_progress()
                    # 弹窗提示用户
                    self.log_queue.put("[SHOW_ERROR]登录失败，请检查路由器管理员密码是否正确")
                    return

                stok = captured_stok[0]
                self.log("✅ 登录成功")

                # 更新进度：登录成功
                self.update_progress(30, "正在配置路由器......")

                # 等待登录后的页面完全加载
                time.sleep(3)
                
                # ===== 按照正确的流程操作 =====
                self.log("正在进入路由设置...")
                self.update_status("正在配置路由器...")
                try:
                    router_set_btn = page.wait_for_selector("#routerSetMbtn", timeout=5000)
                    if router_set_btn:
                        router_set_btn.click()
                        time.sleep(2)
                except:
                    pass
                
                self.log("正在打开上网设置...")
                
                # 使用正确的选择器
                internet_menu_selectors = [
                    "#network_rsMenu",
                    "li#network_rsMenu",
                    "li.menuLi",
                    "li:has-text('上网设置')",
                ]
                
                menu_clicked = False
                for selector in internet_menu_selectors:
                    try:
                        menu_item = page.wait_for_selector(selector, timeout=2000)
                        if menu_item:
                            menu_item.click()
                            menu_clicked = True
                            time.sleep(2)
                            break
                    except:
                        continue
                
                if not menu_clicked:
                    self.log("❌ 无法打开上网设置")
                    browser.close()
                    self.update_button("connect", tk.NORMAL, "开始连接")
                    self.update_status("配置失败")
                    self.stop_progress()
                    # 弹窗提示用户
                    self.log_queue.put("[SHOW_ERROR]无法打开上网设置，请检查路由器是否正常工作")
                    return
                
                self.log("正在配置拨号方式...")
                try:
                    # 先检查当前选中的值
                    wan_sel = page.wait_for_selector("#wanSel .value", timeout=5000)
                    if wan_sel:
                        current_value = wan_sel.inner_text()
                        
                        if "宽带拨号上网" in current_value or "PPPoE" in current_value:
                            self.log("✅ 当前已是宽带拨号模式")
                        else:
                            # 点击下拉框打开选项列表
                            wan_sel_box = page.wait_for_selector("#wanSel", timeout=5000)
                            wan_sel_box.click()
                            time.sleep(1)
                            
                            # 点击"宽带拨号上网"选项
                            pppoe_option_selectors = [
                                "#selOptsUlwanSel li:has-text('宽带拨号上网')",
                                "#selOptsUlwanSel li[title='宽带拨号上网']",
                                "li.option:has-text('宽带拨号上网')",
                            ]
                            
                            option_clicked = False
                            for selector in pppoe_option_selectors:
                                try:
                                    pppoe_option = page.wait_for_selector(selector, timeout=1000)
                                    if pppoe_option:
                                        pppoe_option.click()
                                        option_clicked = True
                                        time.sleep(1)
                                        break
                                except:
                                    continue
                            
                            if not option_clicked:
                                self.log("⚠️ 无法切换到宽带拨号模式")
                except Exception as e:
                    self.log(f"⚠️ 配置拨号方式时出错: {e}")

                # 更新进度：配置完成，准备输入账号密码
                self.update_progress(50, "正在输入账号密码......")

                # ===== 填写账号密码 =====
                self.log("正在输入账号密码...")
                self.update_status("正在输入账号密码...")

                # 等待输入框出现
                try:
                    page.wait_for_selector("#name", timeout=10000)
                    page.wait_for_selector("#psw", timeout=5000)
                except:
                    self.log("❌ 无法找到账号密码输入框")
                    browser.close()
                    self.update_button("connect", tk.NORMAL, "开始连接")
                    self.update_status("配置失败")
                    self.stop_progress()
                    # 弹窗提示用户
                    self.log_queue.put("[SHOW_ERROR]无法找到账号密码输入框，请检查路由器页面是否正常")
                    return

                # 更新进度：账号密码输入完成
                self.update_progress(70, "正在拨号连接......")

                # 清空并填写账号
                page.fill("#name", "")
                page.fill("#name", broadband_user)

                # 清空并填写密码
                page.fill("#psw", "")
                page.fill("#psw", broadband_pass)

                # 触发 blur 事件（重要）
                page.locator("#psw").blur()

                time.sleep(1)

                # ===== 点击连接（最多尝试3次） =====
                max_attempts = 3
                connection_success = False

                for attempt in range(1, max_attempts + 1):
                    self.log("=" * 50)
                    self.log(f"🔄 正在进行第 {attempt}/{max_attempts} 次拨号...")
                    self.log("=" * 50)

                    # 更新进度：正在拨号
                    self.update_progress(70 + (attempt - 1) * 10, f"正在拨号（第{attempt}次）......")

                    # 点击连接按钮
                    self.update_status(f"正在拨号（第{attempt}次）...")
                    self.log("🔘 正在点击保存/连接按钮...")
                    try:
                        page.click("#save")
                        self.log("✅ 已点击保存按钮")
                    except Exception as e:
                        self.log(f"⚠️ 点击#save失败: {e}")
                        try:
                            page.click("button:has-text('保存'), button:has-text('连接'), .save-btn")
                            self.log("✅ 已点击备用按钮")
                        except Exception as e2:
                            self.log(f"⚠️ 点击备用按钮也失败: {e2}")
                            page.click("#save")
                            self.log("✅ 再次尝试点击#save")

                    self.log("⏳ 正在等待拨号完成（10秒）...")
                    time.sleep(10)

                    # ===== 检查连接状态 =====
                    self.update_status(f"正在验证连接（第{attempt}次）...")
                    self.log("🔍 正在检查连接状态...")
                    try:
                        # 等待IP地址更新
                        time.sleep(3)

                        # 获取IP地址
                        self.log("📡 正在获取WAN IP地址...")
                        ip_element = page.wait_for_selector("#wanIpLbl", timeout=5000)
                        if ip_element:
                            ip_address = ip_element.inner_text()
                            self.log(f"📋 获取到IP地址: {ip_address}")
                            
                            if ip_address and ip_address != "0.0.0.0" and ip_address != "0.0.0.0 ":
                                self.log("=" * 50)
                                self.log("✅ 拨号成功！")
                                self.log(f"已获取IP地址: {ip_address}")
                                self.log("=" * 50)

                                # 更新进度：连接成功
                                self.update_progress(100, "连接成功！")

                                self.update_status(f"连接成功！IP: {ip_address}")
                                connection_success = True

                                # 隐藏窗口到系统托盘
                                self.log("🎉 连接成功！程序将在后台运行...")
                                self.log("💡 双击系统托盘图标可重新显示窗口")
                                self.log_queue.put("[HIDE_TO_TRAY]")

                                # 恢复按钮状态
                                self.update_button("connect", tk.DISABLED, "已连接")
                                self.update_button("disconnect", tk.NORMAL)
                                self.log("✅ 连接流程完成")
                                
                                # 更新托盘图标为"在线"
                                self.update_tray_icon("online")
                                
                                return
                            else:
                                if attempt < max_attempts:
                                    self.log(f"⚠️ 拨号未成功（IP={ip_address}），准备重试...")
                                    time.sleep(2)
                                else:
                                    self.log("⚠️ 多次尝试后仍无法获取有效IP")
                        else:
                            if attempt < max_attempts:
                                self.log(f"⚠️ 无法获取IP地址元素，准备重试...")
                                time.sleep(2)
                    except Exception as e:
                        if attempt < max_attempts:
                            self.log(f"⚠️ 验证连接时出错，准备重试...")
                            time.sleep(2)
                
                # 所有尝试都失败
                if not connection_success:
                    self.log("=" * 50)
                    self.log("❌ 拨号失败")
                    self.log("=" * 50)
                    self.log("可能的原因：")
                    self.log("• 宽带账号或密码错误")
                    self.log("• 网络线路故障")
                    self.log("• 路由器故障")
                    self.log("=" * 50)
                    self.update_status("拨号失败（已尝试3次）")

                    # 弹窗提示用户
                    error_msg = "拨号失败（已尝试3次）\n\n可能的原因：\n• 宽带账号或密码错误\n• 网络线路故障\n• 路由器故障\n\n请检查后重试"
                    self.log_queue.put(f"[SHOW_ERROR]{error_msg}")

        except Exception as e:
            self.log(f"❌ 发生错误: {e}")
            self.update_status("发生错误")

            # 弹窗提示用户
            error_msg = f"发生错误：{e}\n\n请检查：\n• 路由器是否正常工作\n• 网络连接是否正常\n• 程序是否有足够的权限"
            self.log_queue.put(f"[SHOW_ERROR]{error_msg}")

        # 恢复按钮状态
        self.log("🔄 正在恢复按钮状态...")
        self.update_button("connect", tk.NORMAL, "开始连接")
        self.update_button("disconnect", tk.NORMAL)
        self.stop_progress()
        self.log("✅ 按钮状态已恢复")

        # 更新托盘图标为"错误"（连接失败）
        self.update_tray_icon("error")

        # 清除保存的账号密码（连接失败后允许重新连接）
        self.saved_account = ""
        self.saved_password = ""
        self.log("✅ 已清除保存的账号密码，可以重新连接")


# ==================== 单实例检查 ====================
class SingleInstanceChecker:
    """确保程序只运行一个实例"""
    def __init__(self):
        self.mutex_handle = None
        # 使用全局命名空间和唯一标识符，确保互斥对象的唯一性
        # 格式：Global\\AppName_GUID，确保在所有会话中都是唯一的
        self.mutex_name = "Global\\TP_Link_Broadband_Dialer_Single_Instance_8F3D2A1C_7B4E_4F9A_A123_C456D789E012"
        
    def already_running(self):
        """检查是否已有实例在运行"""
        try:
            # 尝试创建或打开互斥对象
            # 使用 CreateMutexW，如果已存在则返回现有句柄
            self.mutex_handle = ctypes.windll.kernel32.CreateMutexW(None, False, self.mutex_name)
            
            if self.mutex_handle == 0:
                # 创建失败，可能有实例在运行
                print("Warning: Failed to create mutex handle")
                return True
            
            # 检查 GetLastError 是否为 ERROR_ALREADY_EXISTS (183)
            last_error = ctypes.windll.kernel32.GetLastError()
            if last_error == 183:
                # 互斥对象已存在，说明有实例在运行
                print(f"Program is already running (mutex already exists)")
                # 关闭句柄
                ctypes.windll.kernel32.CloseHandle(self.mutex_handle)
                self.mutex_handle = None
                return True
            
            # 成功创建新的互斥对象，这是第一个实例
            print(f"Single instance check passed (created new mutex)")
            return False
            
        except Exception as e:
            # 如果Windows API失败，记录错误但不阻止程序运行
            print(f"Warning: Single instance check failed: {e}")
            return False
    
    def release(self):
        """释放互斥锁"""
        try:
            if self.mutex_handle and self.mutex_handle != 0:
                ctypes.windll.kernel32.CloseHandle(self.mutex_handle)
                self.mutex_handle = None
                print("Mutex released successfully")
        except Exception as e:
            print(f"Warning: Failed to release mutex: {e}")


def main():
    # 单实例检查（静默拒绝，不弹出窗口）
    checker = SingleInstanceChecker()
    if checker.already_running():
        # 静默退出，不显示任何窗口
        print("Program is already running. Exiting silently...")
        sys.exit(0)
    
    # 注册退出时释放锁
    atexit.register(checker.release)
    
    try:
        root = tk.Tk()
        app = RouterLoginGUI(root)
        root.mainloop()
    except Exception as e:
        # 显示错误信息
        try:
            error_root = tk.Tk()
            error_root.withdraw()
            messagebox.showerror("启动错误", f"程序启动时发生错误：\n\n{e}")
            error_root.destroy()
        except:
            print(f"程序启动时发生错误：{e}")


if __name__ == "__main__":
    main()
