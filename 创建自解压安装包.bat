@echo off
chcp 65001 >nul
echo ========================================
echo   创建自解压安装包
echo ========================================
echo.

cd /d "%~dp0"

:: 检查7-Zip
where 7z >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ 未找到7-Zip
    echo 请安装7-Zip: https://www.7-zip.org/
    pause
    exit /b 1
)

set VERSION=2.0
set DATE=%date:~0,4%%date:~5,2%%date:~8,2%
set SFXNAME=Release\宽带拨号工具_v%VERSION%_安装.exe

echo 版本: %VERSION%
echo 日期: %DATE%
echo 输出: %SFXNAME%
echo.

echo 步骤1: 准备安装文件...
if not exist "Release\install_temp" mkdir "Release\install_temp"
copy /y "Release\一键安装.bat" "Release\install_temp\安装.bat" >nul
copy /y "Release\快速使用指南.md" "Release\install_temp\" >nul

echo 步骤2: 打包主程序和服务...
7z a -tzip "Release\package_temp.zip" "Release\install_temp\*" "Release\TP-Link_Dialer\*" "Release\CleanupService\*" "Release\ServiceInstaller.exe" -mx5 >nul

echo 步骤3: 创建自解压安装包...
copy /b "7z.sfx" + "config.txt" + "Release\package_temp.zip" "%SFXNAME%" 2>nul

:: 清理临时文件
del "Release\package_temp.zip" 2>nul
rd /s /q "Release\install_temp" 2>nul

if exist "%SFXNAME%" (
    echo.
    echo ========================================
    echo   自解压安装包创建成功！
    echo ========================================
    echo.
    echo 📦 输出文件: %SFXNAME%
    dir "%SFXNAME%" | find ".exe"
    echo.
    echo ✅ 用户双击即可自动安装
    echo.
) else (
    echo.
    echo ❌ 创建失败
    echo.
    echo 请尝试手动压缩 Release 文件夹
)

pause
