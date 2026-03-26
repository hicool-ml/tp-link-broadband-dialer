@echo off
setlocal

REM Get script directory
set "SCRIPT_DIR=%~dp0"

REM Set log directory
set "LOG_DIR=C:\ProgramData\BroadbandDialer"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

set "LOG_FILE=%LOG_DIR%\cleanup.log"

REM Write log
echo %date% %time% - === GPO Batch triggered === >> "%LOG_FILE%"

REM Run cleanup_http.exe directly
"%SCRIPT_DIR%cleanup_http.exe" >> "%LOG_FILE%" 2>&1

echo %date% %time% - === GPO Batch finished === >> "%LOG_FILE%"

endlocal
