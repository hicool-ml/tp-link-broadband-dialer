@echo off
chcp 65001 >nul
echo ========================================
echo 安装TP-Link路由器清理服务(HTTP版)
echo ========================================
echo.

cd /d %~dp0

echo [1/4] 卸载旧服务...
python service_http.py remove 2>nul

echo.
echo [2/4] 安装服务...
python service_http.py install

if errorlevel 1 (
    echo [ERROR] 服务安装失败！
    pause
    exit /b 1
)

echo.
echo [3/4] 启动服务...
net start TPLinkCleanupHTTP2

if errorlevel 1 (
    echo [ERROR] 服务启动失败！
    pause
    exit /b 1
)

echo.
echo [4/4] 检查服务状态...
sc query TPLinkCleanupHTTP2

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 日志位置: %TEMP%\tplink_cleanup\cleanup_service.log
echo.

pause
