#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
获取详细 WAN 配置
"""
import sys
sys.path.insert(0, '.')

from tplink_http_cleaner import TPLinkHTTPCleaner
import json

cleaner = TPLinkHTTPCleaner('192.168.1.1', 'Cdu@123')

# 登录
print("登录路由器...")
if not cleaner.login():
    print("登录失败")
    sys.exit(1)

print("\n尝试获取 WAN 配置...")

# 尝试多种查询方式
queries = [
    # 获取 WAN 信息
    {"network": {"name": ["wan"]}, "method": "get"},
    {"network": {"get_wan_info": {}}, "method": "do"},
    {"network": {"wan": {}}, "method": "get"},

    # 获取所有配置
    {"network": {}, "method": "get"},
]

url = f"{cleaner.base_url}/stok={cleaner.stok}/ds"

for i, query in enumerate(queries, 1):
    print(f"\n>>> 查询 #{i}: {json.dumps(query, ensure_ascii=False)}")

    try:
        response = cleaner.session.post(url, json=query, timeout=10)
        result = response.json()

        print(f"    error_code: {result.get('error_code')}")

        if result.get("error_code") == 0:
            data = result.get("data", result)
            print(json.dumps(data, indent=4, ensure_ascii=False)[:500])
    except Exception as e:
        print(f"    错误: {e}")

print("\n完成")
