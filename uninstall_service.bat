@echo off
chcp 65001 > nul
echo ========================================
echo TP-Link Broadband Dialer Service
echo Uninstallation Script
echo ========================================
echo.

REM Check for administrator privileges
net session > nul 2>&1
if errorlevel 1 (
    echo ERROR: This script requires administrator privileges!
    echo.
    echo Please right-click this script and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo [1/3] Stopping the service...
echo.

REM Stop the service
net stop TPLinkBroadbandDialer > nul 2>&1
if errorlevel 1 (
    echo Service was not running or already stopped.
) else (
    echo Service stopped successfully.
)

echo.
echo [2/3] Removing the service...
echo.

REM Remove the service
dist\TPLinkDialerService\TPLinkDialerService.exe remove

if errorlevel 1 (
    echo.
    echo ERROR: Service removal failed!
    echo.
    pause
    exit /b 1
)

echo.
echo [3/3] Cleaning up...
echo.

REM Close service manager if running
taskkill /F /IM ServiceManager.exe > nul 2>&1

echo.
echo ========================================
echo Uninstallation completed!
echo ========================================
echo.
echo The TP-Link Broadband Dialer Service has been removed.
echo.
echo IMPORTANT: After uninstalling the service:
echo - The system will NOT automatically disconnect dialer on shutdown
echo - The system will NOT automatically clear account information on shutdown
echo.
echo If you want to reinstall the service later, run install_service.bat
echo.
pause
