@echo off
REM 切换到脚本所在目录
cd /d "%~dp0"

chcp 65001 >nul
title TP-Link宽带拨号工具 - 打包脚本
echo ========================================
echo TP-Link宽带拨号工具 - 自动打包
echo ========================================
echo.
echo 方案：Playwright + Chromium（固定版本）
echo 优点：跨环境一致，无需依赖系统浏览器
echo.
echo 当前工作目录: %CD%
echo.

REM 检查Python
py -3.11 --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python 3.11
    pause
    exit /b 1
)

echo [1/5] 安装打包工具...
py -3.11 -m pip install pyinstaller >nul 2>&1

echo [2/5] 安装项目依赖...
py -3.11 -m pip install playwright pystray pillow >nul 2>&1

echo [2.5/5] 生成状态图标...
py -3.11 generate_icons.py >nul 2>&1

echo [3/5] 安装Playwright浏览器...
py -3.11 -m playwright install chromium >nul 2>&1

echo [4/5] 清理旧文件...
if exist build rmdir /s /q build 2>nul
if exist dist rmdir /s /q dist 2>nul
if exist *.spec del /q *.spec 2>nul

echo [5/5] 开始打包...
echo.

REM 获取 Playwright 浏览器路径
for /f "delims=" %%i in ('py -3.11 -c "import os; from pathlib import Path; playwright_path = Path(os.path.expanduser('~')) / 'AppData' / 'Local' / 'ms-playwright'; chromium_dirs = list(playwright_path.glob('chromium-*')); print(max(chromium_dirs, key=os.path.getmtime))" 2^>nul') do set CHROMIUM_PATH=%%i

if not defined CHROMIUM_PATH (
    echo [警告] 未找到 Playwright 浏览器，尝试重新安装...
    py -3.11 -m playwright install chromium
    for /f "delims=" %%i in ('py -3.11 -c "import os; from pathlib import Path; playwright_path = Path(os.path.expanduser('~')) / 'AppData' / 'Local' / 'ms-playwright'; chromium_dirs = list(playwright_path.glob('chromium-*')); print(max(chromium_dirs, key=os.path.getmtime))" 2^>nul') do set CHROMIUM_PATH=%%i
)

echo 检测到 Playwright 浏览器路径: %CHROMIUM_PATH%
echo.

REM 询问用户是否使用控制台模式（用于调试）
set USE_CONSOLE=N
set /p USE_CONSOLE="是否使用控制台模式（用于调试）？[Y/N]: "
if /i "%USE_CONSOLE%"=="Y" (
    echo 使用控制台模式...
    py -3.11 -m PyInstaller ^
      --onedir ^
      --console ^
      --name "TP-Link_Dialer" ^
      --hidden-import playwright ^
      --hidden-import playwright.sync_api ^
      --hidden-import playwright.async_api ^
      --hidden-import playwright.sync_api._context_manager ^
      --hidden-import playwright.sync_api._generated ^
      --hidden-import pystray ^
      --hidden-import PIL ^
      --hidden-import PIL.Image ^
      --hidden-import PIL.ImageDraw ^
      --hidden-import queue ^
      --hidden-import threading ^
      --hidden-import re ^
      --hidden-import tkinter ^
      --hidden-import ctypes ^
      --hidden-import atexit ^
      --hidden-import subprocess ^
      --hidden-import greenlet ^
      --hidden-import pyee ^
      --collect-all playwright ^
      --collect-data playwright ^
      --collect-binaries playwright ^
      --add-data "%CHROMIUM_PATH%\chrome-win64;ms-playwright\chromium-1208\chrome-win64" ^
      --add-data "app.ico;." ^
      --add-data "online.ico;." ^
      --add-data "offline.ico;." ^
      --add-data "connecting.ico;." ^
      --add-data "error.ico;." ^
      --icon "app.ico" ^
      tp_link_broadband_dialer.py
) else (
    echo 使用窗口模式（无控制台）...
    py -3.11 -m PyInstaller ^
      --onedir ^
      --windowed ^
      --name "TP-Link_Dialer" ^
      --hidden-import playwright ^
      --hidden-import playwright.sync_api ^
      --hidden-import playwright.async_api ^
      --hidden-import playwright.sync_api._context_manager ^
      --hidden-import playwright.sync_api._generated ^
      --hidden-import pystray ^
      --hidden-import PIL ^
      --hidden-import PIL.Image ^
      --hidden-import PIL.ImageDraw ^
      --hidden-import queue ^
      --hidden-import threading ^
      --hidden-import re ^
      --hidden-import tkinter ^
      --hidden-import ctypes ^
      --hidden-import atexit ^
      --hidden-import subprocess ^
      --hidden-import greenlet ^
      --hidden-import pyee ^
      --collect-all playwright ^
      --collect-data playwright ^
      --collect-binaries playwright ^
      --add-data "%CHROMIUM_PATH%\chrome-win64;ms-playwright\chromium-1208\chrome-win64" ^
      --add-data "app.ico;." ^
      --add-data "online.ico;." ^
      --add-data "offline.ico;." ^
      --add-data "connecting.ico;." ^
      --add-data "error.ico;." ^
      --icon "app.ico" ^
      tp_link_broadband_dialer.py
)

if errorlevel 1 (
    echo.
    echo [错误] 打包失败！
    pause
    exit /b 1
)

echo.
echo ========================================
echo 打包成功！
echo ========================================
echo.
echo 生成的文件夹：dist\TP-Link_Dialer\
echo 主程序：dist\TP-Link_Dialer\TP-Link_Dialer.exe
echo 文件大小：约 150-250 MB（包含浏览器）
echo.

REM 创建部署包
if not exist "发布包" mkdir "发布包"
if exist "发布包\TP-Link_Dialer" rmdir /s /q "发布包\TP-Link_Dialer" 2>nul
xcopy /E /I /Y "dist\TP-Link_Dialer" "发布包\TP-Link_Dialer" >nul

REM 创建使用说明
echo TP-Link Broadband Dialer Tool - User Guide > "发布包\使用说明.txt"
echo. >> "发布包\使用说明.txt"
echo ======================================== >> "发布包\使用说明.txt"
echo Quick Start >> "发布包\使用说明.txt"
echo ======================================== >> "发布包\使用说明.txt"
echo. >> "发布包\使用说明.txt"
echo 1. Go to folder: TP-Link_Dialer >> "发布包\使用说明.txt"
echo 2. Double click: TP-Link_Dialer.exe >> "发布包\使用说明.txt"
echo 3. Enter broadband account and password >> "发布包\使用说明.txt"
echo 4. Click Start Connection >> "发布包\使用说明.txt"
echo 5. Auto hide to tray after success >> "发布包\使用说明.txt"
echo. >> "发布包\使用说明.txt"
echo ======================================== >> "发布包\使用说明.txt"
echo Important Notes >> "发布包\使用说明.txt"
echo ======================================== >> "发布包\使用说明.txt"
echo. >> "发布包\使用说明.txt"
echo Using Playwright plus Chromium >> "发布包\使用说明.txt"
echo Fixed version, cross-platform consistency >> "发布包\使用说明.txt"
echo All required browser files included >> "发布包\使用说明.txt"
echo No need to install Python or browser >> "发布包\使用说明.txt"
echo Works on any Windows 10/11 machine >> "发布包\使用说明.txt"
echo. >> "发布包\使用说明.txt"
echo Exit via tray icon >> "发布包\使用说明.txt"
echo Closing window will not disconnect >> "发布包\使用说明.txt"
echo Do not delete or move any files in folder >> "发布包\使用说明.txt"
echo. >> "发布包\使用说明.txt"
echo ======================================== >> "发布包\使用说明.txt"
echo Tray Menu >> "发布包\使用说明.txt"
echo ======================================== >> "发布包\使用说明.txt"
echo. >> "发布包\使用说明.txt"
echo - Show Window: Show main window >> "发布包\使用说明.txt"
echo - Disconnect: Disconnect and clear credentials >> "发布包\使用说明.txt"
echo - Exit: Safe exit (recommended) >> "发布包\使用说明.txt"
echo. >> "发布包\使用说明.txt"

echo 部署包已创建：发布包\
echo.
echo ========================================
echo 部署说明
echo ========================================
echo.
echo 1. 将发布包\TP-Link宽带拨号文件夹复制到目标机器
echo 2. 双击运行 TP-Link宽带拨号.exe
echo 3. 首次运行可能需要5-10秒启动
echo.
echo 注意：无需安装任何依赖
echo       请保持文件夹完整性，不要删除任何文件
echo.
pause
