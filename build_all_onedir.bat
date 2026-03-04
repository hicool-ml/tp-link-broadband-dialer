@echo off
chcp 65001 >nul
echo ========================================
echo   Broadband Dialer - One-Click Build
echo   (onedir mode + installer)
echo ========================================
echo.
echo This script will:
echo   1. Build EXE (onedir mode, low resource usage)
echo   2. Build installer (NSIS)
echo   3. Output: Release\Broadband_Dialer_Setup.exe
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul
echo.

cd /d "%~dp0"

:: Step 1: Build EXE (onedir mode)
echo ========================================
echo [Step 1/2] Building EXE (onedir mode)...
echo ========================================
echo.

call build_exe_onedir.bat

if errorlevel 1 (
    echo.
    echo ========================================
    echo [Error] EXE build failed!
    echo ========================================
    pause
    exit /b 1
)
echo.

:: Step 2: Build installer
echo ========================================
echo [Step 2/2] Building installer...
echo ========================================
echo.

call build_installer.bat

if errorlevel 1 (
    echo.
    echo ========================================
    echo [Error] Installer build failed!
    echo ========================================
    pause
    exit /b 1
)
echo.

echo ========================================
echo   All Build Completed!
echo ========================================
echo.
echo Output files:
echo   - EXE: dist\TP-Link_Dialer\TP-Link_Dialer.exe
echo   - Installer: Release\Broadband_Dialer_Setup.exe
echo.
echo Features:
echo   - Low resource usage (onedir mode)
echo   - Fast startup (1-2 seconds)
echo   - Desktop shortcut: Broadband Connection
echo   - Start menu: Broadband Connection
echo   - Zero dependencies (no Python/Chrome needed)
echo.
echo Press any key to exit...
pause >nul
