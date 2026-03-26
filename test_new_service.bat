@echo off
chcp 65001 >nul
echo ========================================
echo   Testing New Service Version
echo ========================================
echo.

cd /d "D:\13jiao\dist_new\CleanupService"

echo [1/3] Removing old service...
CleanupService.exe remove
echo.

echo [2/3] Installing new service...
CleanupService.exe install
echo.

echo [3/3] Starting service...
sc start TPLinkShutdownCleanup
echo.

echo Waiting 3 seconds...
timeout /t 3 /nobreak >nul

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
