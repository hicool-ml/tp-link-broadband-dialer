@echo off
chcp 65001 >nul
echo ========================================
echo   TP-Link宽带拨号工具 - 一键打包脚本
echo ========================================
echo.

cd /d "%~dp0"

echo 此脚本将按顺序执行以下操作：
echo   1. 打包 exe 文件
echo   2. 构建安装程序
echo.
echo 按任意键继续，或关闭窗口取消...
pause >nul

echo.
echo ========================================
echo   开始打包流程...
echo ========================================
echo.

echo [步骤 1/2] 打包 exe 文件...
echo.
call build_exe.bat

if errorlevel 1 (
    echo.
    echo [错误] exe 打包失败，终止流程
    pause
    exit /b 1
)

echo.
echo [步骤 2/2] 构建安装程序...
echo.
call build_installer.bat

if errorlevel 1 (
    echo.
    echo [错误] 安装程序构建失败，但 exe 文件已生成
    pause
    exit /b 1
)

echo.
echo ========================================
echo   全部完成！
echo ========================================
echo.
echo   exe 文件: dist\TP-Link_Dialer.exe
echo   安装程序: 发布包\TP-Link_Dialer_Setup.exe
echo.
echo 按任意键退出...
pause >nul
