@echo off
chcp 65001 >nul
echo Updating Release directory and rebuilding Setup.exe...

echo.
echo [1/3] Update Release directory...
rmdir /s /q Release\CleanupService 2>nul
xcopy /E /I /Y dist\CleanupService Release\CleanupService
echo CleanupService updated

echo.
echo [2/3] Rebuild Setup.exe...
"C:\Program Files (x86)\NSIS\makensis.exe" /V2 Setup.nsi >nul 2>&1

if exist Release\Setup.exe (
    echo Setup.exe rebuilt successfully
    echo.
    echo [3/3] File info:
    dir Release\Setup.exe | find "Setup.exe"
) else (
    echo ERROR: Setup.exe not generated!
)

echo.
pause
