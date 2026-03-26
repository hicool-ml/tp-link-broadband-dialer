@echo off
chcp 65001 >nul
echo ========================================
echo   复制浏览器文件（手动版本）
echo ========================================
echo.

echo 源目录: D:\13jiao\chrome-win64
echo 目标目录: C:\Program Files (x86)\TPLinkDialer\chrome-win64
echo.

echo 请按以下步骤操作：
echo.
echo 1. 创建目标目录：
echo    mkdir "C:\Program Files (x86)\TPLinkDialer\chrome-win64"
echo.
echo 2. 复制文件：
echo    xcopy "D:\13jiao\chrome-win64" "C:\Program Files (x86)\TPLinkDialer\chrome-win64\" /E /I /H /Y
echo.
echo 或者，直接以管理员身份运行此命令：
echo    robocopy "D:\13jiao\chrome-win64" "C:\Program Files (x86)\TPLinkDialer\chrome-win64" /E /R:0 /NFL /NDL /NJH
echo.

pause
