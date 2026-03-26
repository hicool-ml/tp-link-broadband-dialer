@echo off
REM 服务启动器 - 使用系统Python运行服务脚本
set SCRIPT_DIR=%~dp0
set PYTHON_EXE=python

REM 尝试多个Python路径
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    goto :RUN
)

where python3 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_EXE=python3
    goto :RUN
)

REM 尝试常见安装路径
if exist "C:\Program Files\Python311\python.exe" (
    set PYTHON_EXE=C:\Program Files\Python311\python.exe
    goto :RUN
)

if exist "C:\Program Files\Python310\python.exe" (
    set PYTHON_EXE=C:\Program Files\Python310\python.exe
    goto :RUN
)

if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe
    goto :RUN
)

echo Error: Python not found!
exit /b 1

:RUN
cd /d "%SCRIPT_DIR%"
"%PYTHON_EXE%" service_minimal.py %*
