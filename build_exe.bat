@echo off
chcp 65001 >nul
echo ========================================
echo 宽带拨号工具 - 零依赖版本打包脚本
echo ========================================
echo.
echo 🎯 目标：创建完全不依赖用户环境的独立 EXE
echo 📦 预期体积：100-150MB（精简版浏览器）
echo 🌐 适配环境：Win7/10/11、32/64位、高低权限
echo.

cd /d "%~dp0"

:: 检查 Python 是否安装
echo [1/5] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Python
    echo 请先安装 Python 3.8 或更高版本
    pause
    exit /b 1
)
python --version
echo ✅ Python 环境检查通过
echo.

:: 检查浏览器目录是否存在
echo [2/5] 检查浏览器文件...
if not exist "chromium-mini\chrome.exe" (
    if not exist "ms-playwright\chromium-1208\chrome-win64\chrome.exe" (
        echo ❌ 错误: 未找到浏览器文件！
        echo.
        echo 请先执行以下步骤之一：
        echo.
        echo 方案1：使用精简版浏览器（推荐，体积最小）
        echo   1. 下载 Chromium 128.x: playwright install chromium@128.0.6613.119 --only-shell --with-deps
        echo   2. 复制到项目: xcopy "%LOCALAPPDATA%\ms-playwright\chromium-1280\chrome-win64" "chromium-mini" /E /I /Y
        echo   3. 裁剪浏览器: 删除 chromium-mini\locales、chromium-mini\resources\extensions 等
        echo.
        echo 方案2：使用完整版浏览器（体积较大）
        echo   1. 下载 Chromium: playwright install chromium --with-deps
        echo   2. 复制到项目: xcopy "%LOCALAPPDATA%\ms-playwright" "ms-playwright" /E /I /Y
        echo.
        pause
        exit /b 1
    )
    echo ✅ 找到完整版浏览器: ms-playwright\chromium-1208\chrome-win64\chrome.exe
) else (
    echo ✅ 找到精简版浏览器: chromium-mini\chrome.exe
)
echo.

:: 清理旧的构建文件（避免缓存导致依赖遗漏）
echo [3/5] 清理旧的构建文件...
if exist "dist" rd /s /q "dist"
if exist "build" rd /s /q "build"
if exist "TP-Link_Dialer.spec" del /f /q "TP-Link_Dialer.spec"
echo ✅ 清理完成
echo.

:: 核心打包命令（零依赖配置）
echo [4/5] 使用 PyInstaller 打包 EXE...
echo.

:: 根据浏览器类型选择打包参数
if exist "chromium-mini\chrome.exe" (
    echo 📦 使用精简版浏览器打包...
    set "BROWSER_DATA=chromium-mini;chromium-mini"
) else (
    echo 📦 使用完整版浏览器打包...
    set "BROWSER_DATA=ms-playwright;ms-playwright"
)

python -m PyInstaller ^
  --onefile ^
  --windowed ^
  --name "TP-Link_Dialer" ^
  --icon "app.ico" ^
  --add-data "%BROWSER_DATA%" ^
  --add-data "app.ico;." ^
  --add-data "connecting.ico;." ^
  --add-data "error.ico;." ^
  --add-data "offline.ico;." ^
  --add-data "online.ico;." ^
  --hidden-import=playwright.sync_api ^
  --hidden-import=playwright._impl._api_types ^
  --hidden-import=playwright._impl._browser ^
  --hidden-import=playwright._impl._connection ^
  --hidden-import=tkinter ^
  --hidden-import=queue ^
  --hidden-import=threading ^
  --hidden-import=ctypes ^
  --hidden-import=re ^
  --hidden-import=time ^
  --hidden-import=subprocess ^
  --hidden-import=atexit ^
  --hidden-import=tempfile ^
  --collect-all playwright ^
  --exclude-module=unittest ^
  --exclude-module=setuptools ^
  --exclude-module=pip ^
  --exclude-module=email ^
  --exclude-module=pydoc ^
  --exclude-module=doctest ^
  --clean ^
  --noupx ^
  --noconfirm ^
  tp_link_broadband_dialer.py

if errorlevel 1 (
    echo.
    echo ❌ 打包失败！
    echo.
    echo 可能的原因：
    echo 1. Python 依赖包未安装
    echo 2. 浏览器文件路径错误
    echo 3. PyInstaller 版本不兼容
    echo.
    echo 请检查错误信息并重试
    pause
    exit /b 1
)
echo.

:: 显示打包结果
echo [5/5] 打包完成！
echo ========================================
echo ✅ 零依赖版本打包成功！
echo ========================================
echo.
echo 📦 输出文件: dist\TP-Link_Dialer.exe
echo.
echo 📊 文件信息:
for %%I in ("dist\TP-Link_Dialer.exe") do (
    set /a SIZE_MB=%%~zI/1024/1024
    echo   - 文件大小: !SIZE_MB! MB
)
echo.
echo ✨ 特性:
echo   - ✅ 完全独立运行，无需安装 Python
echo   - ✅ 内置浏览器，无需安装 Chrome
echo   - ✅ 适配 Win7/10/11、32/64位
echo   - ✅ 支持低权限用户运行
echo   - ✅ 禁用 UPX 压缩，避免杀毒软件误报
echo   - ✅ 自定义临时目录，避免权限问题
echo.
echo 🧪 验证步骤：
echo   1. 在纯净 Windows 机器上测试（无 Python、无 Chrome）
echo   2. 以低权限用户运行测试
echo   3. 断网测试（确保不下载依赖）
echo   4. 检查文件大小是否在预期范围
echo.
echo 按任意键退出...
pause >nul
