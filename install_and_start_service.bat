@echo off
echo ========================================
echo   安装并启动 TP-Link 清理服务
echo ========================================
echo.

cd /d "D:\13jiao\dist\CleanupService"

echo [1/2] 正在安装服务...
CleanupService.exe install
echo.

echo [2/2] 正在启动服务...
sc start TPLinkShutdownCleanup
echo.

echo 检查服务状态...
sc query TPLinkShutdownCleanup
echo.

echo ========================================
echo   完成！
echo ========================================
pause
