@echo off
chcp 65001 >nul
echo ========================================
echo   Reinstall TP-Link Cleanup Service
echo ========================================
echo.

cd /d "D:\13jiao\dist\CleanupService"

echo [1/3] Removing old service...
CleanupService.exe remove
echo.

echo [2/3] Installing service...
CleanupService.exe install
echo.

echo [3/3] Starting service...
sc start TPLinkShutdownCleanup
echo.

echo Checking service status...
sc query TPLinkShutdownCleanup
echo.

echo Done! Press any key to exit...
pause >nul
