@echo off
chcp 65001 >nul
echo ========================================
echo   Force Delete and Reinstall Service
echo ========================================
echo.

echo [Step 1] Stop service (if running)...
sc stop TPLinkShutdownCleanup 2>nul
timeout /t 2 /nobreak >nul
echo.

echo [Step 2] Force delete service...
sc delete TPLinkShutdownCleanup
if errorlevel 1 (
    echo Service is marked for deletion.
    echo This usually requires a system restart.
    echo.
    echo Would you like to restart now? (y/n)
    set /p restart=
    if /i "%restart%"=="y" (
        shutdown /r /t 10 /c "Restarting to complete service removal"
        echo System will restart in 10 seconds...
        echo Press any key to cancel restart...
        pause >nul
        shutdown /a
        echo Restart cancelled.
    )
    goto :end
)
echo Service deleted successfully.
echo.

:end
pause
