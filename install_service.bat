@echo off
chcp 65001 > nul
echo ========================================
echo TP-Link Broadband Dialer Service
echo Installation Script
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

echo [1/4] Checking installation files...
if not exist "dist\TPLinkDialerService\TPLinkDialerService.exe" (
    echo ERROR: Service executable not found!
    echo.
    echo Please run build_service.bat first to build the service.
    echo.
    pause
    exit /b 1
)

if not exist "dist\ServiceManager\ServiceManager.exe" (
    echo ERROR: Service manager not found!
    echo.
    echo Please run build_service.bat first to build the service manager.
    echo.
    pause
    exit /b 1
)

echo.
echo [2/4] Installing TP-Link Broadband Dialer Service...
echo.

REM Install the service
dist\TPLinkDialerService\TPLinkDialerService.exe install

if errorlevel 1 (
    echo.
    echo ERROR: Service installation failed!
    echo.
    pause
    exit /b 1
)

echo.
echo [3/4] Starting the service...
echo.

REM Start the service
net start TPLinkBroadbandDialer

if errorlevel 1 (
    echo.
    echo WARNING: Service failed to start automatically.
    echo You can start it manually from the Service Manager.
    echo.
)

echo.
echo [4/4] Opening Service Manager...
echo.

REM Open service manager
start "" "dist\ServiceManager\ServiceManager.exe"

echo.
echo ========================================
echo Installation completed!
echo ========================================
echo.
echo Service Information:
echo - Service Name: TPLinkBroadbandDialer
echo - Display Name: TP-Link Broadband Dialer Service
echo - Startup Type: Automatic
echo.
echo The service is now installed and will start automatically
echo when the system boots up.
echo.
echo When shutting down the system, the service will:
echo 1. Intercept the shutdown event
echo 2. Disconnect the broadband dialer
echo 3. Clear account information
echo 4. Allow the system to shut down
echo.
echo You can use the Service Manager to:
echo - Start/Stop the service
echo - View service status
echo - View service logs
echo - Open the control panel
echo.
pause
