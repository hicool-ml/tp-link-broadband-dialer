@echo off
echo ============================================================
echo  GPO关机脚本测试工具
echo ============================================================
echo.

echo [1/5] 清空日志...
echo. > "C:\ProgramData\BroadbandDialer\cleanup.log"
if exist "C:\ProgramData\BroadbandDialer\cleanup_http.log" del "C:\ProgramData\BroadbandDialer\cleanup_http.log"
echo 日志已清空
echo.

echo [2/5] 验证GPO注册...
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Shutdown\0\0" /v Script
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Shutdown\0\0" /v Parameters
echo.

echo [3/5] 手动测试PowerShell脚本...
powershell -ExecutionPolicy Bypass -File "C:\Program Files (x86)\Broadband_Dialer\cleanup.ps1"
echo.

echo [4/5] 显示日志...
echo === cleanup.log (PowerShell) ===
type "C:\ProgramData\BroadbandDialer\cleanup.log"
echo.
echo === cleanup_http.log (Python) ===
type "C:\ProgramData\BroadbandDialer\cleanup_http.log"
echo.

echo [5/5] 准备重启测试...
echo ============================================================
echo  手动测试完成！
echo ============================================================
echo.
echo 现在请测试关机功能：
echo 1. 保存所有工作
echo 2. 运行: shutdown /r /t 0
echo 3. 重启后重新登录
echo 4. 运行此脚本查看日志
echo.
echo 或者测试关机功能：
echo 1. 保存所有工作
echo 2. 运行: shutdown /s /t 0
echo 3. 下次开机后运行此脚本查看日志
echo.
echo ⚠️ 重要：GPO脚本更改必须重启后才会生效！
echo.
pause
