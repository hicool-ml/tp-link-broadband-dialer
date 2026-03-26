@echo off
chcp 65001 >nul
title 安装关机清理任务

echo ========================================
echo 安装TP-Link路由器关机清理任务
echo ========================================
echo.

cd /d %~dp0

set SCRIPT_DIR=%~dp0
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%
set PS_SCRIPT=%SCRIPT_DIR%\cleanup_shutdown.ps1

echo [1/4] 检查PowerShell脚本...
if not exist "%PS_SCRIPT%" (
    echo [错误] 找不到脚本: %PS_SCRIPT%
    pause
    exit /b 1
)
echo     脚本: %PS_SCRIPT%

echo.
echo [2/4] 删除旧任务...
schtasks /Delete /TN "TPLinkCleanup" /F 2>nul

echo.
echo [3/4] 创建关机触发任务...
schtasks /Create ^
    /TN "TPLinkCleanup" ^
    /TR "powershell.exe -ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File \"%PS_SCRIPT%\"" ^
    /SC ONEVENT ^
    /EC System ^
    /MO "*[System[(EventID=1074 or EventID=6006)]]" ^
    /RU SYSTEM ^
    /RL HIGHEST ^
    /F

if errorlevel 1 (
    echo [错误] 任务创建失败！
    echo.
    echo 可能原因：
    echo   - 需要管理员权限
    echo   - PowerShell脚本路径有问题
    pause
    exit /b 1
)

echo.
echo [4/4] 验证任务...
schtasks /Query /TN "TPLinkCleanup" /FO LIST

echo.
echo ========================================
echo 安装成功！
echo ========================================
echo.
echo 任务名称: TPLinkCleanup
echo 触发条件: 系统关机/重启事件
echo 运行权限: SYSTEM（最高权限）
echo.
echo 管理命令:
echo   查看任务: schtasks /Query /TN TPLinkCleanup
echo   运行任务: schtasks /Run /TN TPLinkCleanup
echo   删除任务: schtasks /Delete /TN TPLinkCleanup /F
echo.
echo 测试命令（立即执行一次）:
echo   schtasks /Run /TN TPLinkCleanup
echo.
echo 日志位置: %TEMP%\tplink_cleanup\cleanup.log
echo.

pause
