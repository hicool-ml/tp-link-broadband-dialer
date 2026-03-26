@echo off
echo Generating Setup.exe with NSIS...
"C:\Program Files (x86)\NSIS\makensis.exe" Setup.nsi
if %ERRORLEVEL% equ 0 (
    echo.
    echo ========================================
    echo   Setup.exe generated successfully!
    echo ========================================
    echo.
    dir Release\Setup.exe
) else (
    echo Failed to generate Setup.exe
)
pause
