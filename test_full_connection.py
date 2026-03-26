#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试完整的连接流程
"""
import sys
sys.path.insert(0, '.')

from tplink_http_cleaner import TPLinkHTTPCleaner
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

# 测试账号
test_account = "test123"
test_password = "test123456"

print("=" * 60)
print("测试完整连接流程")
print("=" * 60)
print(f"账号: {test_account}")
print(f"密码: {'*' * len(test_password)}")
print()

cleaner = TPLinkHTTPCleaner('192.168.1.1', 'Cdu@123')

try:
    # 1. 登录
    print("\n1. 登录...")
    if not cleaner.login():
        print("登录失败")
        sys.exit(1)
    print("登录成功")

    # 2. 设置随机MAC
    print("\n2. 设置随机MAC...")
    if cleaner.set_mac_address():
        print("MAC设置成功")
    else:
        print("MAC设置失败")

    # 3. 设置PPPoE账号
    print("\n3. 设置PPPoE账号...")
    if cleaner.set_pppoe_account(test_account, test_password):
        print("PPPoE账号设置成功")
    else:
        print("PPPoE账号设置失败")
        sys.exit(1)

    # 4. 连接
    print("\n4. 连接PPPoE...")
    if cleaner.connect_pppoe():
        print("连接请求已发送")
    else:
        print("连接失败")
        sys.exit(1)

    # 5. 等待连接
    print("\n5. 等待连接建立（15秒）...")
    import time
    time.sleep(15)

    # 6. 检查状态
    print("\n6. 检查连接状态...")
    wan_status = cleaner.get_wan_status()
    print(f"WAN状态: {wan_status}")

    if wan_status:
        ip = wan_status.get("network", {}).get("wan_status", {}).get("ipaddr", "")
        print(f"IP地址: {ip}")

        if ip and ip != "0.0.0.0":
            print("\n" + "=" * 60)
            print("SUCCESS! 连接成功")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("WARNING: 未获取到有效IP")
            print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("WARNING: 无法获取连接状态")
        print("=" * 60)

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
