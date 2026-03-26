@echo off
chcp 65001 >nul
title TP-Link Broadband Dialer - 打包发布

echo ========================================
echo TP-Link Broadband Dialer v2.2.0
echo 打包发布程序
echo ========================================
echo.

cd /d %~dp0

set VERSION=2.2.0
set DATE=20260325
set RELEASE_DIR=Release
set ZIP_NAME=TP-Link_Broadband_Dialer_v%VERSION%_%DATE%.zip

echo [1/5] 清理旧文件...
if exist "%ZIP_NAME%" del "%ZIP_NAME%"

echo.
echo [2/5] 检查文件...
if not exist "%RELEASE_DIR%\Broadband_Dialer_Setup_%VERSION%.exe" (
    echo [错误] 找不到安装程序！
    pause
    exit /b 1
)
echo     [OK] 安装程序

if not exist "%RELEASE_DIR%\README.txt" (
    echo [错误] 找不到README文件！
    pause
    exit /b 1
)
echo     [OK] README.txt

if not exist "%RELEASE_DIR%\CHANGELOG.md" (
    echo [错误] 找不到CHANGELOG文件！
    pause
    exit /b 1
)
echo     [OK] CHANGELOG.md

echo.
echo [3/5] 创建版本信息文件...
echo TP-Link Broadband Dialer v%VERSION%> "%RELEASE_DIR%\VERSION.txt"
echo 发布日期: %DATE%>> "%RELEASE_DIR%\VERSION.txt"
echo 版权: Hicool ^& CMCC>> "%RELEASE_DIR%\VERSION.txt"
echo.>> "%RELEASE_DIR%\VERSION.txt"
echo 文件清单:>> "%RELEASE_DIR%\VERSION.txt"
echo   - Broadband_Dialer_Setup_%VERSION%.exe>> "%RELEASE_DIR%\VERSION.txt"
echo   - README.txt>> "%RELEASE_DIR%\VERSION.txt"
echo   - CHANGELOG.md>> "%RELEASE_DIR%\VERSION.txt"
echo   - VERSION.txt>> "%RELEASE_DIR%\VERSION.txt"

echo.
echo [4/5] 打包压缩文件...
powershell -Command "Compress-Archive -Path '%RELEASE_DIR%\*' -DestinationPath '%ZIP_NAME%' -Force"

if errorlevel 1 (
    echo [错误] 打包失败！
    pause
    exit /b 1
)

echo.
echo [5/5] 验证打包...
if exist "%ZIP_NAME%" (
    echo     [OK] 打包成功
    echo.
    echo 文件信息:
    dir "%ZIP_NAME%" | findstr "%ZIP_NAME%"
) else (
    echo [错误] 打包文件未生成！
    pause
    exit /b 1
)

echo.
echo ========================================
echo 打包完成！
echo ========================================
echo.
echo 发布包: %ZIP_NAME%
echo.
echo 包含文件:
echo   - Broadband_Dialer_Setup_%VERSION%.exe (安装程序)
echo   - README.txt (使用说明)
echo   - CHANGELOG.md (更新日志)
echo   - VERSION.txt (版本信息)
echo.
echo 文件大小:
for %%A in ("%ZIP_NAME%") do echo   %%~zA 字节
echo.
echo ========================================
echo.

pause
