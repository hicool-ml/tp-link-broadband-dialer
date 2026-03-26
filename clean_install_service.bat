@echo off
chcp 65001 >nul
echo ========================================
echo   Clean Install Service
echo ========================================
echo.

echo [1/4] Stopping service (if running)...
net stop TPLinkShutdownCleanup 2>nul
echo.

echo [2/4] Deleting old service...
sc delete TPLinkShutdownCleanup 2>nul
if errorlevel 1 (
    echo Service marked for deletion, waiting 5 seconds...
    timeout /t 5 /nobreak >nul
)
echo.

echo [3/4] Installing new service...
cd /d "D:\13jiao\dist_new2\CleanupService"
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
