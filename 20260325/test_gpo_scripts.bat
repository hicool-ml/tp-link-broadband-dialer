@echo off
echo ============================================================
echo  GPO脚本验证工具
echo ============================================================
echo.

echo [1/6] 检查Shutdown脚本注册...
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Shutdown\0" /v List >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Shutdown脚本已注册
) else (
    echo [ERROR] Shutdown脚本未注册！
)
echo.

echo [2/6] 检查Logoff脚本注册...
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Logoff\0" /v List >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Logoff脚本已注册
) else (
    echo [ERROR] Logoff脚本未注册！
)
echo.

echo [3/6] 显示Shutdown脚本详情...
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Shutdown\0" /v DisplayName
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Shutdown\0" /v List
echo.

echo [4/6] 显示Logoff脚本详情...
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Logoff\0" /v DisplayName
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Logoff\0" /v List
echo.

echo [5/6] 检查cleanup.log...
if exist "C:\ProgramData\BroadbandDialer\cleanup.log" (
    echo [OK] 日志文件存在
    echo.
    echo === 最新10条日志 ===
    powershell -Command "Get-Content 'C:\ProgramData\BroadbandDialer\cleanup.log' -Tail 10"
) else (
    echo [INFO] 日志文件不存在（可能还没执行过）
)
echo.

echo [6/6] 刷新组策略...
echo 正在刷新组策略...
gpupdate /Force
echo.

echo ============================================================
echo  验证完成！
echo ============================================================
echo.
echo 测试步骤：
echo 1. 注销当前用户（Win+L，然后重新登录）
echo 2. 检查路由器是否断开
echo 3. 检查日志：type "C:\ProgramData\BroadbandDialer\cleanup.log"
echo.
pause
