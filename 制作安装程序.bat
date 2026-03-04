@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

title Broadband Dialer - Create Installer
cls
echo ========================================
echo Broadband Dialer - Create Installer
echo ========================================
echo.
echo Working directory: %CD%
echo.

REM Check NSIS installation
echo [1/5] Checking NSIS installation...
set "NSIS_PATH=C:\Program Files (x86)\NSIS"
if exist "!NSIS_PATH!\makensis.exe" (
    echo [OK] Found NSIS: !NSIS_PATH!
    set "MAKENSIS=!NSIS_PATH!\makensis.exe"
) else (
    set "NSIS_PATH=C:\Program Files\NSIS"
    if exist "!NSIS_PATH!\makensis.exe" (
        echo [OK] Found NSIS: !NSIS_PATH!
        set "MAKENSIS=!NSIS_PATH!\makensis.exe"
    ) else (
        echo [ERROR] NSIS compiler not found
        echo Expected locations:
        echo   - C:\Program Files (x86)\NSIS\makensis.exe
        echo   - C:\Program Files\NSIS\makensis.exe
        echo.
        echo Please install NSIS from: nsis.sourceforge.io
        echo.
        pause
        exit /b 1
    )
)

echo.
echo [2/5] Checking package files...
if not exist "dist\Broadband_Dialer" (
    echo [ERROR] Package folder not found: dist\Broadband_Dialer
    echo.
    echo Please run the package script first to create the program files.
    echo Expected: dist\Broadband_Dialer\*.exe
    echo.
    pause
    exit /b 1
)
echo [OK] Package folder found

echo.
echo [3/5] Checking icon file...
if not exist "app.ico" (
    echo [WARNING] Icon file not found: app.ico
    echo Will use default icon
) else (
    echo [OK] Icon file found
)

echo.
echo [4/5] Checking NSIS script...
if not exist "installer.nsi" (
    echo [ERROR] NSIS script not found: installer.nsi
    echo.
    pause
    exit /b 1
)
echo [OK] NSIS script found

echo.
echo [5/5] Compiling installer...
echo.
echo Command: "!MAKENSIS!" installer.nsi
echo.

REM Create release folder
if not exist "Release" mkdir "Release"

REM Compile NSIS script
"!MAKENSIS!" "installer.nsi"

if errorlevel 1 (
    echo.
    echo ========================================
    echo [ERROR] Compilation failed!
    echo ========================================
    echo.
    echo Please check:
    echo 1. NSIS script syntax: installer.nsi
    echo 2. Package files exist: dist\Broadband_Dialer\
    echo 3. Sufficient disk space
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Compilation Successful!
echo ========================================
echo.
echo Output file: Release\Broadband-Dialer-Setup.exe
echo.

REM Check if output file was created
if exist "Release\Broadband-Dialer-Setup.exe" (
    echo [OK] Installer created successfully
    for %%A in ("Release\Broadband-Dialer-Setup.exe") do (
        echo Size: %%~zA bytes
    )
) else (
    echo [WARNING] Output file not found
)

echo.
echo ========================================
echo Installer Features
echo ========================================
echo.
echo - Install to: C:\Program Files\Broadband_Dialer
echo - Create desktop shortcut
echo - Create start menu shortcut
echo - Support uninstall
echo.

echo ========================================
echo Usage Instructions
echo ========================================
echo.
echo 1. Copy Release\Broadband-Dialer-Setup.exe to target machine
echo 2. Double-click to run installer
echo 3. Follow the prompts to complete installation
echo 4. Launch from desktop or start menu
echo.
echo ========================================
echo Press any key to exit...
echo ========================================
pause >nul
exit /b 0
