@echo off
chcp 65001 >nul
echo 正在启动服务管理工具...
python service_installer.py
if errorlevel 1 (
    echo.
    echo 启动失败！请检查Python环境。
    pause
)
