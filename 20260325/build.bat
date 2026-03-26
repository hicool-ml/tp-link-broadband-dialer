@echo off
chcp 65001 >nul
title TP-Link Broadband Dialer - Build Script

echo ========================================
echo TP-Link Broadband Dialer - Build
echo ========================================
echo.

REM Check admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Administrator privileges required!
    echo.
    echo Please right-click this script and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo [OK] Administrator privileges check passed
echo.

REM Check PyInstaller
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [1/5] Installing PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo [ERROR] PyInstaller installation failed!
        pause
        exit /b 1
    )
) else (
    echo [1/5] PyInstaller already installed
)

echo.
echo [2/5] Checking dependencies...
echo     - requests
python -c "import requests" 2>nul
if errorlevel 1 (
    echo     [Installing] requests
    pip install requests
) else (
    echo     [OK] requests
)

echo     - pystray
python -c "import pystray" 2>nul
if errorlevel 1 (
    echo     [Installing] pystray
    pip install pystray
) else (
    echo     [OK] pystray
)

echo     - pillow
python -c "import PIL" 2>nul
if errorlevel 1 (
    echo     [Installing] pillow
    pip install pillow
) else (
    echo     [OK] pillow
)

echo     - pywin32
python -c "import win32service" 2>nul
if errorlevel 1 (
    echo     [Installing] pywin32
    pip install pywin32
) else (
    echo     [OK] pywin32
)

echo.
echo [3/5] Building main program...
python -m PyInstaller --clean --noconfirm build_main.spec
if errorlevel 1 (
    echo [ERROR] Main program build failed!
    pause
    exit /b 1
)

echo [OK] Main program built successfully

echo.
echo [4/5] Building service program...
python -m PyInstaller --clean --noconfirm build_service.spec
if errorlevel 1 (
    echo [ERROR] Service program build failed!
    pause
    exit /b 1
)

echo [OK] Service program built successfully

echo.
echo [5/5] Verifying output files...
if not exist "dist\broadband_dialer.exe" (
    echo [ERROR] Main program exe not found!
    pause
    exit /b 1
)
echo [OK] broadband_dialer.exe

if not exist "dist\TPLinkCleanupService.exe" (
    echo [ERROR] Service exe not found!
    pause
    exit /b 1
)
echo [OK] TPLinkCleanupService.exe

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Output files:
echo   - dist\broadband_dialer.exe (Main program)
echo   - dist\TPLinkCleanupService.exe (Service)
echo.
echo Next steps:
echo   1. Test main program: dist\broadband_dialer.exe
echo   2. Test service: dist\TPLinkCleanupService.exe install
echo   3. Build installer: "C:\Program Files (x86)\NSIS\makensis.exe" setup_build.nsi
echo.
echo ========================================
echo Build completed at: %date% %time%
echo ========================================
echo.

pause
