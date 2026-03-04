@echo off
chcp 65001 >nul
echo ========================================
echo   Broadband Dialer - Build Script
echo   (onedir mode, low resource usage)
echo ========================================
echo.

cd /d "%~dp0"

:: Check Python installation
echo [1/5] Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo [Error] Python not found
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)
python --version
echo [OK] Python environment check passed
echo.

:: Check browser directory
echo [2/5] Checking browser files...
if exist "chrome-win64\chrome.exe" (
    echo [OK] Found project browser: chrome-win64\chrome.exe
) else if exist "chromium-mini\chrome.exe" (
    echo [OK] Found mini browser: chromium-mini\chrome.exe
) else if exist "ms-playwright\chromium-1208\chrome-win64\chrome.exe" (
    echo [OK] Found full browser: ms-playwright\chromium-1208\chrome-win64\chrome.exe
) else (
    echo [Error] Browser files not found!
    echo.
    echo Please place Chrome browser files in one of these locations:
    echo   1. chrome-win64\chrome.exe (project built-in, recommended)
    echo   2. chromium-mini\chrome.exe (mini version)
    echo   3. ms-playwright\chromium-1208\chrome-win64\chrome.exe (full version)
    echo.
    pause
    exit /b 1
)
echo.

:: Clean old build files
echo [3/5] Cleaning old build files...
if exist "dist" rd /s /q "dist"
if exist "build" rd /s /q "build"
if exist "TP-Link_Dialer.spec" del /f /q "TP-Link_Dialer.spec"
echo [OK] Clean completed
echo.

:: Build command (zero-dependency config + onedir mode)
echo [4/5] Building with PyInstaller (onedir mode)...
echo.

:: Select browser data based on available browser
if exist "chrome-win64\chrome.exe" (
    echo [Info] Using project built-in browser...
    set "BROWSER_DATA=chrome-win64;chrome-win64"
) else if exist "chromium-mini\chrome.exe" (
    echo [Info] Using mini browser...
    set "BROWSER_DATA=chromium-mini;chromium-mini"
) else (
    echo [Info] Using full browser...
    set "BROWSER_DATA=ms-playwright;ms-playwright"
)

python -m PyInstaller ^
  --onedir ^
  --windowed ^
  --name "TP-Link_Dialer" ^
  --icon "app.ico" ^
  --add-data "%BROWSER_DATA%" ^
  --add-data "app.ico;." ^
  --add-data "connecting.ico;." ^
  --add-data "error.ico;." ^
  --add-data "offline.ico;." ^
  --add-data "online.ico;." ^
  --hidden-import=playwright.sync_api ^
  --hidden-import=playwright._impl._api_types ^
  --hidden-import=playwright._impl._browser ^
  --hidden-import=playwright._impl._connection ^
  --hidden-import=tkinter ^
  --hidden-import=queue ^
  --hidden-import=threading ^
  --hidden-import=ctypes ^
  --hidden-import=re ^
  --hidden-import=time ^
  --hidden-import=subprocess ^
  --hidden-import=atexit ^
  --hidden-import=tempfile ^
  --collect-all playwright ^
  --exclude-module=unittest ^
  --exclude-module=setuptools ^
  --exclude-module=pip ^
  --exclude-module=email ^
  --exclude-module=pydoc ^
  --exclude-module=doctest ^
  --clean ^
  --noupx ^
  --noconfirm ^
  tp_link_broadband_dialer.py

if errorlevel 1 (
    echo.
    echo [Error] Build failed!
    echo.
    echo Possible reasons:
    echo 1. Python dependencies not installed
    echo 2. Browser file path incorrect
    echo 3. PyInstaller version incompatible
    echo.
    echo Please check error messages and retry
    pause
    exit /b 1
)
echo.

:: Display build results
echo [5/5] Build completed!
echo ========================================
echo [OK] Zero-dependency version built! (onedir mode)
echo ========================================
echo.
echo Output directory: dist\TP-Link_Dialer\
echo Main program: dist\TP-Link_Dialer\TP-Link_Dialer.exe
echo.
echo Resource usage comparison:
echo   --onedir mode (current):
echo     - Main program: 50-100 MB
echo     - Runtime temp space: Not needed
echo     - Startup speed: Fast (1-2 seconds)
echo.
echo   --onefile mode (single file):
echo     - Main program: 400-500 MB
echo     - Runtime temp space: Need 400-500 MB
echo     - Startup speed: Slow (5-10 seconds)
echo.
echo Advantages:
echo   - Fast startup (no extraction needed)
echo   - Low resource usage (no temp space needed)
echo   - Small memory footprint (load on demand)
echo   - Easy updates (only update changed files)
echo.
echo Distribution methods:
echo   1. Compress dist\TP-Link_Dialer\ directory to ZIP
echo   2. Use NSIS to create installer (recommended)
echo   3. Use build_installer.bat to auto-create installer
echo.
echo Press any key to exit...
pause >nul
