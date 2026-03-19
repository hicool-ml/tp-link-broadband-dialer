# 打包部署指南

## 环境准备

### 1. 安装Python和依赖

```bash
# 确保Python 3.8+已安装
python --version

# 安装打包依赖
pip install pyinstaller pywin32 playwright

# 安装Playwright浏览器（开发用）
playwright install chromium
```

### 2. 安装NSIS（可选）

如果需要创建Windows安装包，请安装NSIS：

- 下载地址：https://nsis.sourceforge.io/Download
- 安装后确保 `makensis` 命令可用

## 打包流程

### 步骤1：检查项目文件

确保以下文件/目录存在：

```bash
# 必需的Python文件
tp_link_broadband_dialer.py
shutdown_cleanup_service.py
service_installer.py

# 必需的浏览器
chrome-win64/chrome.exe
ms-playwright/

# 必需的图标
app.ico
connecting.ico
error.ico
offline.ico
online.ico

# 必需的配置文件
TP-Link_Dialer_main.spec
CleanupService.spec
ServiceInstaller.spec
SetupScript.nsi
```

### 步骤2：执行完整打包

```bash
# 运行打包脚本
build_complete.bat
```

这将会：

1. 打包主程序 → `dist/TP-Link_Dialer/`
2. 打包清理服务 → `dist/CleanupService/`
3. 打包服务安装器 → `dist/ServiceInstaller.exe`
4. 创建NSIS安装包 → `Release/Setup.exe`

### 步骤3：验证输出

检查以下目录是否正确生成：

```bash
dist/TP-Link_Dialer/
├── TP-Link_Dialer.exe
├── chrome-win64/
└── [其他依赖文件]

dist/CleanupService/
├── CleanupService.exe
├── chrome-win64/
└── [其他依赖文件]

dist/ServiceInstaller.exe

Release/Setup.exe  # 最终安装包
```

## 测试打包结果

### 1. 测试主程序

```bash
# 直接运行主程序
dist\TP-Link_Dialer\TP-Link_Dialer.exe

# 测试功能：
# - 输入账号密码
# - 点击连接
# - 验证能否正常拨号
# - 点击断开
# - 验证能否清除账号
```

### 2. 测试清理服务

```bash
# 安装服务
dist\CleanupService\CleanupService.exe install

# 启动服务
dist\CleanupService\CleanupService.exe start

# 查看状态
dist\CleanupService\CleanupService.exe status

# 测试清理功能
python test_cleanup.py

# 关机测试（需要实际关机）
# 正常关机后检查路由器账号是否已清除
```

### 3. 测试服务安装器

```bash
# 运行服务安装器
dist\ServiceInstaller.exe

# 测试功能：
# - 安装服务
# - 启动服务
# - 查看服务日志
# - 停止服务
# - 卸载服务
```

### 4. 测试完整安装包

```bash
# 在干净的Windows机器上测试
# 1. 运行安装包
Release\Setup.exe

# 2. 从开始菜单启动程序

# 3. 测试所有功能

# 4. 卸载程序
```

## 发布清单

### 方式1：发布安装包（推荐）

```
Release/Setup.exe           # Windows安装包
```

用户只需：
1. 下载 `Setup.exe`
2. 双击安装
3. 从开始菜单启动

### 方式2：发布绿色版本

压缩以下目录：

```
宽带拨号工具.zip
├── TP-Link_Dialer/         # 主程序
├── CleanupService/         # 清理服务
├── ServiceInstaller.exe    # 服务安装器
└── README.md               # 使用说明
```

用户需要：
1. 解压到任意目录
2. 运行 `ServiceInstaller.exe` 安装服务
3. 运行 `TP-Link_Dialer/TP-Link_Dialer.exe` 启动主程序

## 常见问题

### 打包失败

**问题**：PyInstaller打包失败

**解决方案**：
```bash
# 清理缓存
rd /s /q build
rd /s /q dist

# 重新打包
build_complete.bat
```

### 浏览器路径错误

**问题**：找不到浏览器文件

**解决方案**：
```bash
# 确保浏览器文件存在
dir chrome-win64\chrome.exe
dir ms-playwright\chromium-1208\chrome-win64\chrome.exe

# 如果不存在，需要重新下载浏览器
playwright install chromium
```

### 服务安装失败

**问题**：清理服务安装失败

**解决方案**：
```bash
# 以管理员身份运行
# 右键命令提示符 -> 以管理员身份运行

# 检查PyWin32是否安装
pip list | findstr pywin32

# 如果没有，重新安装
pip install pywin32
```

### NSIS编译失败

**问题**：创建安装包失败

**解决方案**：
```bash
# 检查NSIS是否安装
where makensis

# 如果没有，下载安装
# https://nsis.sourceforge.io/Download
```

## 版本发布

### 版本号管理

在以下文件中更新版本号：

1. `README.md` - 版本: 2.0
2. `CHANGELOG.md` - 更新日期和内容
3. `SetupScript.nsi` - `!define APP_VERSION "2.0"`

### 发布步骤

1. 更新版本号和CHANGELOG
2. 运行 `build_complete.bat`
3. 测试所有功能
4. 创建发布标签
5. 上传到发布位置

## 许可和分发

- 本工具仅供学习和个人使用
- 分发时请保留所有许可证文件
- 不得用于商业用途

## 技术支持

如遇到问题，请查看：

- [项目README](README.md)
- [更新日志](CHANGELOG.md)
- [清理服务说明](CLEANUP_SERVICE_README.md)
- [项目结构说明](PROJECT_STRUCTURE.md)
