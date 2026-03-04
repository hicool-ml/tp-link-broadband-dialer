@echo off
chcp 65001 >nul
echo ========================================
echo   TP-Link宽带拨号工具 - 打包脚本
echo ========================================
echo.

cd /d "%~dp0"

echo [1/5] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.11+
    pause
    exit /b 1
)
python --version
echo.

echo [2/5] 安装/更新依赖包...
echo 正在安装 PyInstaller...
pip install pyinstaller playwright pystray pillow -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo [错误] 依赖包安装失败
    pause
    exit /b 1
)
echo.
echo 正在安装 Playwright 浏览器...
python -m playwright install chromium --with-deps
if errorlevel 1 (
    echo [警告] Playwright 浏览器安装失败，程序可能无法正常运行
)
echo.

echo [3/5] 清理旧的构建文件...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "TP-Link_Dialer.spec" del /q "TP-Link_Dialer.spec"
echo.

echo [4/5] 开始打包 exe 文件...
echo 正在使用 PyInstaller 打包...
echo.

pyinstaller --onefile ^
    --windowed ^
    --name="TP-Link_Dialer" ^
    --icon=app.ico ^
    --add-data="app.ico;." ^
    --add-data="connecting.ico;." ^
    --add-data="error.ico;." ^
    --add-data="offline.ico;." ^
    --add-data="online.ico;." ^
    --hidden-import=tkinter ^
    --hidden-import=queue ^
    --hidden-import=threading ^
    --hidden-import=ctypes ^
    --hidden-import=re ^
    --hidden-import=time ^
    --hidden-import=subprocess ^
    --hidden-import=atexit ^
    --hidden-import=tempfile ^
    --collect-all=submodules ^
    --noconfirm ^
    tp_link_broadband_dialer.py

if errorlevel 1 (
    echo.
    echo [错误] 打包失败！
    pause
    exit /b 1
)
echo.

echo [5/5] 打包完成！
echo ========================================
echo   exe 文件位置: dist\TP-Link_Dialer.exe
echo ========================================
echo.
echo 按任意键退出...
pause >nul
