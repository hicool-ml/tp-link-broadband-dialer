@echo off
chcp 65001 >nul
echo ========================================
echo   Broadband Dialer - Build Installer
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] Checking required files...
if not exist "dist\TP-Link_Dialer\TP-Link_Dialer.exe" (
    echo [Error] dist\TP-Link_Dialer\TP-Link_Dialer.exe not found
    echo Please run build_exe_onedir.bat first
    pause
    exit /b 1
)
echo [OK] Found exe file

if not exist "TP-Link_Dialer.nsi" (
    echo [Error] TP-Link_Dialer.nsi not found
    pause
    exit /b 1
)
echo [OK] Found NSIS script

if not exist "license.txt" (
    echo [Error] license.txt not found
    pause
    exit /b 1
)
echo [OK] Found license file

if not exist "app.ico" (
    echo [Error] app.ico not found
    pause
    exit /b 1
)
echo [OK] Found icon file
echo.

echo [2/4] Checking NSIS installation...
set NSIS_PATH=""
if exist "C:\Program Files (x86)\NSIS\makensis.exe" (
    set "NSIS_PATH=C:\Program Files (x86)\NSIS\makensis.exe"
)
if exist "C:\Program Files\NSIS\makensis.exe" (
    set "NSIS_PATH=C:\Program Files\NSIS\makensis.exe"
)
if "%NSIS_PATH%"=="" (
    echo [Error] NSIS not found, please install NSIS first
    echo Download: https://nsis.sourceforge.io/
    pause
    exit /b 1
)
echo [OK] Found NSIS: %NSIS_PATH%
echo.

echo [3/4] Creating release directory...
if not exist "发布包" mkdir "发布包"
echo [OK] Release directory created
echo.

echo [4/4] Building installer...
echo Compiling installer with NSIS...
echo.

"%NSIS_PATH%" TP-Link_Dialer.nsi

if errorlevel 1 (
    echo.
    echo [Error] Installer build failed!
    pause
    exit /b 1
)
echo.

echo ========================================
echo   Build Completed!
echo   Installer: 发布包\Broadband_Dialer_Setup.exe
echo ========================================
echo.
echo Features:
echo   - Desktop shortcut: 宽带连接
echo   - Start menu: 宽带连接
echo   - Low resource usage (onedir mode)
echo.
echo Press any key to exit...
pause >nul
