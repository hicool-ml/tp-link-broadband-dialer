@echo off
REM 安装清理服务 - 使用便携版Python
chcp 65001 >nul

echo ============================================================
echo 安装TP-Link路由器账号清理服务
echo ============================================================
echo.

REM 停止并删除旧服务
sc stop TPLinkShutdownCleanup >nul 2>&1
sc delete TPLinkShutdownCleanup >nul 2>&1

REM 使用便携版Python安装服务
cd /d "%~dp0"
set PYTHON_EXE=%~dp0python\python.exe

if not exist "%PYTHON_EXE%" (
    echo 错误：便携版Python未找到！
    pause
    exit /b 1
)

echo 正在安装服务...
"%PYTHON_EXE%" CleanupService.py install

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
