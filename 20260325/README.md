# TP-Link 宽带拨号助手 v1.0
## 发布日期：2026-03-25

## 版本特性

### 核心功能
- ✅ **HTTP API通信** - 无需浏览器自动化，直接与路由器通信
- ✅ **强制随机MAC** - 自动生成随机MAC地址（02:XX:XX:XX:XX:XX）
- ✅ **系统托盘支持** - 最小化到托盘，支持状态图标显示
- ✅ **关机清理服务** - Windows服务自动清理路由器账号

### 用户界面
- ✅ 简洁的GUI界面（Tkinter）
- ✅ 配置向导（首次运行）
- ✅ 实时日志显示
- ✅ 托盘菜单（显示/隐藏/断开/退出）

### 本版本修复
1. **NSIS中文乱码** - 使用Unicode和LangString支持中文快捷方式
2. **托盘退出假死** - 改进退出流程，移除emoji字符
3. **服务安装** - 添加延迟和错误检查

## 文件说明

### 核心代码
- `tp_link_broadband_dialer_http.py` - 主程序（GUI）
- `tplink_http_cleaner.py` - HTTP API通信核心
- `config_manager.py` - 配置管理（加密存储）
- `service_http.py` - Windows关机清理服务

### 构建脚本
- `build_main.spec` - 主程序PyInstaller配置
- `build_service.spec` - 服务程序PyInstaller配置
- `setup_build.nsi` - NSIS安装程序脚本
- `构建.bat` - 一键构建脚本

### 资源文件
- `app.ico` - 应用图标
- `online.ico` - 在线状态图标
- `offline.ico` - 离线状态图标
- `connecting.ico` - 连接中图标
- `error.ico` - 错误状态图标
- `version_info.txt` - 版本信息

## 构建步骤

### 前置要求
- Python 3.11
- PyInstaller：`pip install pyinstaller`
- NSIS（已安装）
- 依赖：`pip install requests pystray pillow pywin32`

### 方法1：使用构建脚本（推荐）
```bash
cd D:\13jiao\20260325
构建.bat
```

### 方法2：手动构建
```bash
# 1. 构建主程序
python -m PyInstaller --clean --noconfirm build_main.spec

# 2. 构建服务程序
python -m PyInstaller --clean --noconfirm build_service.spec

# 3. 构建安装程序
"C:\Program Files (x86)\NSIS\makensis.exe" setup_build.nsi
```

## 输出文件
- `dist\broadband_dialer.exe` (21MB) - 主程序
- `dist\TPLinkCleanupService.exe` (11MB) - 服务程序
- `Broadband_Dialer_Setup.exe` (31MB) - 安装程序

## 安装配置
- **安装目录**：`C:\Program Files (x86)\Broadband_Dialer`
- **桌面快捷方式**：宽带拨号（中文）
- **开始菜单**：Broadband_Dialer（英文）
- **服务名称**：TPLinkShutdownCleanup

## 配置文件位置
- **主程序配置**：`%USERPROFILE%\.tplink_dialer\config.json`
- **服务日志**：`%TEMP%\tplink_cleanup\cleanup_service.log`

## 使用说明
1. 运行安装程序（需要管理员权限）
2. 首次启动会显示配置向导
3. 输入路由器IP和管理员密码
4. 点击"连接"按钮进行拨号
5. 关机时服务自动清理路由器账号

## 技术架构
- **GUI框架**：Tkinter
- **托盘图标**：pystray + PIL
- **HTTP通信**：requests + 自定义加密
- **Windows服务**：pywin32
- **打包工具**：PyInstaller + NSIS

## 已知问题
- 无

## 更新日志
### v1.0.0 (2026-03-25)
- 初始发布版本
- 使用HTTP API替代浏览器自动化
- 系统托盘支持
- 强制随机MAC地址
- 关机清理服务
- NSIS安装程序（Unicode支持）
