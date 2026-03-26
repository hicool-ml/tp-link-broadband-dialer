@echo off
chcp 65001 >nul
echo ========================================
echo   Installing Service Version 3
echo ========================================
echo.

echo [1/4] Stopping service...
net stop TPLinkShutdownCleanup 2>nul
echo.

echo [2/4] Deleting old service...
sc delete TPLinkShutdownCleanup 2>nul
if errorlevel 1 (
    echo Service marked for deletion, waiting...
    timeout /t 5 /nobreak >nul
)
echo.

echo [3/4] Installing service v3...
cd /d "D:\13jiao\dist_v3\CleanupService"
CleanupService.exe install
echo.

echo [4/4] Starting service...
sc start TPLinkShutdownCleanup
echo.

echo Waiting 5 seconds...
timeout /t 5 /nobreak >nul

echo Checking status...
sc query TPLinkShutdownCleanup
echo.

echo Checking logs...
if exist "%TEMP%\tplink_cleanup\cleanup_service.log" (
    echo --- Log file contents ---
    type "%TEMP%\tplink_cleanup\cleanup_service.log"
) else (
    echo Log file not found
)
echo.

pause
