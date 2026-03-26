@echo off
REM 关机清理脚本 - 通过任务计划程序触发
chcp 65001 >nul

set LOG_DIR=%TEMP%\tplink_cleanup
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

set LOG_FILE=%LOG_DIR%\cleanup.log

echo [%DATE% %TIME%] 开始执行关机清理... >> "%LOG_FILE%"

REM 获取脚本所在目录
set SCRIPT_DIR=%~dp0

REM 执行Python清理脚本
"%SCRIPT_DIR%CleanupService.exe" --cleanup 2>&1 >> "%LOG_FILE%"

echo [%DATE% %TIME%] 关机清理完成 >> "%LOG_FILE%"
