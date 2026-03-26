@echo off
chcp 65001 >nul
echo ========================================
echo   测试新版本主程序
echo ========================================
echo.

echo 此脚本将启动新构建的主程序进行测试
echo.

cd dist\TP-Link_Dialer

if exist TP-Link_Dialer.exe (
    echo 启动主程序...
    echo.
    echo 文件位置: %CD%\TP-Link_Dialer.exe
    echo 文件大小:
    dir TP-Link_Dialer.exe | find "TP-Link_Dialer.exe"
    echo.
    echo ========================================
    echo.

    start TP-Link_Dialer.exe

    echo 程序已启动
    echo.
    echo 测试建议:
    echo 1. 检查是否显示配置向导（首次运行）
    echo 2. 配置路由器IP和密码
    echo 3. 测试宽带连接
    echo 4. 测试断开和清除功能
    echo.
) else (
    echo 错误: 找不到 TP-Link_Dialer.exe
    echo 请先执行构建
)

pause
