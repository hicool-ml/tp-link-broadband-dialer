# TP-Link宽带拨号工具 - 服务版本

## 项目概述

TP-Link宽带拨号工具是一个Windows应用程序，用于自动管理TP-Link路由器的宽带拨号。本项目提供了两个版本：

1. **GUI版本**：带图形界面的应用程序
2. **服务版本**：作为Windows系统服务运行（推荐）

## 核心功能

### 1. 自动拨号连接
- 自动登录路由器管理界面
- 自动输入账号密码
- 自动点击拨号按钮
- 支持多种路由器型号

### 2. 关机前自动断开
- **服务版本特有**：可靠拦截关机事件
- 自动断开拨号连接
- 自动清除账号密码
- 保护账号安全

### 3. 状态监控
- 实时显示连接状态
- 托盘图标显示（在线/离线/连接中/错误）
- 自动重连（可选）

### 4. 日志记录
- 详细记录所有操作
- 便于故障排除
- 支持查看历史日志

## 版本对比

| 特性 | GUI版本 | 服务版本 |
|------|---------|----------|
| **关机拦截** | ⚠️ 可能不可靠 | ✅ 非常可靠 |
| **超时时间** | 5秒 | 30秒-3分钟 |
| **自动启动** | ❌ 需要手动启动 | ✅ 系统启动时自动运行 |
| **无需登录** | ❌ 需要用户登录 | ✅ 可以在登录前运行 |
| **图形界面** | ✅ 完整GUI | ✅ 包含控制面板 |
| **资源占用** | 低 | 中等 |
| **适用场景** | 临时使用 | 长期运行 |

**推荐使用场景：**
- **服务版本**：需要在关机时可靠地断开拨号
- **GUI版本**：临时使用或测试

## 快速开始

### 安装服务版本（推荐）

#### 方法1：一键安装（最简单）

1. **右键点击** `build_and_install_service.bat`
2. 选择**"以管理员身份运行"**
3. 等待安装完成

#### 方法2：分步安装

**步骤1：安装依赖**
```batch
pip install -r requirements_service.txt
```

**步骤2：构建服务**
```batch
build_service.bat
```

**步骤3：安装服务**（需要管理员权限）
```batch
install_service.bat
```

**步骤4：配置路由器**
1. 打开服务管理器（会自动打开）
2. 点击"打开控制面板"
3. 输入路由器地址和账号密码
4. 点击"连接拨号"

### 使用GUI版本

**步骤1：构建程序**
```batch
build_exe_onedir.bat
```

**步骤2：运行程序**
```batch
dist\TP-Link_Dialer\TP-Link_Dialer.exe
```

## 服务管理

### 使用服务管理器

服务管理器提供图形界面来管理服务：

- **安装服务**：将服务安装到系统
- **启动服务**：启动已安装的服务
- **停止服务**：停止正在运行的服务
- **卸载服务**：从系统中移除服务
- **刷新状态**：查看服务当前状态
- **查看日志**：打开服务日志文件
- **打开控制面板**：打开拨号控制面板

### 使用命令行

```batch
# 启动服务
net start TPLinkBroadbandDialer

# 停止服务
net stop TPLinkBroadbandDialer

# 查看状态
sc query TPLinkBroadbandDialer
```

### 卸载服务

**右键点击** `uninstall_service.bat`，选择**"以管理员身份运行"**

## 测试服务

运行测试脚本检查服务是否正常工作：

```batch
run_test.bat
```

测试包括：
- ✅ 服务安装状态
- ✅ 服务运行状态
- ✅ 服务日志
- ✅ 关机拦截能力
- ✅ 浏览器
- ✅ 依赖项

## 文件说明

### 核心文件

- **tp_link_broadband_dialer.py**：主程序（GUI版本）
- **tp_link_broadband_dialer_service.py**：服务版本
- **service_manager.py**：服务管理器

### 构建脚本

- **build_service.bat**：构建服务程序
- **build_exe_onedir.bat**：构建GUI程序（onedir模式）
- **build_exe.bat**：构建GUI程序（onefile模式）

### 安装/卸载脚本

- **install_service.bat**：安装服务
- **uninstall_service.bat**：卸载服务
- **build_and_install_service.bat**：一键构建和安装

### 测试脚本

- **test_service.py**：服务测试脚本
- **run_test.bat**：运行测试脚本

### 文档

- **SERVICE_README.md**：服务版本完整文档
- **QUICKSTART_SERVICE.md**：快速开始指南
- **README.md**：项目主文档

## 系统要求

### 操作系统
- Windows 7 或更高版本
- Windows Server 2008 R2 或更高版本

### 依赖项
- Python 3.8 或更高版本
- pywin32
- playwright
- tkinter（通常随Python一起安装）

### 浏览器
- Chrome/Chromium（自动下载或手动放置）

## 工作原理

### 服务版本的关机拦截流程

1. **系统发出关机信号**
   - 用户点击关机/重启
   - 系统开始关机流程

2. **服务接收关机通知**
   - Windows发送 `SERVICE_CONTROL_SHUTDOWN` 控制码
   - 服务的 `SvcShutdown()` 方法被调用

3. **执行清理操作**
   - 断开路由器拨号
   - 清除账号信息
   - 记录日志

4. **允许系统关机**
   - 服务报告停止完成
   - 系统继续关机流程

### 为什么服务版本更可靠？

1. **关机优先级高**
   - Windows在关机时会先停止服务
   - 服务有更高的优先级来处理关机事件

2. **超时时间长**
   - GUI应用程序：5秒
   - 系统服务：30秒（默认），最长3分钟
   - 有足够时间完成清理操作

3. **与用户会话分离**
   - 服务不受用户注销影响
   - 即使没有用户登录，服务也能正常工作

## 常见问题

### Q1: 服务安装失败？

**A:** 确保以管理员身份运行安装脚本：
- 右键点击 `install_service.bat`
- 选择"以管理员身份运行"

### Q2: 服务无法启动？

**A:** 检查以下几点：
1. 确保服务已正确安装
2. 检查Windows事件查看器中的错误信息
3. 查看服务日志文件
4. 确保端口80未被其他程序占用

### Q3: 关机时没有断开拨号？

**A:** 检查以下几点：
1. 确保服务正在运行
2. 查看服务日志，确认是否收到关机通知
3. 检查路由器连接是否正常
4. 确保账号信息已正确配置

### Q4: 如何查看服务日志？

**A:** 日志文件位置：
```
%TEMP%\tplink_dialer\service.log
```

通常路径为：
```
C:\Users\<YourUsername>\AppData\Local\Temp\tplink_dialer\service.log
```

### Q5: 服务和GUI应用程序可以同时运行吗？

**A:** 不建议。服务版本已经包含了所有功能，同时运行可能会导致冲突。

### Q6: 如何从GUI版本切换到服务版本？

**A:**
1. 卸载GUI版本（如果已安装为开机启动）
2. 安装服务版本
3. 使用服务管理器管理服务

## 技术支持

### 获取帮助

如果遇到问题：

1. 查看 `SERVICE_README.md` 中的常见问题解答
2. 查看服务日志
3. 运行测试脚本：`run_test.bat`
4. 提交Issue并附上日志文件

### 日志位置

- **服务日志**：`%TEMP%\tplink_dialer\service.log`
- **Windows事件查看器**：`eventvwr.msc`

## 开发信息

### 项目结构

```
.
├── tp_link_broadband_dialer.py          # 主程序（GUI版本）
├── tp_link_broadband_dialer_service.py  # 服务版本
├── service_manager.py                    # 服务管理器
├── build_service.bat                     # 构建服务
├── install_service.bat                   # 安装服务
├── uninstall_service.bat                 # 卸载服务
├── test_service.py                       # 测试脚本
├── SERVICE_README.md                     # 服务文档
├── QUICKSTART_SERVICE.md                 # 快速开始
└── SERVICE_SUMMARY.md                    # 本文档
```

### 贡献

欢迎提交Issue和Pull Request！

## 许可证

本项目遵循MIT许可证。

## 更新日志

### Version 1.0.0 (2024-03-05)
- ✅ 初始版本
- ✅ 实现Windows服务功能
- ✅ 支持关机拦截
- ✅ 支持自动断开拨号
- ✅ 支持自动清除账号
- ✅ 提供服务管理器
- ✅ 提供完整的文档和测试工具

---

**祝使用愉快！** 🎉

如有问题，请查看文档或提交Issue。
