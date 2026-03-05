@echo off
chcp 65001 > nul
echo ========================================
echo Building TP-Link Dialer Service (onedir)
echo ========================================
echo.

REM Check if Python is installed
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/3] Checking PyInstaller...
python -m PyInstaller --version > nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found, installing...
    python -m pip install pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple
)

echo.
echo [2/3] Building service EXE (onedir mode)...
echo.

REM Build service (onedir mode)
python -m PyInstaller ^
    --onedir ^
    --add-data "chrome-win64;chrome-win64" ^
    --hidden-import playwright.sync_api ^
    --hidden-import playwright.async_api ^
    --hidden-import playwright ^
    --collect-all playwright ^
    --noupx ^
    --windowed ^
    --name "TPLinkDialerService" ^
    --icon "app.ico" ^
    tp_link_broadband_dialer_service.py

if errorlevel 1 (
    echo.
    echo ERROR: Service build failed!
    pause
    exit /b 1
)

echo.
echo [3/3] Building service manager EXE (onedir mode)...
echo.

REM Build service manager (onedir mode)
python -m PyInstaller ^
    --onedir ^
    --noupx ^
    --windowed ^
    --name "ServiceManager" ^
    --icon "app.ico" ^
    service_manager.py

if errorlevel 1 (
    echo.
    echo ERROR: Service manager build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo Output directories:
echo - dist\TPLinkDialerService\  (Service)
echo - dist\ServiceManager\        (Service Manager)
echo.
echo Service manager: dist\ServiceManager\ServiceManager.exe
echo Service executable: dist\TPLinkDialerService\TPLinkDialerService.exe
echo.
echo Next steps:
echo 1. Run ServiceManager.exe to install the service
echo 2. Start the service from ServiceManager
echo 3. The service will run automatically on system startup
echo.
pause
