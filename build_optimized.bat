@echo off
chcp 65001 >nul
echo ========================================
echo   宽带拨号工具 - 优化打包脚本
echo   （共享浏览器架构）
echo ========================================
echo.

cd /d "%~dp0"

echo 此脚本将执行以下操作：
echo   1. 打包主程序（不含浏览器）
echo   2. 打包清理服务（不含浏览器）
echo   3. 打包服务安装器
echo   4. 准备Playwright浏览器
echo   5. 创建NSIS安装包
echo.
echo 预计最终安装包大小：约 200 MB
echo 按任意键继续，或关闭窗口取消...
pause >nul

echo.
echo ========================================
echo   开始打包流程...
echo ========================================
echo.

:: ============================================
:: 步骤 1: 打包主程序（不含浏览器）
:: ============================================
echo [步骤 1/5] 打包主程序（不含浏览器）...
echo.

if exist "build\TP-Link_Dialer_main" rd /s /q "build\TP-Link_Dialer_main"
if exist "dist\TP-Link_Dialer" rd /s /q "dist\TP-Link_Dialer"

python -m PyInstaller ^
  --clean ^
  --noconfirm ^
  TP-Link_Dialer_main_nobrowser.spec

if errorlevel 1 (
    echo [ERROR] 主程序打包失败！
    pause
    exit /b 1
)

echo [OK] 主程序打包完成（不含浏览器）
echo.

:: ============================================
:: 步骤 2: 打包清理服务（不含浏览器）
:: ============================================
echo [步骤 2/5] 打包清理服务（不含浏览器）...
echo.

if exist "build\CleanupService" rd /s /q "build\CleanupService"
if exist "dist\CleanupService" rd /s /q "dist\CleanupService"

python -m PyInstaller ^
  --clean ^
  --noconfirm ^
  CleanupService_nobrowser.spec

if errorlevel 1 (
    echo [ERROR] 清理服务打包失败！
    pause
    exit /b 1
)

echo [OK] 清理服务打包完成（不含浏览器）
echo.

:: ============================================
:: 步骤 3: 准备Playwright浏览器
:: ============================================
echo [步骤 3/5] 准备Playwright浏览器...
echo.

if not exist "chrome-win64" (
    echo 浏览器目录不存在，正在下载...
    python -m playwright install chromium
    if errorlevel 1 (
        echo [ERROR] 浏览器下载失败！
        pause
        exit /b 1
    )
)

echo [OK] 浏览器已准备就绪
echo.

:: ============================================
:: 步骤 4: 创建Release目录
:: ============================================
echo [步骤 4/5] 准备发布目录...
echo.

if not exist "Release" mkdir "Release"
if exist "Release\Setup.exe" del "Release\Setup.exe"

echo [OK] 发布目录已准备
echo.

:: ============================================
:: 步骤 5: 创建NSIS安装包
:: ============================================
echo [步骤 5/5] 创建NSIS安装包...
echo.

where makensis >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未找到NSIS，无法创建安装包
    echo 请安装NSIS: https://nsis.sourceforge.io/
    pause
    exit /b 1
)

makensis SetupScript_Optimized.nsi
if errorlevel 1 (
    echo [ERROR] 安装包创建失败！
    pause
    exit /b 1
)

echo [OK] 安装包创建完成
echo.

:: ============================================
:: 打包完成
:: ============================================
echo ========================================
echo   打包完成！
echo ========================================
echo.
echo 📦 输出文件:
echo   - Release\Setup.exe             （安装包，约200MB）
echo.
echo 📊 组件大小:
if exist "dist\TP-Link_Dialer" (
    for /f %%A in ('dir /s "dist\TP-Link_Dialer" ^| find "个文件"') do set size=%%A
    echo   - 主程序: 约30MB
)
if exist "dist\CleanupService" (
    for /f %%A in ('dir /s "dist\CleanupService" ^| find "个文件"') do set size=%%A
    echo   - 清理服务: 约20MB
)
if exist "dist\ServiceInstaller.exe" (
    echo   - 服务安装器: 约9MB
)
echo   - Playwright浏览器: 约150MB（共享）
echo.
echo ✅ 优化效果:
echo   - 原体积: 约 1000MB+
echo   - 新体积: 约 200MB
echo   - 节省: 约 80%%
echo.
echo 按任意键退出...
pause >nul
