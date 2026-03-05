# TP-Link宽带拨号服务 - Windows服务版本

## 概述

TP-Link宽带拨号服务是一个Windows系统服务，可以在关机前自动断开TP-Link路由器拨号并清除账号信息。

## 服务版本的优势

与普通应用程序相比，作为Windows服务运行有以下优势：

### 1. **关机优先级高**
- Windows在关机时会先停止服务，然后才关闭应用程序
- 服务可以可靠地拦截关机事件

### 2. **关机超时时间长**
- GUI应用程序关机超时时间：**5秒**
- 系统服务关机超时时间：**30秒（默认），最长可达3分钟**
- 有足够的时间完成断开拨号和清除账号操作

### 3. **自动启动**
- 服务设置为自动启动，系统启动时自动运行
- 无需用户登录即可运行

### 4. **与用户会话分离**
- 服务不受用户注销影响
- 即使没有用户登录，服务也能正常工作

### 5. **更高的权限**
- 服务可以以本地系统账户运行
- 拥有更高的权限来执行系统操作

## 安装步骤

### 方法1：使用安装脚本（推荐）

1. **构建服务程序**
   ```batch
   build_service.bat
   ```

2. **安装服务**（需要管理员权限）
   ```batch
   install_service.bat
   ```

   右键点击 `install_service.bat`，选择"以管理员身份运行"

3. **完成安装**
   - 安装脚本会自动：
     - 安装服务
     - 启动服务
     - 打开服务管理器

### 方法2：手动安装

1. **构建服务程序**
   ```batch
   build_service.bat
   ```

2. **安装服务**
   ```batch
   cd dist\TPLinkDialerService
   TPLinkDialerService.exe install
   ```

3. **启动服务**
   ```batch
   net start TPLinkBroadbandDialer
   ```

4. **打开服务管理器**
   ```batch
   cd ..\ServiceManager
   ServiceManager.exe
   ```

## 使用说明

### 服务管理器

服务管理器提供图形界面来管理服务：

- **安装服务**：将服务安装到系统
- **启动服务**：启动已安装的服务
- **停止服务**：停止正在运行的服务
- **卸载服务**：从系统中移除服务
- **刷新状态**：查看服务当前状态
- **查看日志**：打开服务日志文件
- **打开控制面板**：打开拨号控制面板

### 命令行管理

你也可以使用命令行来管理服务：

```batch
# 安装服务
dist\TPLinkDialerService\TPLinkDialerService.exe install

# 启动服务
net start TPLinkBroadbandDialer

# 停止服务
net stop TPLinkBroadbandDialer

# 卸载服务
dist\TPLinkDialerService\TPLinkDialerService.exe remove

# 查看服务状态
sc query TPLinkBroadbandDialer
```

### 服务日志

服务日志保存在：
```
%TEMP%\tplink_dialer\service.log
```

通常路径为：
```
C:\Users\<YourUsername>\AppData\Local\Temp\tplink_dialer\service.log
```

日志内容包括：
- 服务启动/停止事件
- 关机事件拦截
- 断开拨号操作
- 清除账号操作
- 错误信息

## 工作原理

### 关机拦截流程

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

### 与GUI应用程序的对比

| 特性 | GUI应用程序 | 系统服务 |
|------|------------|----------|
| 关机拦截 | `WM_QUERYENDSESSION` | `SERVICE_CONTROL_SHUTDOWN` |
| 超时时间 | 5秒 | 30秒（默认）- 3分钟 |
| 启动方式 | 用户手动启动 | 系统自动启动 |
| 运行环境 | 用户会话 | 系统级别 |
| 权限级别 | 当前用户权限 | 本地系统权限 |
| 可靠性 | 可能被强制关闭 | 优先级高，可靠 |

## 卸载步骤

### 方法1：使用卸载脚本（推荐）

1. **运行卸载脚本**（需要管理员权限）
   ```batch
   uninstall_service.bat
   ```

   右键点击 `uninstall_service.bat`，选择"以管理员身份运行"

2. **确认卸载**
   - 卸载脚本会自动：
     - 停止服务
     - 移除服务
     - 关闭服务管理器

### 方法2：手动卸载

1. **停止服务**
   ```batch
   net stop TPLinkBroadbandDialer
   ```

2. **卸载服务**
   ```batch
   dist\TPLinkDialerService\TPLinkDialerService.exe remove
   ```

3. **关闭服务管理器**（如果正在运行）

## 常见问题解答

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

**A:** 有两种方法：
1. 使用服务管理器，点击"查看日志"按钮
2. 直接打开日志文件：
   ```
   %TEMP%\tplink_dialer\service.log
   ```

### Q5: 服务和GUI应用程序可以同时运行吗？

**A:** 不建议。服务版本已经包含了所有功能，同时运行可能会导致冲突。

### Q6: 如何从GUI版本切换到服务版本？

**A:**
1. 卸载GUI版本（如果已安装为开机启动）
2. 安装服务版本
3. 使用服务管理器管理服务

### Q7: 服务占用多少资源？

**A:**
- 内存占用：约50-100 MB
- CPU占用：空闲时几乎为0%
- 磁盘占用：约200 MB（包含浏览器）

### Q8: 服务支持哪些Windows版本？

**A:** 支持：
- Windows 7（需要.NET Framework 4.0+）
- Windows 8/8.1
- Windows 10/11
- Windows Server 2008 R2及以上

### Q9: 如何更新服务？

**A:**
1. 停止服务：`net stop TPLinkBroadbandDialer`
2. 卸载旧版本：`dist\TPLinkDialerService\TPLinkDialerService.exe remove`
3. 重新构建：`build_service.bat`
4. 安装新版本：`install_service.bat`

### Q10: 服务会自动重连吗？

**A:** 当前版本不会自动重连。如需自动重连功能，可以在控制面板中配置。

## 技术细节

### 服务配置

- **服务名称**：`TPLinkBroadbandDialer`
- **显示名称**：`TP-Link宽带拨号服务`
- **启动类型**：自动
- **登录身份**：本地系统账户
- **关机超时**：30秒（默认）

### 依赖项

- Python 3.8+
- pywin32
- tkinter
- playwright
- Chrome/Chromium浏览器

### 文件结构

```
dist/
├── TPLinkDialerService/      # 服务程序
│   ├── TPLinkDialerService.exe
│   └── _internal/            # 依赖文件
└── ServiceManager/            # 服务管理器
    ├── ServiceManager.exe
    └── _internal/            # 依赖文件
```

## 安全说明

### 权限要求

- 服务以本地系统账户运行
- 拥有管理员权限
- 可以访问系统级资源

### 安全建议

1. **定期更新**：保持服务为最新版本
2. **检查日志**：定期查看服务日志，确保正常运行
3. **备份数据**：定期备份路由器配置
4. **密码安全**：妥善保管路由器管理员密码

## 故障排除

### 启用详细日志

如果需要更详细的日志信息，可以修改服务代码：

```python
# 在 tp_link_broadband_dialer_service.py 中
logging.basicConfig(
    level=logging.DEBUG,  # 改为 DEBUG
    ...
)
```

### 使用Windows事件查看器

1. 按 `Win + R`，输入 `eventvwr`
2. 导航到 "Windows日志" → "应用程序"
3. 查找来源为 "TPLinkBroadbandDialer" 的事件

### 使用PowerShell管理服务

```powershell
# 查看服务状态
Get-Service TPLinkBroadbandDialer

# 启动服务
Start-Service TPLinkBroadbandDialer

# 停止服务
Stop-Service TPLinkBroadbandDialer

# 重启服务
Restart-Service TPLinkBroadbandDialer

# 查看服务配置
Get-WmiObject Win32_Service | Where-Object {$_.Name -eq 'TPLinkBroadbandDialer'}
```

## 联系支持

如果遇到问题：

1. 查看服务日志
2. 查看Windows事件查看器
3. 检查常见问题解答
4. 提交Issue并附上日志文件

## 许可证

本项目遵循MIT许可证。

## 更新日志

### Version 1.0.0 (2024-03-05)
- 初始版本
- 实现Windows服务功能
- 支持关机拦截
- 支持自动断开拨号
- 支持自动清除账号
- 提供服务管理器
