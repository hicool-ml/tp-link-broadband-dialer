@echo off
chcp 65001 >nul
echo ========================================
echo 安装 TP-Link 关机清理服务
echo ========================================
echo.

cd /d %~dp0

echo [1/2] 停止并删除旧服务（如果存在）...
dist\TPLinkCleanupService.exe remove 2>nul

echo.
echo [2/2] 安装并启动新服务...
dist\TPLinkCleanupService.exe install

timeout /t 2 >nul

echo.
echo 检查服务状态...
sc query TPLinkShutdownCleanup

echo.
echo ========================================
echo 服务安装完成！
echo ========================================
echo.
echo 日志位置: %%TEMP%%\tplink_cleanup\cleanup_service.log
echo.
pause
