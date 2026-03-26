#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试服务启动"""

import sys
import os
import logging
sys.path.insert(0, os.path.dirname(__file__))

try:
    print("初始化日志...")
    logging.basicConfig(level=logging.INFO)

    print("创建清理器...")
    from shutdown_cleanup_service import RouterAccountCleaner
    cleaner = RouterAccountCleaner()
    print("清理器创建成功")

except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
