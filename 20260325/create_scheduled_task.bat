@echo off
chcp 65001 >nul

set TASK_NAME=TPLinkCleanup
set EXE_PATH=D:\13jiao\20260325\cleanup_http.exe
set PS_PATH=D:\13jiao\20260325\cleanup.ps1

echo 删除旧任务...
schtasks /Delete /TN "%TASK_NAME%" /F 2>nul

echo 创建关机触发任务...
schtasks /Create /TN "%TASK_NAME%" /TR "powershell.exe -ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File \"%PS_PATH%\"" /SC ONEVENT /EC System /MO "*[System[(EventID=1074 or EventID=6006)]]" /RU SYSTEM /RL HIGHEST /F

if errorlevel 1 (
    echo 任务创建失败！
    pause
    exit /b 1
)

echo.
echo 任务创建成功！
schtasks /Query /TN "%TASK_NAME%" /FO LIST
echo.
echo 测试运行（立即执行一次）:
schtasks /Run /TN "%TASK_NAME%"
timeout /t 3 /nobreak >nul
echo.
echo 日志:
type "C:\ProgramData\BroadbandDialer\cleanup.log"

pause
