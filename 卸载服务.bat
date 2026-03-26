@echo off
chcp 65001 >nul
echo ========================================
echo 卸载 TP-Link 关机清理服务
echo ========================================
echo.

echo 正在停止服务...
sc stop TPLinkShutdownCleanup
timeout /t 2 >nul

echo.
echo 正在删除服务...
sc delete TPLinkShutdownCleanup

echo.
echo ========================================
echo 服务卸载完成！
echo ========================================
echo.
pause
