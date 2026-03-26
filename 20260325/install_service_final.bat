@echo off
chcp 65001 >nul
title TP-Link路由器清理服务 - 安装

echo ========================================
echo TP-Link路由器清理服务 - 安装程序
echo ========================================
echo.

cd /d %~dp0

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python！
    echo 请确保已安装Python 3.11并添加到PATH
    pause
    exit /b 1
)

echo [1/5] 检查依赖...
python -c "import win32service, win32serviceutil, win32event" 2>nul
if errorlevel 1 (
    echo     安装pywin32...
    pip install pywin32
) else (
    echo     依赖OK
)

echo.
echo [2/5] 卸载旧服务...
python service_http.py remove 2>nul

echo.
echo [3/5] 安装服务...
python service_http.py install
if errorlevel 1 (
    echo [错误] 服务安装失败！
    pause
    exit /b 1
)

echo.
echo [4/5] 启动服务...
net start TPLinkCleanupHTTP2
if errorlevel 1 (
    echo [错误] 服务启动失败！
    echo.
    echo 日志位置: %TEMP%\tplink_cleanup\cleanup_service.log
    pause
    exit /b 1
)

echo.
echo [5/5] 验证服务状态...
sc query TPLinkCleanupHTTP2 | find "STATE"
echo.

echo ========================================
echo 安装成功！
echo ========================================
echo.
echo 服务名称: TPLinkCleanupHTTP2
echo 显示名称: TP-Link路由器清理服务(HTTP v2)
echo.
echo 管理命令:
echo   启动服务: net start TPLinkCleanupHTTP2
echo   停止服务: net stop TPLinkCleanupHTTP2
echo   卸载服务: python service_http.py remove
echo.
echo 日志位置: %TEMP%\tplink_cleanup\cleanup_service.log
echo.

pause
