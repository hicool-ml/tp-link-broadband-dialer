@echo off
chcp 65001 >nul
echo ========================================
echo   测试 HTTP 清理服务
echo ========================================
echo.

cd /d "D:\13jiao\dist_http"

echo [1/3] 卸载旧服务...
CleanupServiceHTTP.exe remove 2>nul
echo.

echo [2/3] 安装服务...
CleanupServiceHTTP.exe install
echo.

echo [3/3] 启动服务...
sc start TPLinkCleanupService
echo.

echo 等待 3 秒...
timeout /t 3 /nobreak >nul

echo 检查状态...
sc query TPLinkCleanupService
echo.

echo 查看日志...
if exist "%TEMP%\tplink_cleanup.log" (
    echo --- 日志内容 ---
    type "%TEMP%\tplink_cleanup.log"
) else (
    echo 日志文件不存在
)
echo.

pause
