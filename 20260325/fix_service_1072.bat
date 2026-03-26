@echo off
echo ========================================
echo 修复服务 1072 错误
echo ========================================
echo.

echo [1/3] 停止服务...
net stop TPLinkShutdownCleanup 2>nul

echo.
echo [2/3] 强制删除服务标记...
sc delete TPLinkShutdownCleanup

if errorlevel 1 (
    echo.
    echo [ERROR] 删除失败，可能需要重启电脑
    echo.
    echo 原因：服务被标记为删除后，需要重启才能彻底清除
    echo.
    echo 临时解决方案：
    echo   1. 重启电脑后，旧服务会自动清除
    echo   2. 然后重新运行 install_service.bat
    echo.
    pause
    exit /b 1
)

echo.
echo [3/3] 等待2秒后重新安装...
timeout /t 2 >nul

echo.
echo 正在安装服务...
dist\TPLinkCleanupService.exe install

if errorlevel 1 (
    echo.
    echo [ERROR] 安装失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 服务安装成功！
echo ========================================
echo.
echo 正在启动服务...
net start TPLinkShutdownCleanup

if errorlevel 1 (
    echo.
    echo [ERROR] 启动失败（可能是1053错误）
    echo.
    echo 请检查：
    echo   1. 事件查看器中的错误信息
    echo   2. 日志文件: %%TEMP%%\tplink_cleanup\cleanup_service.log
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo 服务启动成功！
echo ========================================
echo.
echo 检查服务状态：
sc query TPLinkShutdownCleanup

echo.
echo 如果 STATE 是 4 RUNNING，说明 1053 已修复！
echo.
pause
