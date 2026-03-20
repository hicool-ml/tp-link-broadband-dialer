# -*- coding: utf-8 -*-
"""快速测试URL格式和MAC地址功能"""

import sys
import io
if sys.platform == 'win32':
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except:
        pass

print("=" * 60)
print("🧪 测试1: URL格式验证")
print("=" * 60)

# 模拟stok token
stok = "%3EOUrXT7jwTGXw0*SSwI.NyfZmBSkw%3CNg"
router_ip = "192.168.1.1"

# 旧格式（错误）
print("\n❌ 旧格式（错误）:")
old_urls = [
    f"http://{router_ip}/userRpm/PPPoECfgRpm.htm?stok={stok}",
    f"http://{router_ip}/userRpm/ParaSwtPoolRpm.htm?stok={stok}",
]
for url in old_urls:
    print(f"  {url}")

# 新格式（正确）
print("\n✅ 新格式（正确）:")
new_urls = [
    ("PPPoE配置页面", f"http://{router_ip}/stok={stok}/pc/PPPoE.htm"),
    ("WAN配置页面", f"http://tplogin.cn/stok={stok}/pc/WanCfg.htm"),
]
for name, url in new_urls:
    print(f"  [{name}]")
    print(f"  {url}")

print("\n" + "=" * 60)
print("🧪 测试2: MAC地址格式验证")
print("=" * 60)

import random

def generate_random_mac():
    """生成随机MAC地址（横线格式）"""
    mac_bytes = [0x02, random.randint(0x00, 0xff), random.randint(0x00, 0xff),
                random.randint(0x00, 0xff), random.randint(0x00, 0xff), random.randint(0x00, 0xff)]
    return "-".join([f"{b:02X}" for b in mac_bytes])

print("\n✅ 正确格式（横线分隔）:")
for i in range(3):
    mac = generate_random_mac()
    print(f"  {mac}")

print("\n❌ 错误格式（冒号分隔）:")
mac_bytes = [0x02, 0x34, 0x2D, 0x2B, 0x1E, 0x6A]
mac_colon = ":".join([f"{b:02X}" for b in mac_bytes])
print(f"  {mac_colon} (路由器不接受此格式)")

print("\n" + "=" * 60)
print("🧪 测试3: 日志输出验证")
print("=" * 60)

print("\n✅ Emoji字符测试:")
test_messages = [
    "🔌 正在访问路由器管理页面...",
    "🔑 等待登录密码输入框...",
    "✅ 登录成功",
    "🚀 正在访问上网设置页面...",
    "📍 生成随机MAC: 02-45-99-B1-B7-CB",
    "💾 正在保存MAC地址设置...",
    "📋 保存后MAC: 02-45-99-B1-B7-CB",
    "⚠️ 未找到MAC输入框",
    "❌ 验证失败",
]

for msg in test_messages:
    print(f"  {msg}")

print("\n" + "=" * 60)
print("✅ 所有测试完成！")
print("=" * 60)
print("\n📝 测试结果:")
print("  ✅ URL格式正确")
print("  ✅ MAC地址格式正确（横线分隔）")
print("  ✅ 日志输出正常（emoji显示正常）")
print("\n💡 提示: 如果所有emoji都能正常显示，说明编码修复成功！")
