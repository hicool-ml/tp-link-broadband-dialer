@echo off
chcp 65001 >nul
echo ========================================
echo   项目文件清理脚本
echo ========================================
echo.
echo 此脚本将删除以下类型的文件：
echo   - 旧的编译文件 (build/, dist/, __pycache__)
echo   - 旧的测试文件
echo   - 旧的文档
echo   - 旧的脚本
echo   - 临时文件
echo.
echo ⚠️ 重要：此操作不会删除：
echo   - 浏览器文件 (chrome-win64/, ms-playwright/)
echo   - 主程序和脚本
echo   - 新的打包配置文件
echo   - 图标文件
echo.
echo 按任意键继续，或关闭窗口取消...
pause >nul

cd /d "%~dp0"

echo.
echo ========================================
echo   开始清理...
echo ========================================
echo.

:: ============================================
:: 清理编译和临时文件
:: ============================================
echo [1/5] 清理编译和临时文件...
if exist "build\" rd /s /q "build\"
if exist "dist\" rd /s /q "dist\"
if exist "__pycache__\" rd /s /q "__pycache__\"
if exist "*.pyc" del /f /q "*.pyc"
echo ✅ 完成
echo.

:: ============================================
:: 清理旧的可执行文件
:: ============================================
echo [2/5] 清理旧的可执行文件...
if exist "TP-Link_Dialer.exe" del /f /q "TP-Link_Dialer.exe"
if exist "Broadband_Dialer_Setup.exe" del /f /q "Broadband_Dialer_Setup.exe"
if exist "Broadband_Dialer_Setup_1.exe" del /f /q "Broadband_Dialer_Setup_1.exe"
if exist "chromedriver.exe" del /f /q "chromedriver.exe"
if exist "msedgedriver.exe" del /f /q "msedgedriver.exe"
echo ✅ 完成
echo.

:: ============================================
:: 清理旧的脚本文件
:: ============================================
echo [3/5] 清理旧的脚本文件...
if exist "555.py" del /f /q "555.py"
if exist "mytplink.py" del /f /q "mytplink.py"
if exist "tp_link_broadband_dialer_service.py" del /f /q "tp_link_broadband_dialer_service.py"
if exist "service_manager.py" del /f /q "service_manager.py"
if exist "test_service.py" del /f /q "test_service.py"
if exist "generate_icons.py" del /f /q "generate_icons.py"
if exist "build.bat" del /f /q "build.bat"
if exist "build_all.bat" del /f /q "build_all.bat"
if exist "build_all_onedir.bat" del /f /q "build_all_onedir.bat"
if exist "build_and_install_service.bat" del /f /q "build_and_install_service.bat"
if exist "build_exe.bat" del /f /q "build_exe.bat"
if exist "build_exe_onedir.bat" del /f /q "build_exe_onedir.bat"
if exist "build_installer.bat" del /f /q "build_installer.bat"
if exist "build_service.bat" del /f /q "build_service.bat"
if exist "install_service.bat" del /f /q "install_service.bat"
if exist "uninstall_service.bat" del /f /q "uninstall_service.bat"
if exist "prepare_browser.bat" del /f /q "prepare_browser.bat"
if exist "run_test.bat" del /f /q "run_test.bat"
if exist "make_installer.bat" del /f /q "make_installer.bat"
if exist "制作安装程序.bat" del /f /q "制作安装程序.bat"
if exist "最终打包脚本.bat" del /f /q "最终打包脚本.bat"
echo ✅ 完成
echo.

:: ============================================
:: 清理旧的配置文件
:: ============================================
echo [4/5] 清理旧的配置文件...
if exist "TP-Link_Dialer.spec" del /f /q "TP-Link_Dialer.spec"
if exist "installer.nsi" del /f /q "installer.nsi"
if exist "TP-Link_Dialer.nsi" del /f /q "TP-Link_Dialer.nsi"
if exist "制作安装程序.nsi" del /f /q "制作安装程序.nsi"
echo ✅ 完成
echo.

:: ============================================
:: 清理旧的文档和测试文件
:: ============================================
echo [5/5] 清理旧的文档和测试文件...
if exist "QUICKSTART_SERVICE.md" del /f /q "QUICKSTART_SERVICE.md"
if exist "SERVICE_README.md" del /f /q "SERVICE_README.md"
if exist "SERVICE_SUMMARY.md" del /f /q "SERVICE_SUMMARY.md"
if exist "关机拦截功能说明.md" del /f /q "关机拦截功能说明.md"
if exist "零依赖打包说明.md" del /f /q "零依赖打包说明.md"
if exist "13jiao.zip" del /f /q "13jiao.zip"
if exist "edge_profile\" rd /s /q "edge_profile\"
echo ✅ 完成
echo.

echo ========================================
echo   清理完成！
echo ========================================
echo.
echo 📁 保留的重要文件:
echo   ✅ 浏览器文件 (chrome-win64/, ms-playwright/)
echo   ✅ 主程序 (tp_link_broadband_dialer.py)
echo   ✅ 清理服务 (shutdown_cleanup_service.py)
echo   ✅ 服务安装器 (service_installer.py)
echo   ✅ 打包配置 (*.spec)
echo   ✅ 图标文件 (*.ico)
echo   ✅ 新的文档 (*.md)
echo.
echo 按任意键退出...
pause >nul
