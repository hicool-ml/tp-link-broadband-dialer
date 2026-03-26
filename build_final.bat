@echo off
chcp 65001 >nul
echo ============================================================
echo 构建完整安装包 - 包含便携版Python
echo ============================================================
echo.

echo [1/5] 清理旧构建...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
echo 已清理

echo.
echo [2/5] 构建清理工作程序（包含Playwright）...
python -m PyInstaller CleanupWorker.spec --noconfirm
echo 已构建 cleanup_worker.exe

echo.
echo [3/5] 复制文件到Release目录...
xcopy /E /I /Y "dist\TP-Link_Dialer\*" "Release\"
echo 已复制主程序

echo.
echo [4/5] 复制服务文件...
copy "service_using_pythonservice.py" "Release\CleanupService.py"
copy "config_manager.py" "Release\"
copy "browser_manager.py" "Release\"
copy "dist\cleanup_worker.exe" "Release\"
echo 已复制服务文件

echo.
echo [5/5] 复制Python运行时...
echo 正在复制便携版Python（约200MB，请耐心等待）...
xcopy /E /I /Y "C:\Program Files\Python311\DLLs" "Release\python\DLLs\"
xcopy /E /I /Y "C:\Program Files\Python311\Lib" "Release\python\Lib\"
copy "C:\Program Files\Python311\python.exe" "Release\python\"
copy "C:\Program Files\Python311\python311.dll" "Release\python\"
copy "C:\Program Files\Python311\python3.dll" "Release\python\"
copy "C:\Program Files\Python311\vcruntime140.dll" "Release\python\"
copy "C:\Program Files\Python311\vcruntime140_1.dll" "Release\python\"
echo 已复制Python运行时

echo.
echo [6/6] 生成Setup.exe...
"C:\Program Files (x86)\NSIS\makensis.exe" Setup.nsi

if exist Release\Setup.exe (
    echo.
    echo ============================================================
    echo   构建完成！
    echo ============================================================
    echo.
    dir Release\Setup.exe | find "Setup.exe"
) else (
    echo.
    echo 错误：Setup.exe未生成！
)

pause
