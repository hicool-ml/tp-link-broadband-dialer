@echo off
chcp 65001 >nul
title TP-Link宽带拨号助手 - 安装验证

echo ========================================
echo TP-Link宽带拨号助手 v2.2.0
echo 安装验证工具
echo ========================================
echo.

set ERRORS=0

echo [1/6] 检查程序文件...
if exist "C:\Program Files\Broadband_Dialer\broadband_dialer.exe" (
    echo     [OK] broadband_dialer.exe
) else (
    echo     [ERROR] broadband_dialer.exe 未找到
    set /a ERRORS+=1
)

if exist "C:\Program Files\Broadband_Dialer\cleanup_http.exe" (
    echo     [OK] cleanup_http.exe
) else (
    echo     [ERROR] cleanup_http.exe 未找到
    set /a ERRORS+=1
)

if exist "C:\Program Files\Broadband_Dialer\cleanup.ps1" (
    echo     [OK] cleanup.ps1
) else (
    echo     [ERROR] cleanup.ps1 未找到
    set /a ERRORS+=1
)

echo.
echo [2/6] 检查快捷方式...
if exist "%PUBLIC%\Desktop\宽带拨号助手.lnk" (
    echo     [OK] 桌面快捷方式
) else (
    echo     [WARN] 桌面快捷方式未找到
)

if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Broadband_Dialer\宽带拨号助手.lnk" (
    echo     [OK] 开始菜单快捷方式
) else (
    echo     [WARN] 开始菜单快捷方式未找到
)

echo.
echo [3/6] 检查任务计划...
schtasks /Query /TN "TPLinkCleanup" >nul 2>&1
if errorlevel 1 (
    echo     [ERROR] 任务计划 TPLinkCleanup 未找到
    set /a ERRORS+=1
) else (
    echo     [OK] 任务计划 TPLinkCleanup 已创建
    schtasks /Query /TN "TPLinkCleanup" /FO LIST | findstr "任务名\|触发器\|系统"
)

echo.
echo [4/6] 检查注册表...
reg query "HKLM\Software\Broadband_Dialer" >nul 2>&1
if errorlevel 1 (
    echo     [WARN] 注册表项未找到
) else (
    echo     [OK] 注册表项已创建
)

reg query "HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\TP-Link宽带拨号助手" >nul 2>&1
if errorlevel 1 (
    echo     [WARN] 卸载信息未找到
) else (
    echo     [OK] 卸载信息已注册
)

echo.
echo [5/6] 检查日志目录...
if exist "C:\ProgramData\BroadbandDialer" (
    echo     [OK] 日志目录已创建
) else (
    echo     [WARN] 日志目录未找到（首次运行时创建）
)

echo.
echo [6/6] 测试任务计划...
echo     正在手动触发任务...
schtasks /Run /TN "TPLinkCleanup" >nul 2>&1
if errorlevel 1 (
    echo     [ERROR] 任务触发失败
    set /a ERRORS+=1
) else (
    echo     [OK] 任务已触发
    echo     等待3秒...
    timeout /t 3 /nobreak >nul

    if exist "C:\ProgramData\BroadbandDialer\cleanup.log" (
        echo     [OK] 日志文件已生成
        echo.
        echo     最新日志内容：
        echo     ----------------------------------------
        type "C:\ProgramData\BroadbandDialer\cleanup.log" 2>nul
        echo     ----------------------------------------
    ) else (
        echo     [WARN] 日志文件未生成（可能需要更多时间）
    )
)

echo.
echo ========================================
echo 验证完成
echo ========================================
echo.

if %ERRORS% GTR 0 (
    echo 发现 %ERRORS% 个错误，请检查安装！
    echo.
    echo 建议：
    echo   1. 以管理员身份重新运行安装程序
    echo   2. 检查防火墙/杀毒软件是否阻止
    echo   3. 查看 INSTALL_GUIDE.md 了解详情
) else (
    echo ✅ 所有核心组件安装成功！
    echo.
    echo 下一步：
    echo   1. 双击桌面"宽带拨号助手"快捷方式
    echo   2. 配置路由器IP和密码
    echo   3. 点击"连接"按钮
    echo   4. 关机时自动清理生效！
)

echo.
pause
