#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
获取 WAN 配置
"""
import sys
sys.path.insert(0, '.')

from tplink_http_cleaner import TPLinkHTTPCleaner
import logging
import json

logging.basicConfig(level=logging.DEBUG, format='%(message)s')

cleaner = TPLinkHTTPCleaner('192.168.1.1', 'Cdu@123')

# 登录
print("=" * 60)
print("登录路由器...")
print("=" * 60)
if not cleaner.login():
    print("登录失败")
    sys.exit(1)

print("\n" + "=" * 60)
print("尝试获取 WAN 配置...")
print("=" * 60)

# 尝试多种获取配置的方式
queries = [
    {
        "network": {
            "get_wan_status": {}
        },
        "method": "get"
    },
    {
        "network": {},
        "method": "get"
    },
    {
        "system": {
            "get_sys_info": {}
        },
        "method": "do"
    },
]

url = f"{cleaner.base_url}/stok={cleaner.stok}/ds"

for i, query in enumerate(queries, 1):
    print(f"\n>>> 尝试查询 #{i}:")
    print(f"    {json.dumps(query, ensure_ascii=False)}")

    try:
        response = cleaner.session.post(url, json=query, timeout=10)
        print(f"    响应: {response.text}")

        if response.status_code == 200:
            try:
                result = response.json()
                if result.get("error_code") == 0:
                    print("    >>> 成功！")
                    # 美化输出
                    print(json.dumps(result, indent=2, ensure_ascii=False))
            except:
                pass
    except Exception as e:
        print(f"    错误: {e}")

print("\n" + "=" * 60)
print("完成")
print("=" * 60)
