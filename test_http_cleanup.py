#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 HTTP 清理流程
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from tplink_http_cleaner import TPLinkHTTPCleaner
import logging

# 设置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 创建清理器
cleaner = TPLinkHTTPCleaner('192.168.1.1', 'Cdu@123')

# 执行清理
print("=" * 60)
print("开始测试路由器清理流程")
print("=" * 60)

result = cleaner.run_cleanup()

print("=" * 60)
if result:
    print("测试完成：成功")
else:
    print("测试完成：失败")
print("=" * 60)
