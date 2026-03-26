@echo off
chcp 65001 >nul
echo ========================================
echo 测试新服务（临时服务名）
echo ========================================
echo.

cd /d %~dp0

echo 服务名称: TPLinkCleanupTest
echo.

echo [1/3] 安装测试服务...
dist\TPLinkCleanupService.exe install

if errorlevel 1 (
    echo.
    echo [ERROR] 安装失败！
    pause
    exit /b 1
)

echo.
echo [2/3] 启动测试服务...
net start TPLinkCleanupTest

if errorlevel 1 (
    echo.
    echo [ERROR] 启动失败！
    echo.
    echo 如果是 Error 1053，说明还有问题
    echo 如果是其他错误，查看事件查看器
    echo.
    pause
    exit /b 1
)

echo.
echo [3/3] 检查服务状态...
sc query TPLinkCleanupTest

echo.
echo ========================================
echo 测试完成！
echo ========================================
echo.
echo 如果 STATE 是 4 RUNNING，说明 1053 已修复！
echo.
echo 日志位置: %%TEMP%%\tplink_cleanup\cleanup_service.log
echo.
echo 测试完成后删除服务:
echo   sc delete TPLinkCleanupTest
echo.

pause
