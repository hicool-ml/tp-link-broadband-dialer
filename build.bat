@echo off
cd /d "%~dp0"
if not exist Release mkdir Release
"C:\Program Files (x86)\NSIS\makensis.exe" installer.nsi
if errorlevel 1 (
    echo Compilation failed
    pause
    exit /b 1
)
echo Success
pause
