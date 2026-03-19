@echo off
chcp 65001 >nul
echo ========================================
echo   创建最终发布包
echo ========================================
echo.

cd /d "%~dp0"

:: 检查7-Zip
where 7z >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ 未找到7-Zip，尝试使用PowerShell压缩...
    goto :USE_POWERSHELL
)

set VERSION=2.0
set DATE=%date:~0,4%%date:~5,2%%date:~8,2%
set ZIPFILE=Release\宽带拨号工具_v%VERSION%_%DATE%.zip

echo 使用7-Zip创建发布包...
echo 版本: %VERSION%
echo 日期: %DATE%
echo 输出: %ZIPFILE%
echo.

echo 正在压缩文件（可能需要几分钟）...
7z a -tzip "%ZIPFILE%" "Release\TP-Link_Dialer" "Release\CleanupService" "Release\ServiceInstaller.exe" "Release\一键安装.bat" "Release\一键卸载.bat" "Release\快速使用指南.md" "Release\部署说明.md" "Release\README.md" -mx9 -y

if errorlevel 1 (
    echo ❌ 压缩失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo   发布包创建完成！
echo ========================================
echo.
echo 📦 输出文件: %ZIPFILE%
for %%F in ("%ZIPFILE%") do echo   文件大小: %%~zF 字节
echo.
echo ✅ 分发说明:
echo   1. 将 %ZIPFILE% 发送给用户
echo   2. 用户解压到任意目录
echo   3. 以管理员身份运行"一键安装.bat"
echo   4. 从桌面快捷方式启动程序
echo.
echo 按任意键退出...
pause >nul
exit /b 0

:USE_POWERSHELL
echo 使用PowerShell创建发布包...
powershell -Command "Compress-Archive -Path 'Release\TP-Link_Dialer','Release\CleanupService','Release\ServiceInstaller.exe','Release\一键安装.bat','Release\一键卸载.bat','Release\快速使用指南.md','Release\部署说明.md','Release\README.md' -DestinationPath 'Release\宽带拨号工具_v%VERSION%_%DATE%.zip' -Force"

if errorlevel 1 (
    echo ❌ 压缩失败
    pause
    exit /b 1
)

echo.
echo ✅ 发布包创建完成！
pause
