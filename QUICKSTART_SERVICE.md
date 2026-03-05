# TP-Link宽带拨号服务 - 快速开始指南

## 5分钟快速上手

### 第一步：安装依赖

```batch
pip install -r requirements_service.txt
```

### 第二步：构建服务

```batch
build_service.bat
```

等待构建完成（约2-3分钟）

### 第三步：安装服务

**右键点击** `install_service.bat`，选择**"以管理员身份运行"**

安装脚本会自动：
- ✅ 安装服务
- ✅ 启动服务
- ✅ 打开服务管理器

### 第四步：配置路由器

1. 在服务管理器中，点击**"打开控制面板"**
2. 输入路由器地址（通常是 `http://192.168.1.1`）
3. 输入管理员账号密码
4. 点击**"连接拨号"**

### 完成！

现在，当你关机或重启电脑时：
- ✅ 服务会自动拦截关机事件
- ✅ 自动断开路由器拨号
- ✅ 自动清除账号信息
- ✅ 然后允许系统关机

## 验证服务是否工作

### 方法1：查看服务状态

打开服务管理器，检查服务状态是否为**"正在运行"**

### 方法2：查看日志

在服务管理器中，点击**"查看日志"**按钮

### 方法3：使用命令行

```batch
sc query TPLinkBroadbandDialer
```

应该显示 `STATE: RUNNING`

## 常用操作

### 启动服务

```batch
net start TPLinkBroadbandDialer
```

### 停止服务

```batch
net stop TPLinkBroadbandDialer
```

### 重启服务

```batch
net stop TPLinkBroadbandDialer
net start TPLinkBroadbandDialer
```

### 卸载服务

**右键点击** `uninstall_service.bat`，选择**"以管理员身份运行"**

## 故障排除

### 问题：服务安装失败

**解决方案：**
- 确保以管理员身份运行安装脚本
- 检查是否已安装旧版本，如果是，先卸载

### 问题：服务无法启动

**解决方案：**
1. 检查Windows防火墙设置
2. 查看服务日志：`%TEMP%\tplink_dialer\service.log`
3. 检查端口80是否被占用

### 问题：关机时没有断开拨号

**解决方案：**
1. 确保服务正在运行
2. 查看服务日志，确认是否收到关机通知
3. 检查路由器连接是否正常

## 进阶使用

### 修改服务启动类型

使用服务管理器（services.msc）：
1. 按 `Win + R`，输入 `services.msc`
2. 找到 "TP-Link宽带拨号服务"
3. 右键 → 属性 → 启动类型
4. 选择：
   - **自动**（推荐）：系统启动时自动运行
   - **手动**：需要手动启动
   - **已禁用**：禁用服务

### 设置关机超时时间

默认超时时间是30秒，可以在注册表中修改：

**警告：修改注册表有风险，请谨慎操作！**

1. 按 `Win + R`，输入 `regedit`
2. 导航到：
   ```
   HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control
   ```
3. 找到或创建 `WaitToKillServiceTimeout` 值
4. 设置为 `30000`（30秒，单位：毫秒）

### 查看详细日志

修改服务代码，将日志级别改为DEBUG：

```python
# 在 tp_link_broadband_dialer_service.py 中
logging.basicConfig(
    level=logging.DEBUG,  # 改为 DEBUG
    ...
)
```

然后重新构建和安装服务。

## 与GUI版本的区别

| 特性 | GUI版本 | 服务版本 |
|------|---------|----------|
| 关机拦截 | ⚠️ 可能不可靠 | ✅ 非常可靠 |
| 超时时间 | 5秒 | 30秒-3分钟 |
| 自动启动 | ❌ 需要手动启动 | ✅ 系统启动时自动运行 |
| 无需登录 | ❌ 需要用户登录 | ✅ 可以在登录前运行 |
| 资源占用 | 低 | 中等 |

**推荐：** 如果需要在关机时可靠地断开拨号，使用服务版本。

## 下一步

- 📖 阅读完整文档：`SERVICE_README.md`
- 🔧 配置路由器：使用控制面板
- 📊 监控服务：使用服务管理器
- 📝 查看日志：`%TEMP%\tplink_dialer\service.log`

## 获取帮助

如果遇到问题：

1. 查看 `SERVICE_README.md` 中的常见问题解答
2. 查看服务日志
3. 提交Issue并附上日志文件

---

**祝使用愉快！** 🎉
