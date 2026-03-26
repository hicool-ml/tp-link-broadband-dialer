@echo off
chcp 65001 >nul
echo ========================================
echo   重启后自动安装清理服务
echo ========================================
echo.

cd /d "C:\Program Files (x86)\TPLinkDialer"

echo [1/3] 安装服务...
CleanupService.exe install
echo.

echo [2/3] 启动服务...
sc start TPLinkShutdownCleanup
echo.

echo [3/3] 等待 5 秒后检查状态...
timeout /t 5 /nobreak >nul

sc query TPLinkShutdownCleanup
echo.

if exist "%TEMP%\tplink_cleanup\cleanup_service.log" (
    echo --- 服务日志 ---
    type "%TEMP%\tplink_cleanup\cleanup_service.log"
) else (
    echo 日志文件尚未创建
)
echo.

echo ========================================
echo   安装完成！
echo ========================================
echo.
echo 请检查上面的服务状态。
echo 如果显示 STATE: 4 RUNNING，说明服务已成功启动。
echo.
pause
