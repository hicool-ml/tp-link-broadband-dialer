#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TP-Link 路由器关机守护进程
监听 Windows 关机信号，在网络被卸载前清理路由器账号

这是解决 Windows 关机时序问题的唯一正确方案：
- 拦截 WM_QUERYENDSESSION 消息
- 在网络栈卸载前执行清理
- 允许 Windows 正常关机
"""

import sys
import os
import time
import subprocess
import threading
import logging
from pathlib import Path

# Windows API 依赖
try:
    import win32gui
    import win32con
    import win32api
except ImportError:
    print("错误: 需要安装 pywin32")
    print("请运行: pip install pywin32")
    sys.exit(1)

# =============================================================================
# 配置
# =============================================================================

CLEANUP_EXE_NAME = "cleanup_http.exe"
LOG_DIR = Path("C:/ProgramData/BroadbandDialer")
LOG_FILE = LOG_DIR / "cleanup_guard.log"

# =============================================================================
# 日志设置
# =============================================================================

LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# =============================================================================
# 核心功能
# =============================================================================

def get_cleanup_exe_path():
    """获取清理程序的路径"""
    if getattr(sys, 'frozen', False):
        # 打包后的 exe
        base_dir = Path(sys.executable).parent
    else:
        # 开发环境
        base_dir = Path(__file__).parent

    cleanup_exe = base_dir / CLEANUP_EXE_NAME

    if not cleanup_exe.exists():
        logger.error(f"清理程序不存在: {cleanup_exe}")
        return None

    return str(cleanup_exe)


def run_cleanup():
    """执行清理程序"""
    try:
        cleanup_exe = get_cleanup_exe_path()
        if not cleanup_exe:
            return False

        logger.info("=" * 60)
        logger.info("收到关机信号，开始执行路由器清理...")
        logger.info(f"清理程序: {cleanup_exe}")
        logger.info("=" * 60)

        # 在新线程中执行清理，避免阻塞消息循环
        def cleanup_thread():
            try:
                result = subprocess.run(
                    [cleanup_exe],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    encoding='utf-8',
                    errors='replace'
                )

                logger.info("清理程序输出:")
                if result.stdout:
                    for line in result.stdout.split('\n'):
                        if line.strip():
                            logger.info(f"  {line}")

                if result.stderr:
                    logger.warning(f"清理程序错误: {result.stderr}")

                if result.returncode == 0:
                    logger.info("✅ 路由器清理完成")
                else:
                    logger.warning(f"⚠️  清理程序返回码: {result.returncode}")

            except subprocess.TimeoutExpired:
                logger.error("❌ 清理程序超时（30秒）")
            except Exception as e:
                logger.error(f"❌ 清理程序异常: {e}")

        thread = threading.Thread(target=cleanup_thread, daemon=True)
        thread.start()

        # 等待清理完成（最多20秒）
        thread.join(timeout=20)

        if thread.is_alive():
            logger.warning("⚠️  清理仍在进行中，关机继续...")
        else:
            logger.info("✅ 清理已完成，允许关机")

        return True

    except Exception as e:
        logger.error(f"执行清理失败: {e}")
        return False


# =============================================================================
# Windows 消息处理
# =============================================================================

class WindowMessageHandler:
    """Windows 消息处理器"""

    def __init__(self):
        self.hwnd = None
        self.cleanup_started = False

    def wnd_proc(self, hwnd, msg, wparam, lparam):
        """窗口过程函数"""
        try:
            # 关机查询消息（关机/重启/注销）
            if msg == win32con.WM_QUERYENDSESSION:
                logger.info("")
                logger.info("=" * 60)
                logger.info("收到 WM_QUERYENDSESSION 消息")
                logger.info("系统即将关机/重启/注销")
                logger.info("=" * 60)

                if not self.cleanup_started:
                    self.cleanup_started = True
                    run_cleanup()

                logger.info("✅ 返回 TRUE，允许关机")
                logger.info("")
                return 1  # TRUE - 允许关机

            # 关机开始消息
            elif msg == win32con.WM_ENDSESSION:
                logger.info("收到 WM_ENDSESSION 消息，关机流程开始")
                return 0

            # 其他消息
            else:
                return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

        except Exception as e:
            logger.error(f"消息处理异常: {e}")
            return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)


def create_hidden_window(handler):
    """创建隐藏窗口用于接收系统消息"""
    try:
        # 注册窗口类
        wc = win32gui.WNDCLASS()
        wc.hInstance = win32api.GetModuleHandle(None)
        wc.lpszClassName = "TPLinkCleanupGuard"
        wc.lpfnWndProc = handler.wnd_proc
        wc.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW
        wc.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        wc.hbrBackground = win32con.COLOR_WINDOW + 1

        class_atom = win32gui.RegisterClass(wc)

        # 创建隐藏窗口
        handler.hwnd = win32gui.CreateWindow(
            class_atom,
            "TP-Link Cleanup Guard",
            0,  # style
            0, 0, 0, 0,  # x, y, width, height
            0, 0,  # parent, menu
            0,  # instance
            None  # param
        )

        logger.info(f"✅ 隐藏窗口创建成功: HWND={handler.hwnd}")
        return handler.hwnd

    except Exception as e:
        logger.error(f"创建隐藏窗口失败: {e}")
        raise


# =============================================================================
# 主程序
# =============================================================================

def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("TP-Link 路由器关机守护进程启动")
    logger.info("=" * 60)
    logger.info(f"Python 版本: {sys.version}")
    logger.info(f"工作目录: {os.getcwd()}")
    logger.info(f"清理程序: {get_cleanup_exe_path()}")
    logger.info("=" * 60)
    logger.info("")
    logger.info("✅ 守护进程已启动，正在监听关机信号...")
    logger.info("✅ 此程序将常驻后台，拦截关机/重启/注销事件")
    logger.info("✅ 收到关机信号时将自动清理路由器账号")
    logger.info("")
    logger.info("提示: 此程序无窗口，将在系统托盘中静默运行")
    logger.info("如需停止，请通过任务管理器结束 cleanup_guard.exe")
    logger.info("")

    try:
        # 创建消息处理器
        handler = WindowMessageHandler()

        # 创建隐藏窗口
        hwnd = create_hidden_window(handler)

        logger.info("✅ 守护进程运行中，等待关机信号...")
        logger.info("")

        # 消息循环
        while True:
            try:
                win32gui.PumpWaitingMessages()
                time.sleep(0.2)  # 200ms
            except Exception as e:
                logger.error(f"消息循环异常: {e}")
                time.sleep(1)

    except KeyboardInterrupt:
        logger.info("收到中断信号，程序退出")
    except Exception as e:
        logger.error(f"程序异常: {e}")
        raise


if __name__ == "__main__":
    main()
