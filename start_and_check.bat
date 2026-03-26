@echo off
chcp 65001 >nul
echo Starting service...
sc start TPLinkShutdownCleanup
echo.
echo Waiting 5 seconds...
timeout /t 5 /nobreak >nul
echo.
echo Checking status...
sc query TPLinkShutdownCleanup
echo.
echo Checking logs...
if exist "%TEMP%\tplink_cleanup\cleanup_service.log" (
    type "%TEMP%\tplink_cleanup\cleanup_service.log"
) else (
    echo Log file not found at %TEMP%\tplink_cleanup\cleanup_service.log
)
echo.
pause
