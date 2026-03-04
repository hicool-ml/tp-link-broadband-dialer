from playwright.sync_api import sync_playwright
import re
import time


def main():
    broadband_user = input("请输入宽带账号: ")
    broadband_pass = input("请输入宽带密码: ")

    router_password = "Cdu@123"  # 修改为你的管理员密码
    router_ip = "192.168.1.1"    # 如果是 192.168.0.1 请改这里

    # 用于存储捕获的 stok
    captured_stok = []

    def capture_stok(route, request):
        """捕获包含 stok 的请求"""
        url = request.url
        if "stok=" in url:
            match = re.search(r"stok=([^/&?#]+)", url)
            if match and not captured_stok:
                stok_value = match.group(1)
                captured_stok.append(stok_value)
                print(f"✅ 从网络请求中捕获到 stok: {stok_value}")
                print(f"   完整URL: {url}")
        route.continue_()

    with sync_playwright() as p:
        # 使用 headless=True 静默执行，不显示浏览器窗口
        browser = p.chromium.launch(headless=True, slow_mo=300)
        context = browser.new_context()
        page = context.new_page()

        # 设置路由来监听所有请求
        page.route("**/*", capture_stok)

        print("正在打开路由器登录页面...")
        page.goto(f"http://{router_ip}/")

        # ===== 登录 =====
        page.wait_for_selector("input[type='password']", timeout=10000)
        page.fill("input[type='password']", router_password)
        page.keyboard.press("Enter")

        print("正在等待登录完成...")
        
        # 等待捕获到 stok
        print("等待捕获 stok...")
        for i in range(15):
            time.sleep(1)
            if captured_stok:
                break
            print(f"[{i+1}/15] 等待中... 已捕获: {len(captured_stok)} 个 stok")
        
        # 停止监听
        page.unroute("**/*", capture_stok)
        
        if not captured_stok:
            print("❌ 未获取到 stok，登录可能失败")
            print("提示：请检查管理员密码是否正确")
            input("按回车键关闭浏览器...")
            browser.close()
            return

        stok = captured_stok[0]
        print("✅ 使用 stok:", stok)

        # 等待登录后的页面完全加载
        time.sleep(3)
        
        # ===== 按照正确的流程操作 =====
        print("步骤1: 点击'路由设置'...")
        try:
            router_set_btn = page.wait_for_selector("#routerSetMbtn", timeout=5000)
            if router_set_btn:
                print("✅ 找到'路由设置'按钮，点击...")
                router_set_btn.click()
                time.sleep(2)
        except:
            print("⚠️ 未找到'路由设置'按钮，可能已经在该页面")
        
        print("步骤2: 点击左侧'上网设置'菜单...")
        
        # 使用正确的选择器
        internet_menu_selectors = [
            "#network_rsMenu",  # 通过 ID
            "li#network_rsMenu",  # 通过标签和 ID
            "li.menuLi",  # 通过标签和 class
            "li:has-text('上网设置')",  # 通过文本
        ]
        
        menu_clicked = False
        for selector in internet_menu_selectors:
            try:
                print(f"尝试查找: {selector}")
                menu_item = page.wait_for_selector(selector, timeout=2000)
                if menu_item:
                    print(f"✅ 找到'上网设置'菜单，点击...")
                    menu_item.click()
                    menu_clicked = True
                    time.sleep(2)
                    break
            except:
                continue
        
        if not menu_clicked:
            print("⚠️ 未找到'上网设置'菜单，请手动点击...")
            input("按回车键继续...")
        
        print("步骤3: 检查并选择'宽带拨号上网'方式...")
        try:
            # 先检查当前选中的值
            wan_sel = page.wait_for_selector("#wanSel .value", timeout=5000)
            if wan_sel:
                current_value = wan_sel.inner_text()
                print(f"当前上网方式: {current_value}")
                
                if "宽带拨号上网" in current_value or "PPPoE" in current_value:
                    print("✅ 已经是'宽带拨号上网'方式，无需切换")
                else:
                    print("需要切换到'宽带拨号上网'方式...")
                    # 点击下拉框打开选项列表
                    wan_sel_box = page.wait_for_selector("#wanSel", timeout=5000)
                    wan_sel_box.click()
                    time.sleep(1)
                    
                    # 点击"宽带拨号上网"选项
                    # 根据HTML，选项在 #selOptsUlwanSel 中
                    pppoe_option_selectors = [
                        "#selOptsUlwanSel li:has-text('宽带拨号上网')",
                        "#selOptsUlwanSel li[title='宽带拨号上网']",
                        "li.option:has-text('宽带拨号上网')",
                    ]
                    
                    option_clicked = False
                    for selector in pppoe_option_selectors:
                        try:
                            pppoe_option = page.wait_for_selector(selector, timeout=1000)
                            if pppoe_option:
                                print(f"✅ 找到'宽带拨号上网'选项，点击...")
                                pppoe_option.click()
                                option_clicked = True
                                time.sleep(1)
                                break
                        except:
                            continue
                    
                    if not option_clicked:
                        print("⚠️ 未找到'宽带拨号上网'选项")
        except Exception as e:
            print(f"⚠️ 检查上网方式时出错: {e}")
            print("继续尝试填写账号密码...")

        # ===== 填写账号密码 =====
        print("填写宽带账号密码...")

        # 等待输入框出现
        try:
            page.wait_for_selector("#name", timeout=10000)
            page.wait_for_selector("#psw", timeout=5000)
        except:
            print("❌ 未找到账号或密码输入框")
            input("按回车键关闭浏览器...")
            browser.close()
            return

        # 清空并填写账号
        page.fill("#name", "")
        page.fill("#name", broadband_user)
        print(f"账号已填写: {broadband_user}")

        # 清空并填写密码
        page.fill("#psw", "")
        page.fill("#psw", broadband_pass)
        print("密码已填写")

        # 触发 blur 事件（重要）
        page.locator("#psw").blur()

        time.sleep(1)

        # ===== 点击连接 =====
        print("点击连接按钮...")
        try:
            page.click("#save")
        except:
            print("尝试点击其他可能的保存按钮...")
            page.click("button:has-text('保存'), button:has-text('连接'), .save-btn")
            page.click("#save")

        print("等待拨号中...")
        time.sleep(10)

        # ===== 检查连接状态 =====
        print("检查连接状态...")
        try:
            # 等待IP地址更新
            time.sleep(3)
            
            # 获取IP地址
            ip_element = page.wait_for_selector("#wanIpLbl", timeout=5000)
            if ip_element:
                ip_address = ip_element.inner_text()
                print(f"当前WAN IP地址: {ip_address}")
                
                if ip_address and ip_address != "0.0.0.0" and ip_address != "0.0.0.0 ":
                    print("✅ 连接成功！已获取到有效的IP地址")
                    print(f"✅ 拨号成功，IP地址: {ip_address}")
                    
                    # 等待2秒后自动关闭浏览器
                    print("2秒后自动关闭浏览器...")
                    time.sleep(2)
                    browser.close()
                    return
                else:
                    print("⚠️ IP地址为 0.0.0.0，连接可能失败")
                    print("请检查账号密码是否正确")
            else:
                print("⚠️ 未找到IP地址显示元素")
        except Exception as e:
            print(f"⚠️ 检查IP地址时出错: {e}")

        print("✅ 脚本执行完成，请观察是否成功拨号。")

        # 不立即关闭浏览器，方便观察
        input("按回车键关闭浏览器...")
        browser.close()


if __name__ == "__main__":
    main()

