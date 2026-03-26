# TP-Link 宽带拨号助手 - 构建指南

## 环境要求

### 必需组件
- Python 3.11
- PyInstaller：`pip install pyinstaller`
- NSIS (已安装)
- 依赖库：
  ```bash
  pip install requests pystray pillow pywin32
  ```

## 项目结构
```
20260325/
├── tp_link_broadband_dialer_http.py  # 主程序（GUI）
├── tplink_http_cleaner.py            # HTTP API核心
├── config_manager.py                  # 配置管理
├── service_http.py                    # 系统服务
├── build_main.spec                     # 主程序spec
├── build_service.spec                  # 服务spec
├── setup_build.nsi                     # NSIS安装脚本
├── build.bat                           # 构建脚本（英文版）
├── 构建.bat                            # 构建脚本（中文版）
├── app.ico                             # 应用图标
├── online.ico                          # 在线图标
├── offline.ico                         # 离线图标
├── connecting.ico                      # 连接中图标
├── error.ico                           # 错误图标
└── version_info.txt                    # 版本信息
```

## 构建步骤

### 方式1：使用构建脚本（推荐）

1. **运行构建脚本**
   ```bash
   cd D:\13jiao\20260325
   build.bat
   ```

2. **等待构建完成**
   - 主程序：`dist\broadband_dialer.exe`
   - 服务程序：`dist\TPLinkCleanupService.exe`

3. **构建安装程序**
   ```bash
   "C:\Program Files (x86)\NSIS\makensis.exe" setup_build.nsi
   ```
   - 输出：`Broadband_Dialer_Setup.exe`

### 方式2：手动构建

#### 步骤1：构建主程序
```bash
cd D:\13jiao\20260325
python -m PyInstaller --clean build_main.spec
```

#### 步骤2：构建服务程序
```bash
python -m PyInstaller --clean build_service.spec
```

#### 步骤3：构建安装程序
```bash
"C:\Program Files (x86)\NSIS\makensis.exe" setup_build.nsi
```

## 安装程序特性

### ✅ Unicode支持
- 启用Unicode支持，解决中文显示问题
- 使用LangString定义中文快捷方式名称

### ✅ 组件选择
- **主程序**：必须安装，包含GUI和托盘功能
- **系统服务**：推荐安装，关机时自动清理路由器账号

### ✅ 服务自动部署
- 安装Windows服务
- 自动启动服务
- 验证服务状态

### ✅ 快捷方式
- 桌面快捷方式：**宽带拨号**（中文）
- 开始菜单程序组：Broadband_Dialer（英文）
- 服务状态查看

## 验证安装

### 检查主程序
1. 双击桌面"宽带拨号"快捷方式启动程序
2. 首次运行会显示配置向导
3. 配置路由器IP和管理密码
4. 测试连接功能

### 检查服务
1. 打开服务管理器（`services.msc`）
2. 查找 `TPLinkShutdownCleanup` 服务
3. 状态应为"正在运行"
4. 启动类型应为"自动"

### 测试关机清理
1. 连接宽带账号
2. 关闭主程序（保留托盘图标）
3. 重启电脑
4. 检查路由器账号是否已清空

## 文件说明

### 输出文件
```
dist/
├── broadband_dialer.exe          # 主程序（~21MB）
└── TPLinkCleanupService.exe      # 服务程序（~11MB）

Broadband_Dialer_Setup.exe        # 安装程序（~31MB）
```

### 配置文件位置
- 主程序配置：`%USERPROFILE%\.tplink_dialer\config.json`
- 服务日志：`%TEMP%\tplink_cleanup\cleanup_service.log`

## 故障排除

### 构建问题

**问题：PyInstaller找不到模块**
```
解决方案：pip install pyinstaller --upgrade
```

**问题：NSIS编译错误**
```
解决方案：确保NSIS已正确安装
检查路径：C:\Program Files (x86)\NSIS\
```

### 安装问题

**问题：安装失败提示权限不足**
```
解决方案：右键安装程序 → 选择"以管理员身份运行"
```

**问题：服务安装失败**
```
解决方案：
1. 检查是否有旧服务残留：sc query TPLinkShutdownCleanup
2. 如有，手动删除：sc delete TPLinkShutdownCleanup
3. 重新运行安装程序
```

### 运行问题

**问题：托盘图标不显示**
```
解决方案：
1. 检查pystray和PIL是否已安装
2. 检查图标文件是否存在
```

**问题：服务无法启动**
```
解决方案：
1. 检查日志：%TEMP%\tplink_cleanup\cleanup_service.log
2. 确认config.json配置正确
3. 手动测试：TPLinkCleanupService.exe start
```

**问题：托盘退出假死**
```
解决方案：已在v1.0中修复
- 移除emoji字符
- 改进退出流程
- 使用轮询检查状态
```

## 卸载

### 方式1：通过控制面板
1. 控制面板 → 程序和功能
2. 找到"Broadband Dialer"
3. 点击"卸载"

### 方式2：通过开始菜单
1. 开始菜单 → Broadband_Dialer
2. 点击"Uninstall"

### 方式3：手动卸载
```bash
# 停止并卸载服务
net stop TPLinkShutdownCleanup
TPLinkCleanupService.exe remove

# 删除文件
rm -r "C:\Program Files (x86)\Broadband_Dialer"
```

## 版本信息

### v1.0.0 (2026-03-25)
- ✅ 使用HTTP API替代浏览器自动化
- ✅ 系统托盘支持
- ✅ 强制使用随机MAC
- ✅ 关机清理服务
- ✅ 简化的用户界面
- ✅ 一键安装和卸载
- ✅ Unicode支持中文快捷方式
- ✅ 修复托盘退出假死问题
- ✅ 修复服务安装问题

## 技术架构

### 核心技术
- **GUI框架**：Tkinter
- **托盘图标**：pystray + PIL
- **HTTP通信**：requests + 自定义加密
- **Windows服务**：pywin32
- **打包工具**：PyInstaller + NSIS

### 通信流程
1. 主程序通过HTTP API与路由器通信
2. 使用自定义密码加密算法
3. 基于stok令牌的身份验证
4. 支持拨号、断开、MAC设置等操作

### 服务机制
1. 服务运行在LocalSystem账户
2. 监听Windows关机事件
3. 关机前自动清理路由器账号
4. 记录详细日志到临时目录
