@echo off
chcp 65001 >nul
echo ========================================
echo   宽带拨号工具 - 全速打包模式
echo   CPU: Ultra 9 185 - 全核心加速
echo ========================================
echo.

cd /d "%~dp0"

echo 优化设置:
echo   - PyInstaller 单线程
echo   - 并行打包多个组件
echo   - 关闭不必要的优化
echo   - 最大程度利用CPU性能
echo.

echo ========================================
echo   准备并行打包...
echo ========================================
echo.

:: 设置PyInstaller优化级别为0（最快）
set PYINSTALLER_OPT_LEVEL=0

:: 步骤 1: 清理旧的构建文件
echo [1/5] 清理旧构建文件...
if exist "build" rd /s /q "build"
if exist "dist\TP-Link_Dialer" rd /s /q "dist\TP-Link_Dialer"
if exist "dist\CleanupService" rd /s /q "dist\CleanupService"
echo [OK] 清理完成
echo.

:: 步骤 2: 并行打包主程序和清理服务
echo [2/5] 并行打包主程序和清理服务...
echo [后台任务 1] 打包主程序...
start /B "" python -m PyInstaller --clean --noconfirm --optimize 0 TP-Link_Dialer_main_nobrowser.spec > build_main.log 2>&1

echo [后台任务 2] 打包清理服务...
start /B "" python -m PyInstaller --clean --noconfirm --optimize 0 CleanupService_nobrowser.spec > build_service.log 2>&1

echo 等待打包完成...
timeout /t 120 /nobreak >nul

:: 等待后台任务完成
:wait_loop
tasklist | find /i "python.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo 打包进行中...
    timeout /t 5 /nobreak >nul
    goto wait_loop
)
echo [OK] 并行打包完成
echo.

:: 步骤 3: 打包服务安装器
echo [3/5] 打包服务安装器...
if exist "build\ServiceInstaller" rd /s /q "build\ServiceInstaller"
if exist "dist\ServiceInstaller.exe" del "dist\ServiceInstaller.exe"

python -m PyInstaller --clean --noconfirm --optimize 0 ServiceInstaller.spec > build_installer.log 2>&1

if errorlevel 1 (
    echo [ERROR] 服务安装器打包失败
    type build_installer.log
    pause
    exit /b 1
)
echo [OK] 服务安装器打包完成
echo.

:: 步骤 4: 验证打包结果
echo [4/5] 验证打包结果...
if not exist "dist\TP-Link_Dialer\TP-Link_Dialer.exe" (
    echo [ERROR] 主程序打包失败
    type build_main.log
    pause
    exit /b 1
)

if not exist "dist\CleanupService\CleanupService.exe" (
    echo [ERROR] 清理服务打包失败
    type build_service.log
    pause
    exit /b 1
)

echo [OK] 所有组件打包成功
echo.

:: 步骤 5: 创建NSIS安装包
echo [5/5] 创建NSIS安装包...
if not exist "Release" mkdir "Release"

"C:\Program Files (x86)\NSIS\makensis.exe" Setup.nsi

if errorlevel 1 (
    echo [ERROR] NSIS安装包创建失败
    pause
    exit /b 1
)
echo [OK] NSIS安装包创建完成
echo.

:: 显示打包结果
echo ========================================
echo   打包完成！
echo ========================================
echo.

echo 📦 打包结果:
for /f "tokens=3" %%a in ('dir "dist\TP-Link_Dialer" /-c ^| find "bytes" ^| find /v "bytes free"') do set size_main=%%a
for /f "tokens=3" %%a in ('dir "dist\CleanupService" /-c ^| find "bytes" ^| find /v "bytes free"') do set size_service=%%a
for /f "tokens=3" %%a in ('dir "dist\ServiceInstaller.exe" /-c ^| find "bytes" ^| find /v "bytes free"') do set size_installer=%%a

echo   - 主程序: %size_main% bytes
echo   - 清理服务: %size_service% bytes
echo   - 服务安装器: %size_installer% bytes
echo.

for /f "tokens=3" %%a in ('dir "Release\Setup.exe" /-c ^| find "bytes" ^| find /v "bytes free"') do set size_setup=%%a
echo   - 安装包: %size_setup% bytes
echo.

echo 📁 输出位置:
echo   - dist\TP-Link_Dialer\
echo   - dist\CleanupService\
echo   - dist\ServiceInstaller.exe
echo   - Release\Setup.exe
echo.

echo 🎉 全速打包完成！
echo.
pause
