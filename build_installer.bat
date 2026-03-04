@echo off
chcp 65001 >nul
echo ========================================
echo   TP-Link宽带拨号工具 - 构建安装程序
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] 检查必要文件...
if not exist "dist\TP-Link_Dialer.exe" (
    echo [错误] 未找到 dist\TP-Link_Dialer.exe
    echo 请先运行 build_exe.bat 打包 exe 文件
    pause
    exit /b 1
)
echo ✓ 找到 exe 文件

if not exist "TP-Link_Dialer.nsi" (
    echo [错误] 未找到 TP-Link_Dialer.nsi
    pause
    exit /b 1
)
echo ✓ 找到 NSIS 脚本

if not exist "license.txt" (
    echo [错误] 未找到 license.txt
    pause
    exit /b 1
)
echo ✓ 找到许可协议文件

if not exist "app.ico" (
    echo [错误] 未找到 app.ico
    pause
    exit /b 1
)
echo ✓ 找到图标文件
echo.

echo [2/4] 检查 NSIS 安装...
set NSIS_PATH=""
if exist "C:\Program Files (x86)\NSIS\makensis.exe" (
    set "NSIS_PATH=C:\Program Files (x86)\NSIS\makensis.exe"
)
if exist "C:\Program Files\NSIS\makensis.exe" (
    set "NSIS_PATH=C:\Program Files\NSIS\makensis.exe"
)
if "%NSIS_PATH%"=="" (
    echo [错误] 未找到 NSIS，请先安装 NSIS
    echo 下载地址: https://nsis.sourceforge.io/
    pause
    exit /b 1
)
echo ✓ 找到 NSIS: %NSIS_PATH%
echo.

echo [3/4] 创建发布目录...
if not exist "发布包" mkdir "发布包"
echo ✓ 发布包目录已创建
echo.

echo [4/4] 开始构建安装程序...
echo 正在使用 NSIS 编译安装程序...
echo.

"%NSIS_PATH%" TP-Link_Dialer.nsi

if errorlevel 1 (
    echo.
    echo [错误] 安装程序构建失败！
    pause
    exit /b 1
)
echo.

echo ========================================
echo   构建完成！
echo   安装程序位置: 发布包\TP-Link_Dialer_Setup.exe
echo ========================================
echo.
echo 按任意键退出...
pause >nul
