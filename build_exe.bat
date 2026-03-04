@echo off
chcp 65001 >nul
echo ========================================
echo   TP-Link宽带拨号工具 - 打包脚本
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.11+
    pause
    exit /b 1
)
python --version
echo.

echo [2/4] 清理旧的构建文件...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "TP-Link_Dialer.spec" del /q "TP-Link_Dialer.spec"
echo.

echo [3/4] 开始打包 exe 文件...
echo 正在使用 PyInstaller 打包...
echo.

python -m PyInstaller --onefile ^
    --windowed ^
    --name="TP-Link_Dialer" ^
    --icon=app.ico ^
    --add-data="app.ico;." ^
    --add-data="connecting.ico;." ^
    --add-data="error.ico;." ^
    --add-data="offline.ico;." ^
    --add-data="online.ico;." ^
    --add-data="ms-playwright;ms-playwright" ^
    --hidden-import=tkinter ^
    --hidden-import=queue ^
    --hidden-import=threading ^
    --hidden-import=ctypes ^
    --hidden-import=re ^
    --hidden-import=time ^
    --hidden-import=subprocess ^
    --hidden-import=atexit ^
    --hidden-import=tempfile ^
    --hidden-import=playwright ^
    --hidden-import=playwright.sync_api ^
    --collect-all playwright ^
    --collect-all submodules ^
    --noconfirm ^
    tp_link_broadband_dialer.py

if errorlevel 1 (
    echo.
    echo [错误] 打包失败！
    pause
    exit /b 1
)
echo.

echo [4/4] 打包完成！
echo ========================================
echo   exe 文件位置: dist\TP-Link_Dialer.exe
echo ========================================
echo.
echo 按任意键退出...
pause >nul
