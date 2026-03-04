@echo off
chcp 65001 >nul
echo ========================================
echo 准备精简版浏览器（零依赖打包）
echo ========================================
echo.
echo 🎯 目标：下载并精简 Chromium，减小打包体积
echo 📦 预期体积：100-150MB（精简后）
echo.

cd /d "%~dp0"

:: 检查 Python 是否安装
echo [1/6] 检查 Python 环境...
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

:: 检查 Playwright 是否安装
echo [2/6] 检查 Playwright...
python -c "import playwright; print(f'Playwright 版本: {playwright.__version__}')" 2>nul
if errorlevel 1 (
    echo ❌ 错误: 未安装 Playwright
    echo 正在安装 Playwright...
    pip install playwright==1.45.0
    if errorlevel 1 (
        echo ❌ 安装 Playwright 失败
        pause
        exit /b 1
    )
)
echo ✅ Playwright 已安装
echo.

:: 下载指定版本的 Chromium
echo [3/6] 下载 Chromium 128.x（适配 Win7+，体积最小）...
echo.
echo 📥 正在下载 Chromium，这可能需要几分钟...
echo.
python -m playwright install chromium@128.0.6613.119 --with-deps
if errorlevel 1 (
    echo.
    echo ❌ 下载 Chromium 失败
    echo.
    echo 可能的原因：
    echo 1. 网络连接问题
    echo 2. Playwright 版本不兼容
    echo 3. 防火墙阻止下载
    echo.
    echo 请检查网络连接后重试
    pause
    exit /b 1
)
echo ✅ Chromium 下载完成
echo.

:: 复制 Chromium 到项目目录
echo [4/6] 复制 Chromium 到项目目录...
if exist "chromium-mini" rd /s /q "chromium-mini"

:: 源路径（根据 Playwright 版本可能不同）
set "SOURCE_PATH=%LOCALAPPDATA%\ms-playwright\chromium-1280\chrome-win64"
if not exist "%SOURCE_PATH%" (
    echo ❌ 错误: 未找到 Chromium 目录
    echo 预期路径: %SOURCE_PATH%
    echo.
    echo 请检查 Playwright 是否正确安装
    pause
    exit /b 1
)

echo 正在复制: %SOURCE_PATH%
echo 目标目录: chromium-mini
echo.
xcopy "%SOURCE_PATH%" "chromium-mini" /E /I /H /Y
if errorlevel 1 (
    echo ❌ 复制失败
    pause
    exit /b 1
)
echo ✅ 复制完成
echo.

:: 精简浏览器（删除不必要的文件）
echo [5/6] 精简浏览器（减小体积）...
echo.
echo 🗑️ 正在删除不必要的文件...
echo.

:: 删除语言包（仅保留中文）
if exist "chromium-mini\locales" (
    echo   - 删除语言包（保留 zh-CN.pak）...
    cd chromium-mini\locales
    for %%f in (*.pak) do (
        if /i not "%%f"=="zh-CN.pak" (
            del /f /q "%%f" 2>nul
        )
    )
    cd ..\..
)

:: 删除扩展程序
if exist "chromium-mini\resources\extensions" (
    echo   - 删除扩展程序...
    rd /s /q "chromium-mini\resources\extensions" 2>nul
)

:: 删除调试工具
if exist "chromium-mini\chrome_debugger.exe" (
    echo   - 删除调试工具...
    del /f /q "chromium-mini\chrome_debugger.exe" 2>nul
)
if exist "chromium-mini\chromedriver.exe" (
    del /f /q "chromium-mini\chromedriver.exe" 2>nul
)

:: 删除其他不必要的文件
if exist "chromium-mini\chrome.exe" (
    echo   - 保留核心文件...
)
echo.
echo ✅ 精简完成
echo.

:: 显示精简结果
echo [6/6] 精简结果
echo ========================================
echo.
echo 📊 精简前后对比：
echo.
echo 精简前：
dir "%SOURCE_PATH%" | find "chrome-win64"
echo.
echo 精简后：
dir "chromium-mini" | find "chromium-mini"
echo.
echo 📦 精简版浏览器已准备完成！
echo.
echo ✨ 下一步：
echo   1. 运行 build_exe.bat 打包 EXE
echo   2. 打包后的 EXE 将包含精简版浏览器
echo   3. 预期体积：100-150MB
echo.
echo 按任意键退出...
pause >nul
