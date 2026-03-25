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
        self.status_label = ttk.Label(status_frame, text="就绪", foreground="green")
        self.status_label.pack(side=tk.LEFT, padx=5)

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
            text="重新连接",
            command=self.reconnect,
            width=20,
            state=tk.DISABLED
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
        """重新连接（功能待实现）"""
        self.log("[WARNING] 重新连接功能尚未实现")
        messagebox.showinfo("提示", "重新连接功能将在后续版本中实现")

    def quit_app(self):
        """退出应用"""
        if messagebox.askyesno("确认退出", "确定要退出吗？"):
            self.root.destroy()


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

    # 运行主循环
    root.mainloop()


if __name__ == '__main__':
    main()
