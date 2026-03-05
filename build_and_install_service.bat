@echo off
chcp 65001 > nul
echo ========================================
echo TP-Link Broadband Dialer Service
echo Build and Install Script
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

echo [1/3] Checking dependencies...
echo.

REM Check if Python is installed
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo Python found: 
python --version

echo.
echo [2/3] Building service...
echo.

REM Run build script
call build_service.bat

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo [3/3] Installing service...
echo.

REM Run install script
call install_service.bat

if errorlevel 1 (
    echo.
    echo ERROR: Installation failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo All done!
echo ========================================
echo.
echo The service has been built and installed successfully.
echo.
echo You can now:
echo - Use the Service Manager to manage the service
echo - Open the Control Panel to configure the router
echo - View logs at: %%TEMP%%\tplink_dialer\service.log
echo.
pause
