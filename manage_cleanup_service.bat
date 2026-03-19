@echo off
chcp 65001 >nul
echo ========================================
echo TP-Link路由器账号清理服务管理工具
echo ========================================
echo.

if "%1"=="" goto MENU
if /i "%1"=="install" goto INSTALL
if /i "%1"=="remove" goto REMOVE
if /i "%1"=="start" goto START
if /i "%1"=="stop" goto STOP
if /i "%1"=="status" goto STATUS
if /i "%1"=="restart" goto RESTART
goto MENU

:MENU
echo 请选择操作:
echo.
echo 1. 安装服务
echo 2. 卸载服务
echo 3. 启动服务
echo 4. 停止服务
echo 5. 查看服务状态
echo 6. 重启服务
echo 0. 退出
echo.
set /p choice=请输入选项 (0-6):

if "%choice%"=="1" goto INSTALL
if "%choice%"=="2" goto REMOVE
if "%choice%"=="3" goto START
if "%choice%"=="4" goto STOP
if "%choice%"=="5" goto STATUS
if "%choice%"=="6" goto RESTART
if "%choice%"=="0" goto END
echo 无效的选项！
pause
goto MENU

:INSTALL
echo.
echo ========================================
echo 正在安装服务...
echo ========================================
python shutdown_cleanup_service.py install
echo.
pause
goto MENU

:REMOVE
echo.
echo ========================================
echo 正在卸载服务...
echo ========================================
python shutdown_cleanup_service.py remove
echo.
pause
goto MENU

:START
echo.
echo ========================================
echo 正在启动服务...
echo ========================================
python shutdown_cleanup_service.py start
echo.
pause
goto MENU

:STOP
echo.
echo ========================================
echo 正在停止服务...
echo ========================================
python shutdown_cleanup_service.py stop
echo.
pause
goto MENU

:STATUS
echo.
echo ========================================
echo 服务状态
echo ========================================
python shutdown_cleanup_service.py status
echo.
pause
goto MENU

:RESTART
echo.
echo ========================================
echo 正在重启服务...
echo ========================================
python shutdown_cleanup_service.py restart
echo.
pause
goto MENU

:END
echo 再见！
exit /b 0
