# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == 'win32':
    import ctypes
    ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import re

with open('tp_link_broadband_dialer.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 统计
total_lines = len(lines)
code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
comment_lines = [l for l in lines if l.strip().startswith('#')]
blank_lines = [l for l in lines if not l.strip()]

print(f"代码统计:")
print(f"  总行数: {total_lines}")
print(f"  代码行: {len(code_lines)}")
print(f"  注释行: {len(comment_lines)}")
print(f"  空行: {len(blank_lines)}")

# 检查重复的MAC模式代码
print(f"\n发现的代码质量问题:")
print(f"\n1. 严重重复代码 - MAC设置模式:")
mac_code_sections = 0
for i, line in enumerate(lines):
    if 'page.query_selector("#wanMacSel")' in line:
        mac_code_sections += 1

print(f"   MAC设置代码重复: {mac_code_sections}次")
print(f"   问题: router/pc/random三种模式的代码90%相同，只是选择器不同")
print(f"   建议: 提取为独立方法 set_mac_mode(page, mode, value)")

# 检查run_connection方法长度
print(f"\n2. 超长方法:")
run_connection_start = None
for i, line in enumerate(lines):
    if 'def run_connection(' in line:
        run_connection_start = i
    if run_connection_start and i > run_connection_start and line.startswith('def ') and i < run_connection_start + 700:
        run_connection_length = i - run_connection_start
        print(f"   run_connection方法: ~{run_connection_length}行")
        print(f"   问题: 单个方法过长，难以维护")
        print(f"   建议: 拆分为 login(), fill_account(), set_mac_mode(), connect()等")
        break

# 检查类职责
print(f"\n3. 单一类职责过重:")
print(f"   RouterLoginGUI类包含: GUI + 业务逻辑 + 浏览器自动化 + 托盘图标")
print(f"   问题: 违反单一职责原则")
print(f"   建议: 拆分为:")
print(f"     - RouterBrowser: 负责浏览器自动化")
print(f"     - MACManager: 负责MAC地址设置")
print(f"     - DialerGUI: 只负责GUI界面")

# 检查重复的validate_and_save
print(f"\n4. 重复定义:")
validate_count = len([l for l in lines if 'def validate_and_save' in l])
if validate_count > 1:
    print(f"   validate_and_save方法定义了{validate_count}次")
    print(f"   问题: 重复定义会导致后面的覆盖前面的")

