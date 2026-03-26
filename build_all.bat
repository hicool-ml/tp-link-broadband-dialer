@echo off
chcp 65001 >nul
echo ========================================
echo    TP-Link 拨号工具 - 完整构建脚本
echo ========================================
echo.

set PYTHON_EXE=python

echo [1/6] 清理旧的构建文件...
if exist "dist" (
    echo 删除 dist 目录...
    rmdir /s /q "dist"
)
if exist "Release\Setup.exe" (
    echo 删除旧的 Setup.exe...
    del "Release\Setup.exe"
)
echo ✅ 清理完成
echo.

echo [2/6] 构建主程序 (TP-Link_Dialer.exe)...
%PYTHON_EXE% -m PyInstaller TP-Link_Dialer.spec --noconfirm
if %ERRORLEVEL% neq 0 (
    echo ❌ 主程序构建失败！
    pause
    exit /b 1
)
echo ✅ 主程序构建完成
echo.

echo [3/6] 构建关机清理服务 (CleanupService.exe)...
%PYTHON_EXE% -m PyInstaller CleanupService.spec --noconfirm
if %ERRORLEVEL% neq 0 (
    echo ❌ 服务构建失败！
    pause
    exit /b 1
)
echo ✅ 服务构建完成
echo.

echo [4/6] 构建服务安装器 (ServiceInstaller.exe)...
%PYTHON_EXE% -m PyInstaller ServiceInstaller.spec --noconfirm
if %ERRORLEVEL% neq 0 (
    echo ❌ 服务安装器构建失败！
    pause
    exit /b 1
)
echo ✅ 服务安装器构建完成
echo.

echo [5/6] 复制文件到发布目录...
echo 创建发布目录...
if not exist "Release" mkdir "Release"

echo 复制主程序...
xcopy /E /I /Y "dist\TP-Link_Dialer\*" "Release\TP-Link_Dialer\"

echo 复制服务程序...
xcopy /E /I /Y "dist\CleanupService\*" "Release\CleanupService\"

echo 复制服务安装器...
copy /Y "dist\ServiceInstaller.exe" "Release\ServiceInstaller.exe"

echo 复制浏览器...
xcopy /E /I /Y "chrome-win64" "Release\chrome-win64\"

echo ✅ 文件复制完成
echo.

echo [6/6] 生成安装包 (Setup.exe)...
echo 编译 NSIS 脚本...
"C:\Program Files (x86)\NSIS\makensis.exe" /V4 "Setup.nsi"
if %ERRORLEVEL% neq 0 (
    echo ❌ 安装包生成失败！
    pause
    exit /b 1
)
echo ✅ 安装包生成完成
echo.

echo ========================================
echo    ✅ 构建完成！
echo ========================================
echo.
echo 输出文件：
echo   - Release\Setup.exe        (完整安装包)
echo   - Release\TP-Link_Dialer\   (主程序)
echo   - Release\CleanupService\  (清理服务)
echo.
echo 安装包大小：
dir "Release\Setup.exe" | find "Setup.exe"
echo.

pause
