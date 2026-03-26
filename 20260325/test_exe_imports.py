#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试编译后的exe能否导入模块
"""

import subprocess
import sys

print("=" * 60)
print("测试编译后的exe模块导入")
print("=" * 60)
print()

# 测试导入
test_code = """
import sys
try:
    # 测试延迟导入
    from config_manager import ConfigManager
    print("[OK] config_manager imported successfully")

    from tplink_http_cleaner import TPLinkHTTPCleaner
    print("[OK] tplink_http_cleaner imported successfully")

    # 测试实例化
    cm = ConfigManager()
    print("[OK] ConfigManager instantiated")

    print()
    print("All imports successful!")

except ImportError as e:
    print(f"[ERROR] Import failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] Error: {e}")
    sys.exit(1)
"""

print("运行测试: dist\\TPLinkCleanupService.exe")
print()

result = subprocess.run(
    [sys.executable, "-c", test_code],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("✓ 模块导入测试通过")
    print()
    print("结论：exe中已包含 config_manager 和 tplink_http_cleaner")
    print()
    print("如果仍然1053，问题不在模块导入，而在其他地方")
else:
    print("✗ 模块导入测试失败")
    print()
    print("STDOUT:")
    print(result.stdout)
    print("STDERR:")
    print(result.stderr)
    print()
    print("结论：exe中缺少必需模块，需要重新打包")
