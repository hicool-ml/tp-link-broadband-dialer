@echo off
chcp 65001 >nul
echo ========================================
echo 服务 1053 测试 - 简化版代码
echo ========================================
echo.

cd /d %~dp0

echo [1/4] 卸载旧服务...
dist\TPLinkCleanupService.exe remove 2>nul

echo.
echo [2/4] 安装新服务...
dist\TPLinkCleanupService.exe install

if errorlevel 1 (
    echo [ERROR] 服务安装失败！
    pause
    exit /b 1
)

echo.
echo [3/4] 启动服务...
net start TPLinkShutdownCleanup

if errorlevel 1 (
    echo [ERROR] 服务启动失败！
    echo.
    echo 可能原因：
    echo   - Error 1053: 服务启动超时
    echo   - Error 1060: 服务未安装
    echo.
    pause
    exit /b 1
)

echo.
echo [4/4] 检查服务状态...
sc query TPLinkShutdownCleanup

echo.
echo ========================================
echo 测试完成！
echo ========================================
echo.
echo 如果 STATE 是 4 RUNNING，说明 1053 已修复！
echo.
echo 日志位置: %TEMP%\tplink_cleanup\cleanup_service.log
echo.

pause
