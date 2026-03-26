@echo off
chcp 65001 >nul
echo Installing and starting TP-Link Cleanup Service...
echo.

cd /d "D:\13jiao\dist\CleanupService"

echo [1/2] Installing service...
CleanupService.exe install
echo.

echo [2/2] Starting service...
sc start TPLinkShutdownCleanup
echo.

echo Checking service status...
sc query TPLinkShutdownCleanup
echo.

echo Done! Press any key to exit...
pause >nul
