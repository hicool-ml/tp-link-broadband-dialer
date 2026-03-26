#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建Windows任务计划 - 用于关机清理
"""

import subprocess
import sys
from pathlib import Path

TASK_NAME = "TPLinkCleanup"
CURRENT_DIR = Path(__file__).parent
EXE_PATH = CURRENT_DIR / "dist" / "cleanup_http.exe"
PS_PATH = CURRENT_DIR / "cleanup.ps1"


def run_command(cmd):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding='gbk',  # Windows使用GBK编码
            errors='ignore',
            timeout=30
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)


def main():
    print("=" * 50)
    print("创建TP-Link路由器关机清理任务")
    print("=" * 50)
    print()

    # 检查文件
    if not EXE_PATH.exists():
        print(f"[错误] 找不到文件: {EXE_PATH}")
        return 1

    print(f"[1/4] 清理程序: {EXE_PATH}")
    print(f"[2/4] PowerShell脚本: {PS_PATH}")
    print()

    # 删除旧任务
    print("[3/4] 删除旧任务...")
    code, out, err = run_command(f'schtasks /Delete /TN "{TASK_NAME}" /F')
    if code == 0:
        print("     旧任务已删除")
    else:
        print("     无旧任务")
    print()

    # 创建新任务
    print("[4/4] 创建关机触发任务...")
    cmd = (
        f'schtasks /Create '
        f'/TN "{TASK_NAME}" '
        f'/TR "powershell.exe -ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File \\"{PS_PATH}\\"" '
        f'/SC ONEVENT '
        f'/EC System '
        f'/MO "*[System[(EventID=1074 or EventID=6006)]]" '
        f'/RU SYSTEM '
        f'/RL HIGHEST '
        f'/F'
    )

    code, out, err = run_command(cmd)

    if code == 0:
        print("     [OK] 任务创建成功!")
        print()
        print("任务详情:")
        print("-" * 50)
        code, out, err = run_command(f'schtasks /Query /TN "{TASK_NAME}" /FO LIST')
        print(out)
        print("-" * 50)
        print()
        print("管理命令:")
        print(f"  运行任务: schtasks /Run /TN {TASK_NAME}")
        print(f"  删除任务: schtasks /Delete /TN {TASK_NAME} /F")
        print(f"  查看日志: C:\\ProgramData\\BroadbandDialer\\cleanup.log")
        print()
        print("立即测试运行...")
        code, out, err = run_command(f'schtasks /Run /TN "{TASK_NAME}"')
        if code == 0:
            print("[OK] 任务已触发，请检查日志")
        else:
            print(f"[WARNING] 触发失败: {err}")

        return 0
    else:
        print(f"[ERROR] 任务创建失败!")
        print(f"错误: {err}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
