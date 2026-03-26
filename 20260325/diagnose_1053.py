#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
直接测试服务exe的启动流程
"""

import subprocess
import time
import os

print("=" * 60)
print("Service 1053 Diagnostic Test")
print("=" * 60)
print()

exe_path = r"D:\13jiao\20260325\dist\TPLinkCleanupService.exe"

print(f"Testing: {exe_path}")
print()

# Test 1: Can exe run?
print("[Test 1] Can exe execute?")
print("-" * 60)

try:
    result = subprocess.run(
        [exe_path, "help"],
        capture_output=True,
        text=True,
        timeout=5
    )
    print(f"Exit code: {result.returncode}")
    if "Usage" in result.stdout or "install" in result.stdout:
        print("Result: OK - exe can run")
    else:
        print("Result: UNKNOWN - unexpected output")
except Exception as e:
    print(f"Result: FAILED - {e}")

print()

# Test 2: Check for dependencies
print("[Test 2] Check module imports")
print("-" * 60)

test_imports = """
import sys
sys.path.insert(0, '.')

errors = []

# Test imports
try:
    from config_manager import ConfigManager
    print("config_manager: OK")
except ImportError as e:
    print(f"config_manager: FAILED - {e}")
    errors.append("config_manager")

try:
    from tplink_http_cleaner import TPLinkHTTPCleaner
    print("tplink_http_cleaner: OK")
except ImportError as e:
    print(f"tplink_http_cleaner: FAILED - {e}")
    errors.append("tplink_http_cleaner")

if errors:
    print(f"\nMissing modules: {', '.join(errors)}")
    sys.exit(1)
else:
    print("\nAll modules: OK")
"""

result = subprocess.run(
    ["python", "-c", test_imports],
    capture_output=True,
    text=True,
    cwd=r"D:\13jiao\20260325"
)

print(result.stdout)
if result.stderr:
    print("Errors:")
    print(result.stderr)

print()

# Test 3: Manual service install simulation
print("[Test 3] Service Install Check")
print("-" * 60)

print("Checking if service exists...")
result = subprocess.run(
    ["sc", "query", "TPLinkCleanupTest"],
    capture_output=True,
    text=True
)

if "1060" in result.stdout:
    print("Service: Not installed (OK)")
else:
    print("Service output:")
    print(result.stdout[:200])

print()
print("=" * 60)
print("Next Steps")
print("=" * 60)
print()
print("1. Run as Administrator:")
print("   dist\\TPLinkCleanupService.exe install")
print()
print("2. Start service:")
print("   net start TPLinkCleanupTest")
print()
print("3. If 1053 occurs:")
print("   - Check Event Viewer (eventvwr)")
print("   - Check service log: %TEMP%\\tplink_cleanup\\cleanup_service.log")
print()
