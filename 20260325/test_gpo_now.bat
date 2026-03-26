@echo off
echo ============================================================
echo  GPO脚本快速测试工具
echo ============================================================
echo.

echo [1/4] 清空日志...
echo. > "C:\ProgramData\BroadbandDialer\cleanup.log"
if exist "C:\ProgramData\BroadbandDialer\cleanup_http.log" del "C:\ProgramData\BroadbandDialer\cleanup_http.log"
echo 日志已清空
echo.

echo [2/4] 验证GPO注册...
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Shutdown\0" /v List >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Shutdown脚本已注册
    reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Shutdown\0\0" /v Script
) else (
    echo [ERROR] Shutdown脚本未注册！
)
echo.

reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Logoff\0" /v List >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Logoff脚本已注册
    reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Logoff\0\0" /v Script
) else (
    echo [ERROR] Logoff脚本未注册！
)
echo.

echo [3/4] 手动测试批处理文件...
"C:\Program Files (x86)\Broadband_Dialer\cleanup.bat"
echo.

echo [4/4] 显示日志...
echo === cleanup.log (batch file) ===
type "C:\ProgramData\BroadbandDialer\cleanup.log"
echo.
echo === cleanup_http.log (Python exe) ===
type "C:\ProgramData\BroadbandDialer\cleanup_http.log"
echo.

echo ============================================================
echo  手动测试完成！
echo ============================================================
echo.
echo 现在请测试注销功能：
echo 1. 按 Win+L 注销
echo 2. 重新登录
echo 3. 运行此脚本查看日志
echo.
pause
