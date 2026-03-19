# 宽带拨号工具

一个用于管理TP-Link路由器宽带拨号的Windows工具，支持自动连接和关机时自动清理账号。

## 功能特性

- ✅ 自动PPPoE拨号连接
- ✅ 自动断开并清除账号密码
- ✅ 系统托盘支持
- ✅ 内置浏览器，零依赖运行
- ✅ 关机时自动清理路由器账号（通过后台服务）
- ✅ 友好的图形界面

## 系统要求

- Windows 7/10/11 (32位或64位)
- 无需安装Python
- 无需安装Chrome浏览器

## 项目结构

```
├── tp_link_broadband_dialer.py    # 主程序
├── shutdown_cleanup_service.py    # 后台清理服务
├── service_installer.py           # 服务安装器（GUI）
├── chrome-win64/                  # 内置浏览器
├── build_complete.bat             # 完整打包脚本
├── SetupScript.nsi                # NSIS安装脚本
└── *.spec                         # PyInstaller配置文件
```

## 快速开始

### 方式1：从源代码运行（需要Python环境）

1. 安装依赖：
```bash
pip install playwright pywin32 pillow pystray
playwright install chromium
```

2. 运行主程序：
```bash
python tp_link_broadband_dialer.py
```

### 方式2：使用打包的exe（推荐）

1. 运行安装包 `Release\Setup.exe`
2. 安装完成后从开始菜单启动

## 打包说明

### 1. 准备环境

```bash
# 安装打包依赖
pip install pyinstaller pywin32

# 安装NSIS（可选，用于创建安装包）
# 下载：https://nsis.sourceforge.io/
```

### 2. 打包项目

```bash
# 运行完整打包脚本
build_complete.bat

# 这将创建：
# - dist\TP-Link_Dialer\         (主程序)
# - dist\CleanupService\         (清理服务)
# - dist\ServiceInstaller.exe    (服务安装器)
# - Release\Setup.exe            (安装包)
```

### 3. 清理项目

```bash
# 删除不需要的文件
cleanup_project.bat
```

## 使用说明

### 主程序

1. 输入宽带账号和密码
2. 点击"开始连接"按钮
3. 等待连接成功
4. 使用完成后：
   - 手动点击"断开连接"清除账号，或
   - 直接关闭窗口，关机时服务会自动清理

### 清理服务

清理服务在后台运行，关机时自动清除路由器账号。

**安装服务：**
```bash
# 方法1：使用图形化工具
启动服务管理工具.bat

# 方法2：使用命令行
python shutdown_cleanup_service.py install
net start TPLinkShutdownCleanup
```

**管理服务：**
```bash
# 查看状态
python shutdown_cleanup_service.py status

# 启动服务
python shutdown_cleanup_service.py start

# 停止服务
python shutdown_cleanup_service.py stop

# 卸载服务
python shutdown_cleanup_service.py remove
```

## 配置说明

### 路由器配置

默认配置：
- 路由器IP: `192.168.1.1`
- 管理员密码: `Cdu@123`

如需修改，请编辑以下文件中的配置：
- `tp_link_broadband_dialer.py` (主程序)
- `shutdown_cleanup_service.py` (清理服务)

找到 `RouterLoginGUI.__init__` 和 `RouterAccountCleaner.__init__` 中的配置。

## 故障排除

### 主程序无法启动

1. 检查内置浏览器文件是否存在：`chrome-win64\chrome.exe`
2. 查看日志（双击进度条可查看详细日志）
3. 确保路由器IP地址和密码配置正确

### 服务无法安装

1. 以管理员身份运行
2. 检查PyWin32是否正确安装
3. 查看服务日志：`%TEMP%\tplink_cleanup\cleanup_service.log`

### 关机时账号未清除

1. 检查服务是否正在运行：`sc query TPLinkShutdownCleanup`
2. 查看服务日志确认清理过程
3. 确保正常关机（不要强制关机）

## 文档

- [更新日志](CHANGELOG.md) - 版本更新记录
- [清理服务说明](CLEANUP_SERVICE_README.md) - 后台服务详细说明

## 技术栈

- **界面**: Tkinter
- **浏览器自动化**: Playwright
- **系统服务**: PyWin32
- **打包工具**: PyInstaller
- **安装程序**: NSIS

## 许可证

本项目仅供学习和个人使用。

## 作者

Kilo Code

## 版本

- 当前版本: 2.0
- 更新日期: 2026-03-18
