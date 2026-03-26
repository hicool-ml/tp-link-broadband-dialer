# 服务 1053 错误测试 - 简化版服务代码

## 测试版本

**服务代码：** service_http.py（简化版）
**编译时间：** 2026-03-25 15:21

## 核心修复点

### ✅ 1. 立即报告 RUNNING
```python
def SvcDoRun(self):
    # ✅ 第一行就报告RUNNING
    self.ReportServiceStatus(win32service.SERVICE_RUNNING)

    # 后台初始化
    self.setup_logging()
```

### ✅ 2. 延迟导入模块
```python
def _perform_cleanup(self):
    # ✅ 在使用时才导入
    from config_manager import ConfigManager
    from tplink_http_cleaner import TPLinkHTTPCleaner
```

### ✅ 3. PyInstaller 包含模块
```python
hiddenimports=[
    ...
    # ✅ 延迟导入的模块
    'config_manager',
    'tplink_http_cleaner',
]
```

### ✅ 4. 添加 START_PENDING
```python
def __init__(self, args):
    ...
    # ✅ 防止1053
    self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
```

## 测试步骤

### 1. 卸载旧服务（如果存在）
```bash
cd D:\13jiao\20260325

# 以管理员身份运行
dist\TPLinkCleanupService.exe remove
```

### 2. 安装新服务
```bash
dist\TPLinkCleanupService.exe install
```

**预期输出：**
```
正在安装TP-Link路由器清理服务（HTTP版）...
[OK] 服务安装成功!
```

### 3. 启动服务
```bash
net start TPLinkShutdownCleanup
```

**预期结果：**
- ✅ 服务成功启动（不再出现 1053 错误）
- ✅ 服务状态显示为 "RUNNING"

### 4. 检查服务状态
```bash
sc query TPLinkShutdownCleanup
```

**预期输出：**
```
SERVICE_NAME: TPLinkShutdownCleanup
        TYPE               : 10  WIN32_OWN_PROCESS
        STATE              : 4  RUNNING
```

**关键：** `STATE` 必须是 `4  RUNNING`

### 5. 查看日志
```bash
type %TEMP%\tplink_cleanup\cleanup_service.log
```

**预期输出：**
```
2026-03-25 XX:XX:XX - INFO - 服务已启动，等待关机...
```

## 1053 错误对照表

| 现象 | 原因 | 解决方案 |
|------|------|----------|
| 启动超时30秒 | 初始化太慢 | 先RUNNING后初始化 |
| 模块导入失败 | 打包未包含 | hiddenimports |
| 配置读取卡顿 | 文件IO慢 | 延迟到关机时执行 |
| 服务未响应 | 状态未报告 | 添加START_PENDING |

## 如果仍然出现 1053

### 检查清单

1. **检查 PyInstaller 警告**
   ```bash
   # 查看编译日志
   type build\build_service\warn-build_service.txt
   ```
   - 查找 "module not found" 警告
   - 确认 config_manager 和 tplink_http_cleaner 已包含

2. **手动测试导入**
   ```python
   # 在 Python 中测试
   python -c "from config_manager import ConfigManager; print('OK')"
   python -c "from tplink_http_cleaner import TPLinkHTTPCleaner; print('OK')"
   ```

3. **检查服务日志**
   ```bash
   type %TEMP%\tplink_cleanup\cleanup_service.log
   ```
   - 查找 ImportError 或 ModuleNotFoundError

4. **使用事件查看器**
   ```
   Win + R → eventvwr
   Windows 日志 → 应用程序
   查找错误来源：TPLinkShutdownCleanup
   ```

## 完整测试脚本

保存为 `test_service.bat` 并以管理员身份运行：

```batch
@echo off
chcp 65001 >nul
echo ========================================
echo 服务 1053 测试
echo ========================================
echo.

cd /d %~dp0

echo [1/4] 卸载旧服务...
dist\TPLinkCleanupService.exe remove 2>nul

echo.
echo [2/4] 安装新服务...
dist\TPLinkCleanupService.exe install

if errorlevel 1 (
    echo [ERROR] 服务安装失败！
    pause
    exit /b 1
)

echo.
echo [3/4] 启动服务...
net start TPLinkShutdownCleanup

if errorlevel 1 (
    echo [ERROR] 服务启动失败！
    echo.
    echo 可能原因：
    echo   - Error 1053: 服务启动超时
    echo   - Error 1060: 服务未安装
    echo.
    pause
    exit /b 1
)

echo.
echo [4/4] 检查服务状态...
sc query TPLinkShutdownCleanup

echo.
echo ========================================
echo 测试完成！
echo ========================================
echo.
echo 如果 STATE 是 4 RUNNING，说明 1053 已修复！
echo.
echo 日志位置: %TEMP%\tplink_cleanup\cleanup_service.log
echo.

pause
```

## 文件清单

- **[service_http.py](service_http.py)** - 简化版服务代码
- **[build_service.spec](build_service.spec)** - PyInstaller配置（已添加hiddenimports）
- **[dist\TPLinkCleanupService.exe](dist\TPLinkCleanupService.exe)** - 编译后的服务程序

## 代码对比

### 旧版（可能导致1053）
```python
def SvcDoRun(self):
    # ❌ 先初始化（可能很慢）
    self.setup_logging()
    self.validate_config()

    # ❌ 最后才报告RUNNING
    self.ReportServiceStatus(win32service.SERVICE_RUNNING)
```

### 新版（防1053）
```python
def SvcDoRun(self):
    # ✅ 立即报告RUNNING
    self.ReportServiceStatus(win32service.SERVICE_RUNNING)

    # ✅ 后台初始化
    self.setup_logging()
```

## 技术总结

**❗ 1053 错误 = 服务启动超过30秒**

**✅ 解决方案三要素：**
1. 先 RUNNING，后初始化
2. 延迟导入重量级模块
3. PyInstaller 包含所有模块

**🎯 核心原则：服务启动阶段要做的事情越少越好！**
