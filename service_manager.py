#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TP-Link宽带拨号服务管理工具

提供图形界面来管理TP-Link宽带拨号服务。
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
from pathlib import Path


class ServiceManager:
    """服务管理器"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("TP-Link宽带拨号服务管理")
        self.root.geometry("500x400")
        
        # 设置图标
        try:
            icon_path = self.get_resource_path("app.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass
        
        self.setup_ui()
        self.refresh_status()
        
    def get_resource_path(self, relative_path):
        """获取资源路径（支持PyInstaller打包）"""
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    
    def setup_ui(self):
        """设置UI"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置行列权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # 标题
        title_label = ttk.Label(
            main_frame,
            text="TP-Link宽带拨号服务",
            font=("Microsoft YaHei", 16, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # 服务状态
        status_frame = ttk.LabelFrame(main_frame, text="服务状态", padding="10")
        status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_label = ttk.Label(
            status_frame,
            text="正在查询...",
            font=("Microsoft YaHei", 12)
        )
        self.status_label.grid(row=0, column=0, pady=10)
        
        # 服务信息
        info_frame = ttk.LabelFrame(main_frame, text="服务信息", padding="10")
        info_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        info_frame.columnconfigure(1, weight=1)
        
        info_text = """
服务名称: TPLinkBroadbandDialer
显示名称: TP-Link宽带拨号服务
启动类型: 自动
功能: 在关机前自动断开TP-Link路由器拨号并清除账号信息

作为系统服务运行的优势:
• 关机优先级高，可以可靠拦截关机事件
• 关机超时时间长（默认30秒，最长3分钟）
• 无需用户登录即可自动运行
• 与用户会话分离，不受用户注销影响
        """.strip()
        
        info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT)
        info_label.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # 操作按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, pady=(0, 10))
        
        self.install_button = ttk.Button(
            button_frame,
            text="安装服务",
            command=self.install_service,
            width=15
        )
        self.install_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.start_button = ttk.Button(
            button_frame,
            text="启动服务",
            command=self.start_service,
            width=15
        )
        self.start_button.grid(row=0, column=1, padx=5, pady=5)
        
        self.stop_button = ttk.Button(
            button_frame,
            text="停止服务",
            command=self.stop_service,
            width=15
        )
        self.stop_button.grid(row=1, column=0, padx=5, pady=5)
        
        self.remove_button = ttk.Button(
            button_frame,
            text="卸载服务",
            command=self.remove_service,
            width=15
        )
        self.remove_button.grid(row=1, column=1, padx=5, pady=5)
        
        # 刷新按钮
        refresh_button = ttk.Button(
            main_frame,
            text="刷新状态",
            command=self.refresh_status
        )
        refresh_button.grid(row=4, column=0, pady=(0, 10))
        
        # 日志按钮
        log_button = ttk.Button(
            main_frame,
            text="查看日志",
            command=self.show_log
        )
        log_button.grid(row=5, column=0, pady=(0, 10))
        
        # 控制面板按钮
        control_button = ttk.Button(
            main_frame,
            text="打开控制面板",
            command=self.open_control_panel
        )
        control_button.grid(row=6, column=0)
        
    def run_command(self, command, args):
        """运行命令"""
        try:
            full_command = [sys.executable, command] + args
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def install_service(self):
        """安装服务"""
        if not messagebox.askyesno(
            "确认安装",
            "确定要安装TP-Link宽带拨号服务吗？\n\n"
            "服务将在系统启动时自动运行，并在关机前\n"
            "自动断开拨号和清除账号信息。"
        ):
            return
        
        success, stdout, stderr = self.run_command(
            "tp_link_broadband_dialer_service.py",
            ["install"]
        )
        
        if success:
            messagebox.showinfo(
                "安装成功",
                "服务安装成功！\n\n"
                "服务已设置为自动启动，\n"
                "请点击\"启动服务\"按钮启动服务。"
            )
            self.refresh_status()
        else:
            messagebox.showerror(
                "安装失败",
                f"服务安装失败！\n\n错误信息:\n{stderr}"
            )
    
    def remove_service(self):
        """卸载服务"""
        if not messagebox.askyesno(
            "确认卸载",
            "确定要卸载TP-Link宽带拨号服务吗？\n\n"
            "卸载后，关机时将不会自动断开拨号和清除账号。"
        ):
            return
        
        success, stdout, stderr = self.run_command(
            "tp_link_broadband_dialer_service.py",
            ["remove"]
        )
        
        if success:
            messagebox.showinfo(
                "卸载成功",
                "服务卸载成功！"
            )
            self.refresh_status()
        else:
            messagebox.showerror(
                "卸载失败",
                f"服务卸载失败！\n\n错误信息:\n{stderr}"
            )
    
    def start_service(self):
        """启动服务"""
        success, stdout, stderr = self.run_command(
            "tp_link_broadband_dialer_service.py",
            ["start"]
        )
        
        if success:
            messagebox.showinfo(
                "启动成功",
                "服务启动成功！\n\n"
                "服务正在后台运行，可以通过控制面板进行配置和监控。"
            )
            self.refresh_status()
        else:
            messagebox.showerror(
                "启动失败",
                f"服务启动失败！\n\n错误信息:\n{stderr}"
            )
    
    def stop_service(self):
        """停止服务"""
        success, stdout, stderr = self.run_command(
            "tp_link_broadband_dialer_service.py",
            ["stop"]
        )
        
        if success:
            messagebox.showinfo(
                "停止成功",
                "服务已停止！"
            )
            self.refresh_status()
        else:
            messagebox.showerror(
                "停止失败",
                f"服务停止失败！\n\n错误信息:\n{stderr}"
            )
    
    def refresh_status(self):
        """刷新状态"""
        try:
            import win32service
            import win32serviceutil
            
            status = win32serviceutil.QueryServiceStatus("TPLinkBroadbandDialer")
            
            state_map = {
                win32service.SERVICE_STOPPED: ("已停止", "red"),
                win32service.SERVICE_START_PENDING: ("正在启动", "orange"),
                win32service.SERVICE_STOP_PENDING: ("正在停止", "orange"),
                win32service.SERVICE_RUNNING: ("正在运行", "green"),
                win32service.SERVICE_CONTINUE_PENDING: ("正在继续", "orange"),
                win32service.SERVICE_PAUSE_PENDING: ("正在暂停", "orange"),
                win32service.SERVICE_PAUSED: ("已暂停", "orange"),
            }
            
            state_text, state_color = state_map.get(
                status[1],
                ("未知状态", "gray")
            )
            
            self.status_label.config(text=f"服务状态: {state_text}")
            
            # 更新按钮状态
            if status[1] == win32service.SERVICE_RUNNING:
                self.start_button.state(["disabled"])
                self.stop_button.state(["!disabled"])
            elif status[1] == win32service.SERVICE_STOPPED:
                self.start_button.state(["!disabled"])
                self.stop_button.state(["disabled"])
            else:
                self.start_button.state(["disabled"])
                self.stop_button.state(["disabled"])
                
        except Exception as e:
            self.status_label.config(text="服务未安装")
            self.start_button.state(["disabled"])
            self.stop_button.state(["disabled"])
    
    def show_log(self):
        """显示日志"""
        try:
            log_dir = Path(os.environ.get('TEMP', '/tmp')) / 'tplink_dialer'
            log_file = log_dir / 'service.log'
            
            if log_file.exists():
                os.startfile(log_file)
            else:
                messagebox.showinfo(
                    "日志文件",
                    "日志文件不存在。\n\n"
                    "请先启动服务，日志文件将在服务运行时自动创建。"
                )
        except Exception as e:
            messagebox.showerror(
                "打开日志失败",
                f"无法打开日志文件！\n\n错误信息:\n{str(e)}"
            )
    
    def open_control_panel(self):
        """打开控制面板"""
        try:
            if getattr(sys, 'frozen', False):
                # 打包后的EXE
                control_panel = os.path.join(
                    os.path.dirname(sys.executable),
                    'tp_link_broadband_dialer.exe'
                )
            else:
                # 开发环境
                control_panel = os.path.join(
                    os.path.dirname(__file__),
                    'tp_link_broadband_dialer.py'
                )
            
            if os.path.exists(control_panel):
                subprocess.Popen([control_panel])
            else:
                messagebox.showerror(
                    "打开失败",
                    "找不到控制面板程序！"
                )
        except Exception as e:
            messagebox.showerror(
                "打开失败",
                f"无法打开控制面板！\n\n错误信息:\n{str(e)}"
            )


def main():
    """主函数"""
    root = tk.Tk()
    app = ServiceManager(root)
    root.mainloop()


if __name__ == '__main__':
    main()
