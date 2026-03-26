@echo off
chcp 65001 >nul
echo ========================================
echo   修复 Playwright 浏览器问题
echo ========================================
echo.

cd /d "C:\Program Files (x86)\TPLinkDialer"

echo 检查浏览器目录...
if not exist "chrome-win64" (
    echo 错误：chrome-win64 目录不存在！
    echo 请重新下载并安装最新版本。
    echo.
    echo 下载地址：
    echo https://github.com/hicool-ml/tp-link-broadband-dialer/releases/tag/v2.1
    pause
    exit /b 1
)

echo 找到 chrome-win64 目录
echo.

echo 检查 chrome.exe...
if not exist "chrome-win64\chrome.exe" (
    echo 错误：chrome.exe 不存在！
    pause
    exit /b 1
)

echo 找到 chrome.exe
echo.

echo 浏览器位置：
dir chrome-win64\chrome.exe
echo.

echo ========================================
echo   浏览器文件检查完成
echo ========================================
echo.
echo 如果程序仍然无法找到浏览器，
echo 请尝试以下方法：
echo.
echo 方法 1：重新安装最新版本
echo   https://github.com/hicool-ml/tp-link-broadband-dialer/releases/tag/v2.1
echo.
echo 方法 2：运行主程序，它会自动检测浏览器
echo.
pause
