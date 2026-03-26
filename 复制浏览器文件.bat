@echo off
chcp 65001 >nul
echo ========================================
echo   复制浏览器文件到安装目录
echo ========================================
echo.

echo 源目录: D:\13jiao\chrome-win64
echo 目标目录: C:\Program Files (x86)\TPLinkDialer\chrome-win64
echo.

echo 正在复制浏览器文件...
xcopy "D:\13jiao\chrome-win64" "C:\Program Files (x86)\TPLinkDialer\chrome-win64\" /E /I /H /Y /R

if errorlevel 1 (
    echo.
    echo 复制失败！可能需要管理员权限。
    echo.
    echo 请以管理员身份运行此批处理文件：
    echo 右键点击 -^> 以管理员身份运行
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   复制完成！
echo ========================================
echo.

echo 验证浏览器文件...
if exist "C:\Program Files (x86)\TPLinkDialer\chrome-win64\chrome.exe" (
    echo [OK] chrome.exe 存在
) else (
    echo [FAIL] chrome.exe 不存在
)

echo.
echo 现在可以启动宽带拨号程序了！
echo.
pause
