#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试MAC地址设置功能"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright
import time
import random
from pathlib import Path

# 获取浏览器路径
def get_browser_path():
    # 查找本地浏览器
    possible_paths = [
        Path(__file__).parent / "chrome-win64" / "chrome.exe",
        Path(__file__).parent / "dist" / "TP-Link_Dialer" / "chrome-win64" / "chrome.exe",
    ]
    for path in possible_paths:
        if path.exists():
            return str(path)
    return None

def generate_random_mac():
    """生成随机MAC地址"""
    mac_bytes = [0x02, random.randint(0x00, 0xff), random.randint(0x00, 0xff),
                random.randint(0x00, 0xff), random.randint(0x00, 0xff), random.randint(0x00, 0xff)]
    return ":".join([f"{b:02X}" for b in mac_bytes])

def test_mac_setting():
    """测试MAC地址设置"""
    router_ip = "192.168.1.1"
    router_password = "Cdu@123"

    browser_path = get_browser_path()
    if not browser_path:
        print("❌ 未找到浏览器")
        return

    print(f"🌐 使用浏览器: {browser_path}")

    with sync_playwright() as p:
        print("🚀 启动浏览器...")
        launch_options = {
            'headless': False,  # 显示浏览器，方便观察
            'slow_mo': 500,
            'args': [
                "--no-sandbox",
                "--disable-gpu",
                "--disable-web-security",
            ],
        }

        browser = p.chromium.launch(**launch_options)
        context = browser.new_context()
        page = context.new_page()

        # 访问路由器
        print(f"🔌 访问路由器 {router_ip}...")
        page.goto(f"http://{router_ip}/")

        # 登录
        print("🔑 登录中...")
        page.wait_for_selector("input[type='password']", timeout=10000)
        page.fill("input[type='password']", router_password)
        page.keyboard.press("Enter")

        # 等待登录并捕获stok
        captured_stok = []
        def capture_stok(route, request):
            url = request.url
            if "stok=" in url:
                import re
                match = re.search(r'stok=([^&]+)', url)
                if match:
                    stok = match.group(1)
                    if stok not in captured_stok:
                        captured_stok.append(stok)
                        print(f"✅ 捕获到 stok: {stok}")
            route.continue_()

        page.route("**/*", capture_stok)

        # 等待捕获stok
        for i in range(15):
            time.sleep(1)
            if captured_stok:
                break

        page.unroute("**/*", capture_stok)

        if not captured_stok:
            print("❌ 登录失败")
            browser.close()
            return

        stok = captured_stok[0]
        print("✅ 登录成功")

        # 访问PPPoE页面
        print("🚀 访问PPPoE配置页面...")
        wanc_url = f"http://{router_ip}/userRpm/PPPoECfgRpm.htm?stok={stok}"
        page.goto(wanc_url, timeout=10000)
        time.sleep(3)

        # 检查页面元素
        print("\n🔍 检查页面元素...")

        # 检查MAC选择框
        try:
            mac_sel = page.wait_for_selector("#wanMacSel", timeout=3000)
            if mac_sel:
                print("✅ 找到 MAC选择框 #wanMacSel")
                # 获取当前值
                current_value = mac_sel.query_selector(".value")
                if current_value:
                    print(f"   当前值: {current_value.inner_text()}")
        except:
            print("⚠️ 未找到 #wanMacSel")

        # 检查MAC输入框
        try:
            mac_input = page.wait_for_selector("#wanMac", timeout=3000)
            if mac_input:
                print("✅ 找到 MAC输入框 #wanMac")
                print(f"   当前值: {mac_input.input_value()}")
                print(f"   可见: {mac_input.is_visible()}")
                print(f"   启用: {mac_input.is_enabled()}")
        except:
            print("⚠️ 未找到 #wanMac")

        # 检查高级设置保存按钮
        try:
            save_btn = page.wait_for_selector("#saveHighSet", timeout=3000)
            if save_btn:
                print("✅ 找到高级设置保存按钮 #saveHighSet")
                print(f"   可见: {save_btn.is_visible()}")
                print(f"   启用: {save_btn.is_enabled()}")
        except:
            print("⚠️ 未找到 #saveHighSet")

        print("\n" + "="*60)
        print("请观察浏览器页面，确认MAC地址相关元素的位置")
        print("按回车继续测试MAC地址填写...")
        print("="*60)
        input()

        # 生成随机MAC
        random_mac = generate_random_mac()
        print(f"\n📍 生成随机MAC: {random_mac}")

        # 尝试填写MAC地址
        print("📝 尝试填写MAC地址...")

        # 方法1: 直接填写
        try:
            page.fill("#wanMac", "")
            page.fill("#wanMac", random_mac)
            print("✅ 方法1: 直接填写成功")
            time.sleep(1)

            # 验证
            current_value = page.input_value("#wanMac")
            print(f"   验证值: {current_value}")
            if current_value.upper() == random_mac:
                print("✅ MAC地址填写验证成功！")
            else:
                print(f"❌ MAC地址填写验证失败: 期望 {random_mac}, 实际 {current_value}")
        except Exception as e:
            print(f"❌ 方法1失败: {e}")

            # 方法2: 先点击选择框
            try:
                print("\n🔄 尝试方法2: 先点击MAC选择框...")
                page.click("#wanMacSel")
                time.sleep(1)
                page.fill("#wanMac", "")
                page.fill("#wanMac", random_mac)
                print("✅ 方法2: 点击选择框后填写成功")
            except Exception as e2:
                print(f"❌ 方法2也失败: {e2}")

        print("\n💾 准备点击保存按钮...")
        print("按回车继续...")
        input()

        try:
            page.click("#saveHighSet")
            print("✅ 已点击高级设置保存按钮")
            time.sleep(3)
            print("✅ 保存完成")
        except Exception as e:
            print(f"❌ 保存失败: {e}")

        print("\n" + "="*60)
        print("测试完成！请检查路由器页面MAC地址是否已更新")
        print("按回车关闭浏览器...")
        print("="*60)
        input()

        browser.close()
        print("✅ 测试结束")

if __name__ == "__main__":
    test_mac_setting()
