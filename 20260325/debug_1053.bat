@echo off
chcp 65001 >nul
echo ========================================
echo Debug Service 1053 Error
echo ========================================
echo.

cd /d %~dp0

echo [1/3] Remove old test service...
sc delete TPLinkCleanupTest 2>nul

echo.
echo [2/3] Install test service...
dist\TPLinkCleanupService.exe install

if errorlevel 1 (
    echo.
    echo [ERROR] Install failed!
    pause
    exit /b 1
)

echo.
echo [3/3] Start service and capture error...
net start TPLinkCleanupTest

if errorlevel 1 (
    echo.
    echo [ERROR] Start failed with code: %errorlevel%
    echo.
    echo Check event viewer for details:
    echo   Win+R -^> eventvwr
    echo   Windows Logs -^> Application
    echo   Look for errors from TPLinkCleanupTest
    echo.
    echo Or check service log:
    echo   type %%TEMP%%\tplink_cleanup\cleanup_service.log
    echo.
)

echo.
echo Service status:
sc query TPLinkCleanupTest

echo.
pause
