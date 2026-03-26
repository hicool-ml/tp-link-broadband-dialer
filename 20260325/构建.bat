@echo off
chcp 65001 >nul
title 宽带拨号助手 - 构建脚本

echo ========================================
echo 宽带拨号助手 - 一键构建
echo ========================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [错误] 需要管理员权限！
    echo.
    echo 请右键点击本脚本，选择"以管理员身份运行"
    echo.
    pause
    exit /b 1
)

echo [√] 管理员权限检查通过
echo.

REM 检查PyInstaller
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [1/5] 安装 PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo [错误] PyInstaller 安装失败！
        pause
        exit /b 1
    )
) else (
    echo [1/5] PyInstaller 已安装 ✓
)

echo.
echo [2/5] 检查依赖包...
echo     - requests
python -c "import requests" 2>nul
if errorlevel 1 (
    echo     [安装] requests
    pip install requests
) else (
    echo     [OK] requests
)

echo     - pystray
python -c "import pystray" 2>nul
if errorlevel 1 (
    echo     [安装] pystray
    pip install pystray
) else (
    echo     [OK] pystray
)

echo     - pillow
python -c "import PIL" 2>nul
if errorlevel 1 (
    echo     [安装] pillow
    pip install pillow
) else (
    echo     [OK] pillow
)

echo     - pywin32
python -c "import win32service" 2>nul
if errorlevel 1 (
    echo     [安装] pywin32
    pip install pywin32
) else (
    echo     [OK] pywin32
)

echo.
echo [3/5] 开始构建主程序...
pyinstaller --clean --noconfirm build_main.spec
if errorlevel 1 (
    echo [错误] 主程序构建失败！
    pause
    exit /b 1
)

echo [OK] 主程序构建完成 ✓

echo.
echo [4/5] 开始构建服务程序...
pyinstaller --clean --noconfirm build_service.spec
if errorlevel 1 (
    echo [错误] 服务程序构建失败！
    pause
    exit /b 1
)

echo [OK] 服务程序构建完成 ✓

echo.
echo [5/5] 验证输出文件...
if not exist "dist\宽带拨号助手.exe" (
    echo [错误] 主程序exe未生成！
    pause
    exit /b 1
)
echo [OK] 宽带拨号助手.exe ✓

if not exist "dist\TPLinkCleanupService.exe" (
    echo [错误] 服务程序exe未生成！
    pause
    exit /b 1
)
echo [OK] TPLinkCleanupService.exe ✓

echo.
echo ========================================
echo 构建成功！
echo ========================================
echo.
echo 输出文件:
echo   📦 dist\宽带拨号助手.exe (主程序)
echo   📦 dist\TPLinkCleanupService.exe (服务程序)
echo.
echo 下一步:
echo   1. 测试主程序: dist\宽带拨号助手.exe
echo   2. 测试服务: dist\TPLinkCleanupService.exe install
echo   3. 构建安装程序: 右键点击 setup_http.nsi → 编译 NSIS脚本
echo.
echo ========================================
echo 构建完成时间: %date% %time%
echo ========================================
echo.

pause
