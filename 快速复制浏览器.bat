@echo off
chcp 65001 >nul
echo ========================================
echo   复制浏览器文件
echo ========================================
echo.

echo 正在创建目录...
mkdir "C:\Program Files (x86)\TPLinkDialer\chrome-win64" 2>nul

echo 正在复制文件...
xcopy "D:\13jiao\chrome-win64" "C:\Program Files (x86)\TPLinkDialer\chrome-win64\" /S /I /Y /Q

echo.
echo 检查结果...
if exist "C:\Program Files (x86)\TPLinkDialer\chrome-win64\chrome.exe" (
    echo [SUCCESS] 浏览器文件复制成功！
    echo.
    echo 现在可以运行主程序测试登录功能
) else (
    echo [FAIL] 复制失败，请手动复制
)

echo.
pause
