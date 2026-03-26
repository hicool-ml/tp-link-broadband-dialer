@echo off
chcp 65001 >nul
echo ============================================================
echo 安装TP-Link路由器账号清理服务
echo ============================================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo 错误：未找到Python！
    echo 请先安装Python 3.11或更高版本
    pause
    exit /b 1
)

echo Python版本：
python --version
echo.

REM 停止并删除旧服务（如果存在）
sc stop TPLinkShutdownCleanup >nul 2>&1
sc delete TPLinkShutdownCleanup >nul 2>&1

REM 安装服务
echo 正在安装服务...
cd /d "%~dp0"
python shutdown_cleanup_service_final.py install

if %ERRORLEVEL% equ 0 (
    echo.
    echo ============================================================
    echo 服务安装成功！
    echo ============================================================
    echo.
    echo 启动服务...
    sc start TPLinkShutdownCleanup

    timeout /t 3 >nul

    echo.
    echo 服务状态：
    sc query TPLinkShutdownCleanup

    echo.
    echo ============================================================
    echo 安装完成！
    echo.
    echo 服务日志位置：%%TEMP%%\tplink_cleanup\cleanup_service.log
    echo ============================================================
) else (
    echo.
    echo ============================================================
    echo 服务安装失败！
    echo ============================================================
)

pause
