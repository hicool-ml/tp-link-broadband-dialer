#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 1053 关键指标
"""

import sys
import os
import time

print("=" * 60)
print("1053 Error Test - Service Startup Performance")
print("=" * 60)
print()

# Test 1: Module import speed
print("[Test 1] Module Import Speed")
print("-" * 60)

start = time.time()

try:
    from config_manager import ConfigManager
    elapsed1 = (time.time() - start) * 1000
    print(f"config_manager: {elapsed1:.2f}ms")

    start = time.time()
    from tplink_http_cleaner import TPLinkHTTPCleaner
    elapsed2 = (time.time() - start) * 1000
    print(f"tplink_http_cleaner: {elapsed2:.2f}ms")

    total = elapsed1 + elapsed2
    print(f"Total: {total:.2f}ms")

    if total > 1000:
        print("Result: SLOW - May cause 1053 if imported at startup!")
    else:
        print("Result: OK - Lazy import strategy is good")

except ImportError as e:
    print(f"ERROR: {e}")

print()
print("[Test 2] Logging Setup Speed")
print("-" * 60)

start = time.time()
try:
    import logging
    from pathlib import Path

    log_dir = Path(os.environ.get('TEMP', 'C:\\Windows\\Temp')) / 'tplink_cleanup'
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'test.log'

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.FileHandler(log_file, encoding='utf-8')],
        force=True
    )

    logger = logging.getLogger(__name__)
    elapsed = (time.time() - start) * 1000

    print(f"Logging setup: {elapsed:.2f}ms")

    if elapsed > 500:
        print("Result: SLOW - Consider optimizing")
    else:
        print("Result: OK")

except Exception as e:
    print(f"ERROR: {e}")

print()
print("[Test 3] Critical Path Analysis")
print("-" * 60)

print("Service startup should follow this sequence:")
print()
print("1. __init__():")
print("   - CreateEvent (fast)")
print("   - ReportServiceStatus(START_PENDING) (fast)")
print()
print("2. SvcDoRun():")
print("   - ReportServiceStatus(RUNNING) (fast) <- CRITICAL")
print("   - setup_logging() (can be slow)")
print("   - validate_config() (can be slow)")
print()
print("Key point: RUNNING must be reported BEFORE any slow operations!")
print()

print("=" * 60)
print("Conclusion")
print("=" * 60)
print()
print("If module imports are fast (<1000ms total), and")
print("RUNNING is reported first, 1053 should NOT occur.")
print()
print("Next step: Install and start the actual service:")
print("  1. Run as Administrator")
print("  2. dist\\TPLinkCleanupService.exe install")
print("  3. net start TPLinkShutdownCleanup")
print("  4. sc query TPLinkShutdownCleanup")
print()
print("Expected output: STATE: 4  RUNNING")
print()
