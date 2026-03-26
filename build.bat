@echo off
chcp 65001 >nul
echo ========================================
echo 宽带拨号助手 - 构建脚本
echo ========================================
echo.

REM 检查PyInstaller是否安装
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [1/3] 安装 PyInstaller...
    pip install pyinstaller
) else (
    echo [1/3] PyInstaller 已安装
)

echo.
echo [2/3] 开始构建主程序...
pyinstaller --clean build_main.spec
if errorlevel 1 (
    echo 构建失败！
    pause
    exit /b 1
)

echo.
echo [3/3] 开始构建服务程序...
pyinstaller --clean build_service.spec
if errorlevel 1 (
    echo 构建失败！
    pause
    exit /b 1
)

echo.
echo ========================================
echo 构建完成！
echo ========================================
echo.
echo 输出文件:
echo   - dist\宽带拨号助手.exe (主程序)
echo   - dist\TPLinkCleanupService.exe (服务程序)
echo.
pause
