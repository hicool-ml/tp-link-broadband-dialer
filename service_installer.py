#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TP-Link路由器账号清理服务 - 图形化安装工具

提供简单的图形界面来安装和管理清理服务。
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import sys
from pathlib import Path

# 导入配置管理模块
from config_manager import ConfigManager

class ServiceInstallerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TP-Link路由器账号清理服务 - 管理工具")
        self.root.geometry("600x450")
        self.root.resizable(False, False)

        # 服务名称
        self.service_name = "TPLinkShutdownCleanup"

        self.create_widgets()
        self.update_service_status()

    def create_widgets(self):
        # 标题
        title_label = tk.Label(
            self.root,
            text="TP-Link路由器账号清理服务",
            font=("Microsoft YaHei", 16, "bold")
        )
        title_label.pack(pady=15)

        # 说明
        desc_label = tk.Label(
            self.root,
            text="此服务在系统关机时自动清除路由器中的宽带账号密码",
            font=("Microsoft YaHei", 10),
            fg="#666666"
        )
        desc_label.pack(pady=5)

        # 状态区域
        status_frame = tk.LabelFrame(self.root, text="服务状态", font=("Microsoft YaHei", 10, "bold"))
        status_frame.pack(pady=15, padx=20, fill=tk.X)

        self.status_label = tk.Label(
            status_frame,
            text="正在查询...",
            font=("Microsoft YaHei", 12),
            fg="#666666"
        )
        self.status_label.pack(pady=10)

        # 按钮区域
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=15)

        self.install_button = tk.Button(
            button_frame,
            text="安装服务",
            command=self.install_service,
            font=("Microsoft YaHei", 10),
            bg="#4CAF50",
            fg="white",
            width=15,
            height=2
        )
        self.install_button.pack(side=tk.LEFT, padx=5)

        self.remove_button = tk.Button(
            button_frame,
            text="卸载服务",
            command=self.remove_service,
            font=("Microsoft YaHei", 10),
            bg="#f44336",
            fg="white",
            width=15,
            height=2
        )
        self.remove_button.pack(side=tk.LEFT, padx=5)

        # 第二行按钮
        button_frame2 = tk.Frame(self.root)
        button_frame2.pack(pady=5)

        self.start_button = tk.Button(
            button_frame2,
            text="启动服务",
            command=self.start_service,
            font=("Microsoft YaHei", 10),
            bg="#2196F3",
            fg="white",
            width=15,
            height=2
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(
            button_frame2,
            text="停止服务",
            command=self.stop_service,
            font=("Microsoft YaHei", 10),
            bg="#FF9800",
            fg="white",
            width=15,
            height=2
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # 日志区域
        log_frame = tk.LabelFrame(self.root, text="操作日志", font=("Microsoft YaHei", 10, "bold"))
        log_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            font=("Consolas", 9),
            height=10,
            wrap=tk.WORD
        )
        self.log_text.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)

        # 底部按钮
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(pady=10)

        tk.Button(
            bottom_frame,
            text="刷新状态",
            command=self.update_service_status,
            font=("Microsoft YaHei", 9),
            width=12
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            bottom_frame,
            text="清空日志",
            command=self.clear_log,
            font=("Microsoft YaHei", 9),
            width=12
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            bottom_frame,
            text="查看服务日志",
            command=self.view_service_log,
            font=("Microsoft YaHei", 9),
            width=12
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            bottom_frame,
            text="路由器设置",
            command=self.show_router_config,
            font=("Microsoft YaHei", 9),
            width=12
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            bottom_frame,
            text="退出",
            command=self.root.quit,
            font=("Microsoft YaHei", 9),
            width=12
        ).pack(side=tk.LEFT, padx=5)

    def log(self, message):
        """添加日志"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)

    def run_command(self, command):
        """运行命令并返回输出"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=30
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return -1, "", str(e)

    def update_service_status(self):
        """更新服务状态"""
        self.log("正在查询服务状态...")

        # 查询服务状态
        returncode, stdout, stderr = self.run_command(f'sc query {self.service_name}')

        if returncode == 0:
            # 服务已安装
            if "RUNNING" in stdout:
                status = "正在运行"
                color = "#4CAF50"
            elif "STOPPED" in stdout:
                status = "已停止"
                color = "#f44336"
            else:
                status = "状态未知"
                color = "#FF9800"

            self.status_label.config(text=f"✓ 服务已安装 - {status}", fg=color)
            self.install_button.config(state=tk.DISABLED)
            self.remove_button.config(state=tk.NORMAL)
            self.start_button.config(state=tk.NORMAL if "STOPPED" in stdout else tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL if "RUNNING" in stdout else tk.DISABLED)

            self.log(f"服务状态: {status}")
        else:
            # 服务未安装
            self.status_label.config(text="× 服务未安装", fg="#f44336")
            self.install_button.config(state=tk.NORMAL)
            self.remove_button.config(state=tk.DISABLED)
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.DISABLED)

            self.log("服务未安装")

    def install_service(self):
        """安装服务"""
        self.log("=" * 50)
        self.log("正在安装服务...")
        self.log("=" * 50)

        def install():
            returncode, stdout, stderr = self.run_command(
                f'python shutdown_cleanup_service.py install'
            )

            self.root.after(0, lambda: self._install_complete(returncode, stdout, stderr))

        threading.Thread(target=install, daemon=True).start()

    def _install_complete(self, returncode, stdout, stderr):
        """安装完成"""
        if returncode == 0:
            self.log("✓ 服务安装成功")
            self.log(stdout)
            messagebox.showinfo("成功", "服务安装成功！\n\n请点击\"启动服务\"按钮启动服务。")
        else:
            self.log("✗ 服务安装失败")
            if stderr:
                self.log(stderr)
            messagebox.showerror("错误", f"服务安装失败！\n\n{stderr}")

        self.update_service_status()

    def remove_service(self):
        """卸载服务"""
        if not messagebox.askyesno("确认", "确定要卸载服务吗？\n\n卸载后关机时将无法自动清理路由器账号。"):
            return

        self.log("=" * 50)
        self.log("正在卸载服务...")
        self.log("=" * 50)

        def remove():
            returncode, stdout, stderr = self.run_command(
                f'python shutdown_cleanup_service.py remove'
            )

            self.root.after(0, lambda: self._remove_complete(returncode, stdout, stderr))

        threading.Thread(target=remove, daemon=True).start()

    def _remove_complete(self, returncode, stdout, stderr):
        """卸载完成"""
        if returncode == 0:
            self.log("✓ 服务卸载成功")
            self.log(stdout)
            messagebox.showinfo("成功", "服务卸载成功！")
        else:
            self.log("✗ 服务卸载失败")
            if stderr:
                self.log(stderr)
            messagebox.showerror("错误", f"服务卸载失败！\n\n{stderr}")

        self.update_service_status()

    def start_service(self):
        """启动服务"""
        self.log("正在启动服务...")

        def start():
            returncode, stdout, stderr = self.run_command(
                f'net start {self.service_name}'
            )

            self.root.after(0, lambda: self._start_complete(returncode, stdout, stderr))

        threading.Thread(target=start, daemon=True).start()

    def _start_complete(self, returncode, stdout, stderr):
        """启动完成"""
        if returncode == 0:
            self.log("✓ 服务启动成功")
            messagebox.showinfo("成功", "服务启动成功！\n\n服务现在正在后台运行。")
        else:
            self.log("✗ 服务启动失败")
            messagebox.showerror("错误", f"服务启动失败！\n\n{stdout}")

        self.update_service_status()

    def stop_service(self):
        """停止服务"""
        self.log("正在停止服务...")

        def stop():
            returncode, stdout, stderr = self.run_command(
                f'net stop {self.service_name}'
            )

            self.root.after(0, lambda: self._stop_complete(returncode, stdout, stderr))

        threading.Thread(target=stop, daemon=True).start()

    def _stop_complete(self, returncode, stdout, stderr):
        """停止完成"""
        if returncode == 0:
            self.log("✓ 服务停止成功")
            messagebox.showinfo("成功", "服务已停止。")
        else:
            self.log("✗ 服务停止失败")
            messagebox.showerror("错误", f"服务停止失败！\n\n{stdout}")

        self.update_service_status()

    def view_service_log(self):
        """查看服务日志"""
        import tempfile
        log_dir = Path(tempfile.gettempdir()) / 'tplink_cleanup'
        log_file = log_dir / 'cleanup_service.log'

        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 创建新窗口显示日志
                log_window = tk.Toplevel(self.root)
                log_window.title("服务日志")
                log_window.geometry("800x600")

                log_text = scrolledtext.ScrolledText(
                    log_window,
                    font=("Consolas", 9),
                    wrap=tk.WORD
                )
                log_text.pack(fill=tk.BOTH, expand=True)
                log_text.insert(1.0, content)
                log_text.config(state=tk.DISABLED)

            except Exception as e:
                messagebox.showerror("错误", f"无法读取日志文件：\n\n{e}")
        else:
            messagebox.showinfo("提示", f"日志文件不存在：\n\n{log_file}\n\n可能服务尚未运行。")

    def show_router_config(self):
        """显示路由器配置对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("路由器设置")
        dialog.geometry("450x300")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

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
                messagebox.showinfo("成功", "路由器配置已保存！\n\n请重启服务使配置生效。")
                self.log("路由器配置已更新")
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
            command=dialog.destroy,
            font=("Microsoft YaHei", 10),
            width=12
        ).pack(side=tk.LEFT, padx=5)


def main():
    root = tk.Tk()
    app = ServiceInstallerGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
