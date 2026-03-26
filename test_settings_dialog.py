# -*- coding: utf-8 -*-
"""测试设置对话框显示"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys

# Windows UTF-8控制台支持
if sys.platform == 'win32':
    import ctypes
    import io
    try:
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

def show_settings_dialog():
    """显示设置对话框"""
    dialog = tk.Toplevel()
    dialog.title("路由器配置")
    dialog.geometry("500x500")  # 增加高度
    dialog.resizable(False, False)

    # 模态对话框
    dialog.transient(dialog.master)
    dialog.grab_set()

    print("🔧 对话框尺寸: 500x500")

    # 标题
    title_label = tk.Label(
        dialog,
        text="路由器配置",
        font=("Microsoft YaHei", 14, "bold")
    )
    title_label.pack(pady=15)
    print("✅ 添加标题")

    # 模拟输入框
    ip_frame = tk.Frame(dialog)
    ip_frame.pack(pady=10, padx=30, fill=tk.X)

    tk.Label(ip_frame, text="路由器IP地址:", font=("Microsoft YaHei", 10)).pack(side=tk.LEFT, padx=5)
    ip_entry = tk.Entry(ip_frame, font=("Microsoft YaHei", 10), width=20)
    ip_entry.insert(0, "192.168.1.1")
    ip_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    print("✅ 添加IP输入框")

    # 密码输入框
    password_frame = tk.Frame(dialog)
    password_frame.pack(pady=10, padx=30, fill=tk.X)

    tk.Label(password_frame, text="路由器管理密码:", font=("Microsoft YaHei", 10)).pack(side=tk.LEFT, padx=5)
    password_entry = tk.Entry(password_frame, font=("Microsoft YaHei", 10), width=20, show="*")
    password_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    print("✅ 添加密码输入框")

    # 分隔线
    separator_frame = tk.Frame(dialog, height=2, bg="#CCCCCC")
    separator_frame.pack(pady=10, padx=30, fill=tk.X)
    print("✅ 添加分隔线")

    # 高级选项容器
    advanced_container = tk.Frame(dialog)
    advanced_container.pack(pady=5, padx=30, fill=tk.X)

    # MAC模式选择
    mac_mode_label = tk.Label(
        advanced_container,
        text="MAC地址模式:",
        font=("Microsoft YaHei", 10)
    )
    mac_mode_label.pack(anchor=tk.W, pady=(0, 5))

    mac_mode_var = tk.StringVar(value="使用路由器的MAC地址")
    mac_mode_combobox = ttk.Combobox(
        advanced_container,
        textvariable=mac_mode_var,
        values=[
            "使用路由器的MAC地址",
            "使用当前管理PC的MAC地址",
            "使用随机MAC地址"
        ],
        state="readonly",
        font=("Microsoft YaHei", 9),
        width=45
    )
    mac_mode_combobox.pack(fill=tk.X, pady=(0, 10))
    print("✅ 添加MAC模式下拉框")

    # 错误提示
    error_label = tk.Label(
        dialog,
        text="",
        font=("Microsoft YaHei", 9),
        fg="red"
    )
    error_label.pack(pady=5)
    print("✅ 添加错误提示标签")

    # 按钮区域
    button_frame = tk.Frame(dialog)
    button_frame.pack(pady=20)
    print("✅ 添加按钮框架")

    def on_save():
        print("💾 保存按钮被点击!")
        messagebox.showinfo("测试", "保存按钮可见且可点击!")
        dialog.destroy()

    def on_cancel():
        print("❌ 取消按钮被点击!")
        dialog.destroy()

    tk.Button(
        button_frame,
        text="保存",
        command=on_save,
        font=("Microsoft YaHei", 10, "bold"),
        bg="#4CAF50",
        fg="white",
        width=12
    ).pack(side=tk.LEFT, padx=5)
    print("✅ 添加保存按钮")

    tk.Button(
        button_frame,
        text="取消",
        command=on_cancel,
        font=("Microsoft YaHei", 10),
        width=12
    ).pack(side=tk.LEFT, padx=5)
    print("✅ 添加取消按钮")

    print("\n" + "="*60)
    print("📏 布局分析:")
    print("  标题: pady=15 (约30px)")
    print("  IP框: pady=10 (约50px)")
    print("  密码框: pady=10 (约50px)")
    print("  分隔线: pady=10 (约20px)")
    print("  高级区: pady=5 (约60px)")
    print("  错误提示: pady=5 (约20px)")
    print("  按钮区: pady=20 (约60px)")
    print("  预估总高度: ~290px 内容区域")
    print("  对话框高度: 500px")
    print("  预留空间: 210px ✓ 应该足够!")
    print("="*60)
    print("\n✅ 设置对话框已打开!")
    print("👀 请检查:")
    print("  1. 能否看到完整的MAC模式下拉框")
    print("  2. 能否看到保存和取消按钮")
    print("  3. 点击保存按钮是否有效")
    print("\n按Ctrl+C退出测试...")

if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    print("="*60)
    print("🧪 设置对话框显示测试")
    print("="*60)

    # 显示对话框
    show_settings_dialog()

    root.mainloop()
