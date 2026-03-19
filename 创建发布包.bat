@echo off
chcp 65001 >nul
echo ========================================
echo   创建发布包
echo ========================================
echo.

cd /d "%~dp0"

:: 检查7-Zip是否安装
where 7z >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ 未找到7-Zip
    echo.
    echo 请安装7-Zip: https://www.7-zip.org/
    echo 或手动压缩 Release 目录
    echo.
    pause
    exit /b 1
)

:: 设置版本信息
set VERSION=2.0
set DATE=%date:~0,4%%date:~5,2%%date:~8,2%
set ZIPFILE=Release\宽带拨号工具_v%VERSION%_%DATE%.zip

echo 版本: %VERSION%
echo 日期: %DATE%
echo 输出文件: %ZIPFILE%
echo.

echo 正在创建发布包...
7z a -tzip "%ZIPFILE%" Release\* -mx9 -xr!*.zip -xr!Broadband_Dialer_Setup.exe -xr!宽带拨号工具_Setup.exe

if errorlevel 1 (
    echo.
    echo ❌ 创建发布包失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo   发布包创建完成！
echo ========================================
echo.
echo 📦 输出文件: %ZIPFILE%
dir "%ZIPFILE%" | find "zip"
echo.
echo ✅ 发布包已准备就绪，可以分发给用户
echo.
echo 📝 包含内容:
echo   - TP-Link_Dialer\          主程序
echo   - CleanupService\          清理服务
echo   - ServiceInstaller.exe     服务安装器
echo   - 一键安装.bat             自动安装脚本
echo   - 一键卸载.bat             自动卸载脚本
echo   - 快速使用指南.md          用户文档
echo   - 部署说明.md              部署文档
echo.
echo 按任意键退出...
pause >nul
