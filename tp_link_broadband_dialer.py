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
import io

# ========== 修复Windows控制台编码问题 ==========
# 在Windows系统上，设置控制台为UTF-8编码以支持emoji字符
if sys.platform == 'win32':
    try:
        # 尝试设置控制台代码页为UTF-8
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        # 重新配置stdout
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        # 如果设置失败，使用安全的输出方式
        pass

# 导入配置管理模块
from config_manager import ConfigManager

# 导入浏览器管理模块
from browser_manager import BrowserManager

# ========== 核心：强制程序只使用内置资源 ==========
def get_resource_path(relative_path):
    """获取PyInstaller打包后的内置资源路径（无论是否单文件）"""
    if hasattr(sys, '_MEIPASS'):
        # 单文件打包时，临时解压目录
        base_path = Path(sys._MEIPASS)
    else:
        # 开发环境，项目根目录
        base_path = Path(__file__).parent
    return str(base_path / relative_path)

# 禁用Playwright的自动更新
os.environ["PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD"] = "1"

# 创建浏览器管理器
browser_manager = BrowserManager()

def check_browser():
    """验证浏览器是否存在并返回路径"""
    # 尝试使用共享浏览器
    browser_path = browser_manager.get_browser_path()

    if browser_path:
        print(f"✅ 找到浏览器: {browser_path}")
        # 给浏览器添加执行权限（兼容老旧Windows）
        try:
            os.chmod(browser_path, 0o755)
        except:
            pass
        return browser_path

    # 如果找不到浏览器，返回None（让调用方处理）
    return None

# 检查浏览器是否存在
try:
    browser_exe = check_browser()
    if browser_exe:
        os.environ["CHROME_EXECUTABLE_PATH"] = browser_exe
        print(f"✅ 浏览器就绪: {browser_exe}")
    else:
        print("⚠️ 未找到浏览器")
        # 在开发环境中，只显示警告
        if not getattr(sys, 'frozen', False):
            print("⚠️ 开发环境：请先安装浏览器（运行 browser_manager.py）")
        else:
            # 打包后的环境，显示友好的错误提示
            print("❌ 浏览器未安装！")
            print("请重新安装程序或联系技术支持。")
except Exception as e:
    print(f"⚠️ 浏览器检查出错: {e}")
    browser_exe = None

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

        # 路由器配置（从配置文件读取）
        config_manager = ConfigManager()
        config = config_manager.get_config()

        # 获取路由器配置（如果配置无效则使用默认值）
        self.router_ip = config.get('router_ip', '')
        self.router_password = config.get('router_password', '')

        # 如果没有配置 IP，使用默认值（首次运行时会显示配置向导）
        if not self.router_ip:
            self.router_ip = '192.168.1.1'

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

        # 设置焦点到账号输入框
        self.account_entry.focus()
        
    def on_closing(self):
        """窗口关闭事件处理"""
        # 如果有托盘图标，隐藏到托盘
        if TRAY_AVAILABLE and self.tray_icon:
            self.hide_to_tray()
            return

        # 直接关闭窗口
        # 注意：后台服务会在关机时自动清除路由器账号
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
    
    def create_widgets(self):
        # 隐藏的设置入口（双击标题上方的空白区域）
        secret_settings_frame = tk.Frame(self.root, height=20)
        secret_settings_frame.pack(pady=(0, 0))
        secret_settings_frame.pack_propagate(False)  # 防止frame被内容压缩

        # 添加一个几乎透明的Label作为触发区域
        secret_trigger = tk.Label(
            secret_settings_frame,
            text="",  # 空文本，看起来是空白
            cursor="arrow",  # 鼠标样式保持默认
            bg=self.root.cget("bg")  # 背景色与窗口背景一致
        )
        secret_trigger.pack(fill=tk.BOTH, expand=True)
        # 绑定双击事件
        secret_trigger.bind("<Double-Button-1>", lambda e: self.show_settings())

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
        
        # 提示文字（蓝色，在两个按钮下方，居中显示）
        hint_label = tk.Label(
            self.root,
            text="提示：使用完成后可点击断开按钮清除账号\n系统关机时后台服务会自动清理路由器账号",
            font=("Microsoft YaHei", 9, "bold"),
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

        # 状态栏（包含设置按钮）
        status_frame = tk.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_label = tk.Label(
            status_frame,
            text="就绪 | 双击进度条可查看运行日志",
            font=("Microsoft YaHei", 9),
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 设置按钮（更明显）
        settings_button = tk.Button(
            status_frame,
            text="⚙️ 设置",
            command=self.show_settings,
            font=("Microsoft YaHei", 9, "bold"),
            width=8,
            bg="#f0f0f0",
            relief=tk.RAISED
        )
        settings_button.pack(side=tk.RIGHT, padx=2, pady=2)
        
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

    def show_settings(self):
        """显示设置对话框"""
        result = show_reconfig_dialog(self.root)
        if result:
            # 如果配置已更新，重新加载配置
            config_manager = ConfigManager()
            config = config_manager.get_config()
            self.router_ip = config.get('router_ip', '')
            self.router_password = config.get('router_password', '')
            self.log("✅ 路由器配置已更新")
    
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
                
                # 获取内置浏览器路径
                executable_path = None
                try:
                    executable_path = check_browser()
                    self.log(f"✅ 使用内置浏览器: {executable_path}")
                except RuntimeError as e:
                    self.log(f"⚠️ {e}")
                    # 在开发环境中，使用系统默认浏览器
                    if not getattr(sys, 'frozen', False):
                        self.log("⚠️ 开发环境：使用系统默认浏览器")
                    else:
                        # 打包后的环境，必须有浏览器
                        raise
                
                # 启动浏览器（使用适配所有环境的参数）
                launch_options = {
                    'headless': True,  # 无头模式，无界面，兼容所有环境
                    'slow_mo': 300,
                    'args': [
                        "--no-sandbox",  # 禁用沙箱，Win7/低权限环境必备
                        "--disable-gpu",  # 禁用GPU加速，避免显卡驱动问题
                        "--disable-dev-shm-usage",  # 禁用共享内存，适配低配机器
                        "--disable-extensions",  # 禁用扩展，减少依赖
                        "--disable-plugins",  # 禁用插件
                        "--lang=zh-CN",  # 强制中文，无需语言包
                        "--disable-web-security",  # 禁用Web安全策略，避免跨域问题
                        "--disable-features=VizDisplayCompositor",  # 禁用某些特性，提高兼容性
                    ],
                    'handle_sigint': False,  # 避免用户按Ctrl+C崩溃
                }
                
                if executable_path:
                    launch_options['executable_path'] = executable_path
                
                browser = p.chromium.launch(**launch_options)
                context = browser.new_context()
                page = context.new_page()

                # 设置路由来监听所有请求
                page.route("**/*", capture_stok)

                self.log("🔌 正在访问路由器管理页面...")
                self.log(f"   目标: http://{self.router_ip}/")
                page.goto(f"http://{self.router_ip}/")

                # ===== 登录 =====
                self.log("🔑 等待登录密码输入框...")
                page.wait_for_selector("input[type='password']", timeout=10000)
                self.log("   找到密码输入框，正在填写...")
                page.fill("input[type='password']", self.router_password)
                self.log("   已填写密码，正在提交登录...")
                page.keyboard.press("Enter")

                self.log("⏳ 正在验证登录，等待token响应...")
                
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
                self.update_progress(40, "正在访问上网设置......")

                # 访问上网设置页面
                self.log("🚀 正在访问上网设置页面...")

                # 使用菜单导航（确保页面完整加载）
                # 注意：直接URL访问虽然能找到输入框，但页面加载不完整，导致填写无效
                self.log("   方式: 菜单导航（确保页面完整加载）")
                self.log(f"   📍 返回主页: http://{self.router_ip}/")
                page.goto(f"http://{self.router_ip}/")
                time.sleep(2)

                try:
                    router_set_btn = page.wait_for_selector("#routerSetMbtn", timeout=3000)
                    if router_set_btn:
                        router_set_btn.click()
                        time.sleep(2)
                except:
                    pass

                try:
                    network_menu = page.wait_for_selector("#network_rsMenu", timeout=3000)
                    if network_menu:
                        network_menu.click()
                        time.sleep(2)
                except:
                    pass

                # 断开连接
                self.log("🔌 正在断开网络连接...")
                self.log("   按钮: #disconnect")
                try:
                    disconnect_btn = page.wait_for_selector("#disconnect", timeout=5000)
                    if disconnect_btn:
                        self.log("   ✅ 找到断开按钮，正在点击...")
                        disconnect_btn.click()
                        self.log("   ✅ 已点击断开按钮")
                        time.sleep(2)
                    else:
                        self.log("   ⚠️ 断开按钮不存在（可能已经断开）")
                except Exception as e:
                    self.log(f"   ⚠️ 查找/点击断开按钮失败: {e}")

                # 更新进度：断开完成，正在清除
                self.update_progress(60, "正在清除账号密码......")

                # 清除账号密码
                self.log("🗑️ 正在清除账号密码...")
                try:
                    # 清空账号
                    self.log("   📝 清空账号输入框 (#name)...")
                    name_input = page.wait_for_selector("#name", timeout=5000)
                    if name_input:
                        name_input.fill("")
                        self.log("   ✅ 账号输入框已清空")
                    else:
                        self.log("   ⚠️ 未找到账号输入框")

                    # 清空密码
                    self.log("   📝 清空密码输入框 (#psw)...")
                    psw_input = page.wait_for_selector("#psw", timeout=5000)
                    if psw_input:
                        psw_input.fill("")
                        self.log("   ✅ 密码输入框已清空")
                    else:
                        self.log("   ⚠️ 未找到密码输入框")

                    # 验证账号密码是否真的被清除了
                    self.log("   🔍 正在验证账号密码是否已清除...")
                    time.sleep(1)
                    name_value = name_input.input_value() if name_input else ""
                    psw_value = psw_input.input_value() if psw_input else ""
                    self.log(f"   📋 验证结果：账号=[{name_value}], 密码=[{psw_value}]")

                    if not name_value and not psw_value:
                        self.log("✅ 账号密码已清除")
                        disconnect_success = True
                    else:
                        self.log(f"❌ 清除失败：账号=[{name_value}], 密码=[{psw_value}]")
                        disconnect_success = False
                except Exception as e:
                    self.log(f"⚠️ 清除账号密码时出错: {e}")
                    import traceback
                    self.log(f"详细错误: {traceback.format_exc()}")
                    disconnect_success = False

                # 更新进度：清除完成，正在保存
                self.update_progress(90, "正在保存配置......")

                # 保存（保存空账号密码）
                self.log("💾 正在保存配置（空账号密码）...")
                self.log("   按钮: #save")
                try:
                    save_btn = page.wait_for_selector("#save", timeout=5000)
                    if save_btn:
                        self.log("   ✅ 找到保存按钮，正在点击...")
                        save_btn.click()
                        self.log("   ✅ 已点击保存按钮")
                        time.sleep(2)
                    else:
                        self.log("   ⚠️ 未找到保存按钮")
                except Exception as e:
                    self.log(f"   ⚠️ 保存配置时出错: {e}")

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
                
                # 获取内置浏览器路径
                executable_path = None
                try:
                    executable_path = check_browser()
                    self.log(f"✅ 使用内置浏览器: {executable_path}")
                except RuntimeError as e:
                    self.log(f"⚠️ {e}")
                    # 在开发环境中，使用系统默认浏览器
                    if not getattr(sys, 'frozen', False):
                        self.log("⚠️ 开发环境：使用系统默认浏览器")
                    else:
                        # 打包后的环境，必须有浏览器
                        raise
                
                # 启动浏览器（使用适配所有环境的参数）
                launch_options = {
                    'headless': True,  # 无头模式，无界面，兼容所有环境
                    'slow_mo': 300,
                    'args': [
                        "--no-sandbox",  # 禁用沙箱，Win7/低权限环境必备
                        "--disable-gpu",  # 禁用GPU加速，避免显卡驱动问题
                        "--disable-dev-shm-usage",  # 禁用共享内存，适配低配机器
                        "--disable-extensions",  # 禁用扩展，减少依赖
                        "--disable-plugins",  # 禁用插件
                        "--lang=zh-CN",  # 强制中文，无需语言包
                        "--disable-web-security",  # 禁用Web安全策略，避免跨域问题
                        "--disable-features=VizDisplayCompositor",  # 禁用某些特性，提高兼容性
                    ],
                    'handle_sigint': False,  # 避免用户按Ctrl+C崩溃
                }
                
                if executable_path:
                    launch_options['executable_path'] = executable_path
                
                browser = p.chromium.launch(**launch_options)
                context = browser.new_context()
                page = context.new_page()

                # 设置路由来监听所有请求
                page.route("**/*", capture_stok)

                self.log("🔌 正在访问路由器管理页面...")
                self.log(f"   目标: http://{self.router_ip}/")
                self.update_status("正在登录路由器...")
                page.goto(f"http://{self.router_ip}/")

                # ===== 登录 =====
                self.log("🔑 等待登录密码输入框...")
                page.wait_for_selector("input[type='password']", timeout=10000)
                self.log("   找到密码输入框，正在填写...")
                page.fill("input[type='password']", self.router_password)
                self.log("   已填写密码，正在提交登录...")
                page.keyboard.press("Enter")

                self.log("⏳ 正在验证登录，等待token响应...")
                
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
                self.update_progress(40, "正在访问上网设置......")

                # 访问上网设置页面
                self.log("🚀 正在访问上网设置页面...")

                # 使用菜单导航（确保页面完整加载）
                # 注意：直接URL访问虽然能找到输入框，但页面加载不完整，导致填写无效
                self.log("   方式: 菜单导航（确保页面完整加载）")
                self.log(f"   📍 返回主页: http://{self.router_ip}/")
                page.goto(f"http://{self.router_ip}/")
                time.sleep(2)

                try:
                    router_set_btn = page.wait_for_selector("#routerSetMbtn", timeout=3000)
                    if router_set_btn:
                        router_set_btn.click()
                        time.sleep(2)
                except:
                    pass

                try:
                    network_menu = page.wait_for_selector("#network_rsMenu", timeout=3000)
                    if network_menu:
                        network_menu.click()
                        time.sleep(2)
                except:
                    pass

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

                # ===== 设置随机WAN口MAC地址（已禁用） =====
                # 注意：随机MAC地址可能导致拨号失败（运营商MAC绑定）
                # 如需启用，请取消下方注释
                self.log("⏭️ 跳过MAC地址设置（使用路由器默认MAC）")
                self.log("💡 提示：如需随机MAC功能，可在设置中开启")

                # try:
                #     # 等待页面完全加载
                #     self.log("   ⏳ 等待页面稳定（2秒）...")
                #     time.sleep(2)
                #
                #     # 生成随机MAC地址
                #     import random
                #     mac_bytes = [0x02, random.randint(0x00, 0xff), random.randint(0x00, 0xff),
                #                 random.randint(0x00, 0xff), random.randint(0x00, 0xff), random.randint(0x00, 0xff)]
                #     # 使用横线分隔（与路由器原始格式一致）
                #     random_mac = "-".join([f"{b:02X}" for b in mac_bytes])
                #     self.log(f"📍 生成随机MAC: {random_mac}")
                #     self.log(f"   选择器: #wanMac")
                #
                #     # 检查MAC地址输入框是否存在
                #     self.log("🔍 查找MAC地址输入框 (#wanMac)...")
                #     mac_input_exists = page.query_selector("#wanMac")
                #     if not mac_input_exists:
                #         self.log("⚠️ 未找到 #wanMac 输入框，跳过MAC设置")
                #         raise Exception("MAC输入框不存在")
                #
                #     # 获取当前MAC值
                #     try:
                #         current_mac = page.input_value("#wanMac")
                #         self.log(f"📋 当前MAC地址: {current_mac}")
                #     except:
                #         self.log("📋 当前MAC地址: (空)")
                #         current_mac = ""
                #
                #     # 清空MAC输入框
                #     self.log("🗑️ 清空MAC输入框...")
                #     page.click("#wanMac")
                #     time.sleep(0.3)
                #     page.keyboard.press("Control+A")
                #     time.sleep(0.2)
                #     page.keyboard.press("Backspace")
                #     time.sleep(0.3)
                #
                #     # 输入新的MAC地址（逐字符输入，更可靠）
                #     self.log(f"⌨️ 输入新MAC地址: {random_mac}")
                #     self.log(f"   输入方式: 逐字符输入 (delay=50ms)")
                #     page.type("#wanMac", random_mac, delay=50)
                #     time.sleep(0.5)
                #
                #     # 验证MAC地址是否填写成功
                #     try:
                #         filled_mac = page.input_value("#wanMac")
                #         self.log(f"📋 填写后MAC: {filled_mac}")
                #
                #         # 统一转为大写比较
                #         if filled_mac.upper().strip() == random_mac.upper().strip():
                #             self.log("✅ MAC地址填写验证成功")
                #         else:
                #             self.log(f"⚠️ MAC地址验证失败")
                #             self.log(f"   期望: {random_mac}")
                #             self.log(f"   实际: {filled_mac}")
                #     except Exception as e:
                #         self.log(f"⚠️ 验证MAC地址时出错: {e}")
                #         filled_mac = None
                #
                #     # 如果MAC填写成功，点击保存按钮
                #     if filled_mac and filled_mac.upper().strip() == random_mac.upper().strip():
                #         # 点击高级设置保存按钮
                #         self.log("💾 正在保存MAC地址设置...")
                #         self.log("   按钮: #saveHighSet")
                #         save_btn_exists = page.query_selector("#saveHighSet")
                #         if save_btn_exists:
                #             page.click("#saveHighSet")
                #             self.log("✅ 已点击高级设置保存按钮")
                #
                #             # 等待保存完成
                #             self.log("⏳ 等待保存完成（5秒）...")
                #             time.sleep(5)
                #
                #             # 检查是否有错误提示
                #             try:
                #                 error_alert = page.query_selector(".alert-content, .error, #msg")
                #                 if error_alert and error_alert.is_visible():
                #                     error_text = error_alert.inner_text()
                #                     self.log(f"⚠️ 检测到错误提示: {error_text}")
                #             except:
                #                 pass
                #
                #             # 再次读取MAC地址验证是否保存成功
                #             try:
                #                 # 重新获取输入框元素（页面可能刷新）
                #                 self.log("🔍 验证保存结果...")
                #                 wan_mac_after = page.wait_for_selector("#wanMac", timeout=3000)
                #                 if wan_mac_after:
                #                     saved_mac = wan_mac_after.input_value()
                #                     self.log(f"📋 保存后MAC: {saved_mac}")
                #
                #                     if saved_mac.upper().strip() == random_mac.upper().strip():
                #                         self.log("✅ MAC地址保存成功且已验证")
                #                     else:
                #                         self.log(f"⚠️ MAC地址保存后未更新")
                #                         self.log(f"   期望: {random_mac}")
                #                         self.log(f"   实际: {saved_mac}")
                #                         self.log("💡 提示: 某些路由器需要重启WAN口才能使MAC地址生效")
                #                 else:
                #                     self.log("⚠️ 保存后找不到MAC输入框")
                #             except Exception as e:
                #                 self.log(f"⚠️ 验证保存结果时出错: {e}")
                #         else:
                #             self.log("⚠️ 未找到 #saveHighSet 按钮")
                #
                # except Exception as e:
                #     self.log(f"⚠️ 设置MAC地址时出错: {e}")
                #     import traceback
                #     self.log(f"详细错误: {traceback.format_exc()}")
                #     self.log("继续执行拨号流程...")

                # ===== 填写账号密码 =====
                self.log("📝 正在填写账号密码...")
                self.log(f"   账号: {broadband_user}")
                self.log(f"   密码: {'*' * len(broadband_pass)}")
                self.update_status("正在输入账号密码...")

                # 等待输入框出现
                try:
                    self.log("   🔍 等待账号输入框 (#name)...")
                    page.wait_for_selector("#name", timeout=10000)
                    self.log("   ✅ 找到账号输入框")

                    self.log("   🔍 等待密码输入框 (#psw)...")
                    page.wait_for_selector("#psw", timeout=5000)
                    self.log("   ✅ 找到密码输入框")
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
                self.log("   ⌨️ 填写账号...")
                page.fill("#name", "")
                page.fill("#name", broadband_user)
                self.log("   ✅ 账号已填写")

                # 清空并填写密码
                self.log("   ⌨️ 填写密码...")
                page.fill("#psw", "")
                page.fill("#psw", broadband_pass)
                self.log("   ✅ 密码已填写")

                # 触发 blur 事件（重要）
                self.log("   触发输入框失焦事件...")
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
                    self.log("   按钮: #save")
                    try:
                        page.click("#save")
                        self.log("   ✅ 已点击保存按钮 (#save)")
                    except Exception as e:
                        self.log(f"   ⚠️ 点击#save失败: {e}")
                        self.log("   🔄 尝试备用按钮...")
                        try:
                            page.click("button:has-text('保存'), button:has-text('连接'), .save-btn")
                            self.log("   ✅ 已点击备用按钮")
                        except Exception as e2:
                            self.log(f"   ⚠️ 点击备用按钮也失败: {e2}")
                            self.log("   🔄 最后尝试点击#save...")
                            page.click("#save")
                            self.log("   ✅ 再次尝试点击#save")

                    self.log("⏳ 正在等待拨号完成（10秒）...")
                    self.log("   等待IP地址分配和连接建立...")
                    time.sleep(10)

                    # ===== 检查连接状态 =====
                    self.update_status(f"正在验证连接（第{attempt}次）...")
                    self.log("🔍 正在检查连接状态...")
                    try:
                        # 等待IP地址更新
                        self.log("   ⏳ 等待IP地址更新（3秒）...")
                        time.sleep(3)

                        # 获取IP地址
                        self.log("📡 正在获取WAN IP地址...")
                        self.log("   选择器: #wanIpLbl")
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


def show_config_wizard():
    """显示配置向导"""
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
        font=("Microsoft YaHei", 18, "bold"),
        fg="#333333"
    )
    title_label.pack(pady=(20, 10))

    # 副标题
    subtitle_label = tk.Label(
        wizard_root,
        text="首次使用需要配置路由器信息",
        font=("Microsoft YaHei", 11),
        fg="#666666"
    )
    subtitle_label.pack(pady=(0, 15))

    # 说明框
    info_frame = tk.Frame(wizard_root, bg="#E3F2FD", bd=1, relief=tk.SOLID)
    info_frame.pack(pady=10, padx=40, fill=tk.X)

    info_label = tk.Label(
        info_frame,
        text="ℹ️ 配置说明\n\n程序需要在关机时自动清理路由器账号\n请输入路由器的管理地址和管理员密码\n此信息将加密保存在本地",
        font=("Microsoft YaHei", 9),
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

    tk.Label(ip_frame, text="路由器IP地址：", font=("Microsoft YaHei", 10, "bold"), width=15, anchor=tk.W).pack(side=tk.LEFT, padx=5)
    ip_entry = tk.Entry(ip_frame, font=("Microsoft YaHei", 10), width=25)
    ip_entry.insert(0, "192.168.1.1")
    ip_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

    # 路由器密码输入框
    password_frame = tk.Frame(wizard_root)
    password_frame.pack(pady=10, padx=40, fill=tk.X)

    tk.Label(password_frame, text="路由器管理密码：", font=("Microsoft YaHei", 10, "bold"), width=15, anchor=tk.W).pack(side=tk.LEFT, padx=5)
    password_entry = tk.Entry(password_frame, font=("Microsoft YaHei", 10), width=25, show="●")
    password_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

    # 状态提示
    status_label = tk.Label(
        wizard_root,
        text="",
        font=("Microsoft YaHei", 9),
        fg="#4CAF50",
        wraplength=400
    )
    status_label.pack(pady=5)

    # 错误提示
    error_label = tk.Label(
        wizard_root,
        text="",
        font=("Microsoft YaHei", 9),
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

            # 延迟关闭，让用户看到成功消息
            wizard_root.after(1000, wizard_root.destroy)
        else:
            error_label.config(text="❌ 保存配置失败，请检查是否有写入权限")
            status_label.config(text="")

    def on_exit():
        """退出程序"""
        if result['save']:
            wizard_root.destroy()
        else:
            # 提示用户
            if messagebox.askyesno("确认退出", "未保存配置，程序将无法使用。\n\n确定要退出吗？"):
                wizard_root.destroy()

    # 绑定回车键到保存
    wizard_root.bind('<Return>', lambda e: validate_and_save())

    # 按钮区域
    button_frame = tk.Frame(wizard_root)
    button_frame.pack(pady=20)

    save_button = tk.Button(
        button_frame,
        text="✓ 保存并启动",
        command=validate_and_save,
        font=("Microsoft YaHei", 11, "bold"),
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
        font=("Microsoft YaHei", 10),
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
        font=("Microsoft YaHei", 8),
        fg="#999999"
    )
    footer_label.pack(side=tk.BOTTOM, pady=10)

    # 设置焦点
    ip_entry.focus()
    ip_entry.select_range(0, tk.END)

    wizard_root.mainloop()
    return result


def show_reconfig_dialog(parent_root):
    """显示重新配置对话框

    Returns:
        bool: 配置是否成功保存
    """
    dialog = tk.Toplevel(parent_root)
    dialog.title("路由器设置")
    dialog.geometry("450x300")
    dialog.resizable(False, False)
    dialog.transient(parent_root)
    dialog.grab_set()

    # 结果存储
    result = {'saved': False}

    # 标题
    title_label = tk.Label(
        dialog,
        text="路由器配置",
        font=("Microsoft YaHei", 14, "bold")
    )
    title_label.pack(pady=15)

    # 当前配置显示
    config_manager = ConfigManager()
    current_config = config_manager.get_config()

    # 路由器IP输入框
    ip_frame = tk.Frame(dialog)
    ip_frame.pack(pady=10, padx=30, fill=tk.X)

    tk.Label(ip_frame, text="路由器IP地址:", font=("Microsoft YaHei", 10)).pack(side=tk.LEFT, padx=5)
    ip_entry = tk.Entry(ip_frame, font=("Microsoft YaHei", 10), width=20)
    ip_entry.insert(0, current_config.get('router_ip', '192.168.1.1'))
    ip_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

    # 路由器密码输入框
    password_frame = tk.Frame(dialog)
    password_frame.pack(pady=10, padx=30, fill=tk.X)

    tk.Label(password_frame, text="路由器管理密码:", font=("Microsoft YaHei", 10)).pack(side=tk.LEFT, padx=5)
    password_entry = tk.Entry(password_frame, font=("Microsoft YaHei", 10), width=20, show="*")
    password_entry.insert(0, current_config.get('router_password', ''))
    password_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

    # 错误提示
    error_label = tk.Label(
        dialog,
        text="",
        font=("Microsoft YaHei", 9),
        fg="red"
    )
    error_label.pack(pady=5)

    def validate_and_save():
        """验证并保存配置"""
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

        # 验证密码
        if not router_password:
            error_label.config(text="请输入路由器管理密码")
            return

        # 保存配置
        config = {
            'router_ip': router_ip,
            'router_password': router_password,
            'version': '1.0'
        }

        if config_manager.save_config(config):
            result['saved'] = True
            messagebox.showinfo("成功", "路由器配置已保存！\n\n新配置已立即生效。")
            dialog.destroy()
        else:
            error_label.config(text="保存配置失败，请重试")

    # 按钮区域
    button_frame = tk.Frame(dialog)
    button_frame.pack(pady=20)

    tk.Button(
        button_frame,
        text="保存",
        command=validate_and_save,
        font=("Microsoft YaHei", 10, "bold"),
        bg="#4CAF50",
        fg="white",
        width=12
    ).pack(side=tk.LEFT, padx=5)

    tk.Button(
        button_frame,
        text="取消",
        command=lambda: dialog.destroy(),
        font=("Microsoft YaHei", 10),
        width=12
    ).pack(side=tk.LEFT, padx=5)

    # 等待对话框关闭
    dialog.wait_window()
    return result['saved']


def main():
    # 检查是否已配置
    config_manager = ConfigManager()
    if not config_manager.is_configured():
        # 首次运行，显示配置向导
        result = show_config_wizard()
        if not result or not result['save']:
            # 用户未保存配置，退出
            sys.exit(0)

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
