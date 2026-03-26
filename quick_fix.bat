@echo off
chcp 65001 >nul
echo ========================================
echo   快速修复 - 浏览器路径问题
echo ========================================
echo.

REM 检查是否有管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo 需要管理员权限来复制文件到 Program Files
    echo 请右键点击此文件，选择"以管理员身份运行"
    pause
    exit /b 1
)

echo 此脚本将用新版本的主程序替换已安装的版本
echo.

REM 检查源文件是否存在
if not exist "dist\TP-Link_Dialer\TP-Link_Dialer.exe" (
    echo 错误: 找不到新版本的主程序
    echo 请确保已执行构建
    pause
    exit /b 1
)

REM 检查目标目录是否存在
if not exist "C:\Program Files\TPLinkDialer" (
    echo 错误: 程序未安装
    echo 请先运行安装程序
    pause
    exit /b 1
)

echo 源文件: dist\TP-Link_Dialer\TP-Link_Dialer.exe
echo 目标位置: C:\Program Files\TPLinkDialer\TP-Link_Dialer.exe
echo.

REM 停止正在运行的程序
taskkill /F /IM TP-Link_Dialer.exe >nul 2>&1
timeout /t 2 >nul

REM 备份旧版本
if exist "C:\Program Files\TPLinkDialer\TP-Link_Dialer.exe" (
    echo 正在备份旧版本...
    copy "C:\Program Files\TPLinkDialer\TP-Link_Dialer.exe" "C:\Program Files\TPLinkDialer\TP-Link_Dialer.exe.bak" >nul
)

REM 复制新版本
echo 正在复制新版本...
copy /Y "dist\TP-Link_Dialer\TP-Link_Dialer.exe" "C:\Program Files\TPLinkDialer\TP-Link_Dialer.exe"

if %errorLevel% equ 0 (
    echo.
    echo ========================================
    echo   修复成功！
    echo ========================================
    echo.
    echo 主程序已更新到新版本
    echo 现在可以启动程序了
    echo.
    start "" "C:\Program Files\TPLinkDialer\TP-Link_Dialer.exe"
) else (
    echo.
    echo ========================================
    echo   修复失败！
    echo ========================================
    echo.
    echo 请手动复制文件或以管理员身份运行
)

pause
