@echo off
chcp 65001 >nul
echo ========================================
echo   宽带拨号工具 - 最新版本打包
echo ========================================
echo.

cd /d "%~dp0"

echo 此脚本将执行以下操作：
echo   1. 打包主程序 (TP-Link_Dialer.exe)
echo   2. 打包清理服务 (CleanupService.exe)
echo   3. 打包服务安装器 (ServiceInstaller.exe)
echo   4. 创建NSIS安装包
echo.
echo 按任意键继续，或关闭窗口取消...
pause >nul

echo.
echo ========================================
echo   开始打包流程...
echo ========================================
echo.

:: ============================================
:: 步骤 1: 打包主程序
:: ============================================
echo [步骤 1/4] 打包主程序...
echo.

if exist "build\TP-Link_Dialer" rd /s /q "build\TP-Link_Dialer"
if exist "dist\TP-Link_Dialer" rd /s /q "dist\TP-Link_Dialer"

python -m PyInstaller ^
  --clean ^
  --noconfirm ^
  TP-Link_Dialer_main.spec

if errorlevel 1 (
    echo ❌ 主程序打包失败！
    pause
    exit /b 1
)

echo ✅ 主程序打包完成
echo.

:: ============================================
:: 步骤 2: 打包清理服务
:: ============================================
echo [步骤 2/4] 打包清理服务...
echo.

if exist "build\CleanupService" rd /s /q "build\CleanupService"
if exist "dist\CleanupService" rd /s /q "dist\CleanupService"

python -m PyInstaller ^
  --clean ^
  --noconfirm ^
  CleanupService.spec

if errorlevel 1 (
    echo ❌ 清理服务打包失败！
    pause
    exit /b 1
)

echo ✅ 清理服务打包完成
echo.

:: ============================================
:: 步骤 3: 打包服务安装器
:: ============================================
echo [步骤 3/4] 打包服务安装器...
echo.

if exist "build\ServiceInstaller" rd /s /q "build\ServiceInstaller"
if exist "dist\ServiceInstaller" rd /s /q "dist\ServiceInstaller"

python -m PyInstaller ^
  --clean ^
  --noconfirm ^
  ServiceInstaller.spec

if errorlevel 1 (
    echo ❌ 服务安装器打包失败！
    pause
    exit /b 1
)

echo ✅ 服务安装器打包完成
echo.

:: ============================================
:: 步骤 4: 创建NSIS安装包
:: ============================================
echo [步骤 4/4] 创建NSIS安装包...
echo.

:: 检查NSIS是否安装
where makensis >nul 2>&1
if errorlevel 1 (
    echo ⚠️ 未找到NSIS，跳过安装包创建
    echo 请安装NSIS: https://nsis.sourceforge.io/
) else (
    makensis Setup_Stable.nsi
    if errorlevel 1 (
        echo ❌ 安装包创建失败！
    ) else (
        echo ✅ 安装包创建完成
    )
)

echo.
echo ========================================
echo   打包完成！
echo ========================================
echo.
echo 📦 输出文件:
echo   - dist\TP-Link_Dialer\          (主程序)
echo   - dist\CleanupService\          (清理服务)
echo   - dist\ServiceInstaller\        (服务安装器)
echo   - Release\Setup.exe             (安装包)
echo.
echo 按任意键退出...
pause >nul
