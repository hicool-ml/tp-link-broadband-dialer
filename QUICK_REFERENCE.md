# 快速参考指南

## 文件清单

### 📁 项目根目录文件

| 文件 | 说明 | 必需 |
|------|------|------|
| `tp_link_broadband_dialer.py` | 主程序（GUI拨号工具） | ✅ |
| `shutdown_cleanup_service.py` | 后台清理服务 | ✅ |
| `service_installer.py` | 服务安装器（GUI） | ✅ |
| `test_cleanup.py` | 测试脚本 | ⚠️ |
| `build_complete.bat` | 完整打包脚本 | ✅ |
| `cleanup_project.bat` | 项目清理脚本 | ⚠️ |
| `manage_cleanup_service.bat` | 服务管理（命令行） | ⚠️ |
| `启动服务管理工具.bat` | 服务管理（GUI启动器） | ⚠️ |

### 📋 配置文件

| 文件 | 说明 | 必需 |
|------|------|------|
| `TP-Link_Dialer_main.spec` | 主程序打包配置 | ✅ |
| `CleanupService.spec` | 清理服务打包配置 | ✅ |
| `ServiceInstaller.spec` | 服务安装器打包配置 | ✅ |
| `SetupScript.nsi` | NSIS安装脚本 | ✅ |

### 🎨 资源文件

| 文件/目录 | 说明 | 必需 |
|----------|------|------|
| `app.ico` | 应用图标 | ✅ |
| `connecting.ico` | 连接中图标 | ✅ |
| `error.ico` | 错误图标 | ✅ |
| `offline.ico` | 离线图标 | ✅ |
| `online.ico` | 在线图标 | ✅ |
| `chrome-win64/` | Chrome浏览器（内置） | ✅ |
| `ms-playwright/` | Playwright依赖 | ✅ |

### 📖 文档文件

| 文件 | 说明 |
|------|------|
| `README.md` | 项目说明 |
| `CHANGELOG.md` | 更新日志 |
| `CLEANUP_SERVICE_README.md` | 清理服务说明 |
| `PROJECT_STRUCTURE.md` | 项目结构说明 |
| `PACKAGING_GUIDE.md` | 打包部署指南 |
| `help.txt` | 帮助文件 |
| `license.txt` | 许可证 |
| `使用说明.txt` | 用户说明 |

## 常用命令

### 开发环境

```bash
# 安装依赖
pip install playwright pywin32 pillow pystray
playwright install chromium

# 运行主程序
python tp_link_broadband_dialer.py

# 运行服务安装器
python service_installer.py

# 测试清理功能
python test_cleanup.py
```

### 服务管理

```bash
# 安装服务
python shutdown_cleanup_service.py install

# 启动服务
python shutdown_cleanup_service.py start

# 停止服务
python shutdown_cleanup_service.py stop

# 查看状态
python shutdown_cleanup_service.py status

# 卸载服务
python shutdown_cleanup_service.py remove
```

### 打包发布

```bash
# 完整打包
build_complete.bat

# 清理项目
cleanup_project.bat

# 查看服务日志
# 日志位置: %TEMP%\tplink_cleanup\cleanup_service.log
```

## 默认配置

### 路由器配置

```
IP地址: 192.168.1.1
管理员密码: Cdu@123
```

### 服务配置

```
服务名称: TPLinkShutdownCleanup
显示名称: TP-Link路由器账号清理服务
启动类型: 自动
```

## 工作流程

### 用户使用流程

1. **安装阶段**
   ```
   运行 Setup.exe
   → 安装主程序
   → 安装清理服务
   → 启动服务
   ```

2. **使用阶段**
   ```
   启动主程序
   → 输入账号密码
   → 点击"开始连接"
   → 等待连接成功
   → 使用网络
   → 使用完成后点击"断开连接"
   ```

3. **关机阶段**
   ```
   用户关机
   → 清理服务接收关机信号
   → 自动连接路由器
   → 清除账号密码
   → 允许系统关机
   ```

## 故障排除

### 主程序问题

| 问题 | 解决方案 |
|------|----------|
| 无法启动 | 检查chrome-win64是否存在 |
| 连接失败 | 检查路由器IP和密码 |
| 清除失败 | 查看日志（双击进度条） |

### 服务问题

| 问题 | 解决方案 |
|------|----------|
| 安装失败 | 以管理员身份运行 |
| 启动失败 | 检查PyWin32是否安装 |
| 清理失败 | 查看%TEMP%\tplink_cleanup\日志 |

### 打包问题

| 问题 | 解决方案 |
|------|----------|
| PyInstaller失败 | 清理build/dist后重试 |
| 浏览器缺失 | 运行playwright install chromium |
| NSIS失败 | 检查NSIS是否安装 |

## 版本信息

```
版本: 2.0
更新日期: 2026-03-18
作者: Kilo Code
```

## 相关链接

- Playwright: https://playwright.dev/
- PyInstaller: https://pyinstaller.org/
- NSIS: https://nsis.sourceforge.io/
