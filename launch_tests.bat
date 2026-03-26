@echo off
chcp 65001 >nul
echo ========================================
echo   宽带拨号工具 v2.1 - 测试启动器
echo ========================================
echo.
echo 请选择要执行的测试：
echo.
echo [1] 运行主程序 (测试路由器连接)
echo [2] 运行服务安装器
echo [3] 查看清理服务状态
echo [4] 查看清理服务日志
echo [5] 停止清理服务
echo [6] 启动清理服务
echo [7] 卸载清理服务
echo [8] 运行安装包
echo [9] 重新配置路由器
echo [0] 退出
echo.

set /p choice="请输入选项 (0-9): "

if "%choice%"=="1" goto run_main
if "%choice%"=="2" goto run_installer
if "%choice%"=="3" goto check_service
if "%choice%"=="4" goto view_log
if "%choice%"=="5" goto stop_service
if "%choice%"=="6" goto start_service
if "%choice%"=="7" goto remove_service
if "%choice%"=="8" goto run_setup
if "%choice%"=="9" goto reconfig
if "%choice%"=="0" goto end

echo 无效选项！
pause
goto end

:run_main
echo.
echo 启动主程序...
cd dist\TP-Link_Dialer
start TP-Link_Dialer.exe
goto end

:run_installer
echo.
echo 启动服务安装器...
start dist\ServiceInstaller.exe
goto end

:check_service
echo.
echo 查询清理服务状态...
sc query TPLinkShutdownCleanup
pause
goto end

:view_log
echo.
echo 查看清理服务日志...
if exist "C:\Program Files\TPLinkDialer\logs\cleanup_service.log" (
    type "C:\Program Files\TPLinkDialer\logs\cleanup_service.log"
) else (
    echo 日志文件不存在
)
pause
goto end

:stop_service
echo.
echo 停止清理服务...
cd dist\CleanupService
CleanupService.exe stop
pause
goto end

:start_service
echo.
echo 启动清理服务...
cd dist\CleanupService
CleanupService.exe start
pause
goto end

:remove_service
echo.
echo 卸载清理服务...
cd dist\CleanupService
CleanupService.exe remove
pause
goto end

:run_setup
echo.
echo 启动安装包...
start Release\Setup.exe
goto end

:reconfig
echo.
echo 删除现有配置，下次启动将显示配置向导...
del config.json 2>nul
if exist config.json (
    echo 删除失败，请手动删除 config.json
) else (
    echo 配置已删除，下次启动主程序时会显示配置向导
)
pause
goto end

:end
echo.
echo 按任意键返回主菜单...
pause >nul
cls
goto :eof
