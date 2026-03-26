@echo off
echo ============================================================
echo  RunOnce机制测试工具
echo ============================================================
echo.

echo [1/5] 检查安装...
if exist "C:\Program Files\Broadband_Dialer\broadband_dialer.exe" (
    echo [OK] 主程序已安装
) else (
    echo [ERROR] 主程序未安装！
    pause
    exit /b 1
)

if exist "C:\Program Files\Broadband_Dialer\cleanup_http.exe" (
    echo [OK] 清理程序已安装
) else (
    echo [ERROR] 清理程序未安装！
)

if exist "C:\Program Files\Broadband_Dialer\cleanup.ps1" (
    echo [OK] PowerShell脚本已安装
) else (
    echo [ERROR] PowerShell脚本未安装！
)
echo.

echo [2/5] 检查RunOnce注册...
reg query "HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce" /v TPLinkCleanup
if %errorlevel% equ 0 (
    echo [OK] RunOnce已注册
) else (
    echo [INFO] RunOnce未注册（正常，关机前会自动注册）
)
echo.

echo [3/5] 手动注册RunOnce测试...
powershell -ExecutionPolicy Bypass -File "C:\Program Files\Broadband_Dialer\cleanup.ps1"
echo.

echo [4/5] 验证RunOnce注册...
reg query "HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce" /v TPLinkCleanup
if %errorlevel% equ 0 (
    echo [OK] RunOnce注册成功
) else (
    echo [ERROR] RunOnce注册失败
)
echo.

echo [5/5] 显示日志...
if exist "C:\ProgramData\BroadbandDialer\cleanup.log" (
    echo === cleanup.log ===
    type "C:\ProgramData\BroadbandDialer\cleanup.log"
) else (
    echo cleanup.log 不存在
)
echo.

if exist "C:\ProgramData\BroadbandDialer\cleanup_http.log" (
    echo === cleanup_http.log ===
    type "C:\ProgramData\BroadbandDialer\cleanup_http.log"
) else (
    echo cleanup_http.log 不存在（重启后会生成）
)
echo.

echo ============================================================
echo  测试完成！
echo ============================================================
echo.
echo 现在请测试重启功能：
echo 1. 运行主程序，连接宽带
echo 2. 关闭主程序
echo 3. 重启计算机
echo 4. 重新开机后，RunOnce会自动执行清理
echo 5. 运行此脚本查看日志
echo.
echo ⚠️ 重要：重启后cleanup_http.exe会在开机时自动运行！
echo.
pause
