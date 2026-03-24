#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试服务清理逻辑（不作为服务运行）
"""

import sys
import time
import json
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from tplink_http_cleaner import TPLinkHTTPCleaner

def log(msg):
    """记录日志"""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f"{timestamp} {msg}")
    # 同时写入日志文件
    log_file = Path(os.environ.get("TEMP", "C:\\Temp")) / "tplink_cleanup_test.log"
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{timestamp} {msg}\n")
    except:
        pass

def main():
    log("=" * 60)
    log("开始测试服务清理逻辑")
    log("=" * 60)

    # 读取配置
    config_file = Path(os.environ.get("USERPROFILE", ".")) / ".tplink_dialer" / "config.json"

    if not config_file.exists():
        log(f"[ERROR] 配置文件不存在: {config_file}")
        return False

    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    router_ip = config.get("router_ip", "192.168.1.1")
    router_password = config.get("router_password", "")

    if not router_password:
        log("[ERROR] 路由器密码未配置")
        return False

    log(f"路由器IP: {router_ip}")
    log(f"路由器密码: {'***' if router_password else '(未设置)'}")

    # 执行清理
    cleaner = TPLinkHTTPCleaner(router_ip, router_password)
    result = cleaner.run_cleanup()

    log("=" * 60)
    if result:
        log("[SUCCESS] 清理测试完成：成功")
    else:
        log("[ERROR] 清理测试完成：失败")
    log("=" * 60)

    return result

if __name__ == '__main__':
    try:
        result = main()
        sys.exit(0 if result else 1)
    except Exception as e:
        log(f"[ERROR] 测试异常: {e}")
        import traceback
        log(traceback.format_exc())
        sys.exit(1)
