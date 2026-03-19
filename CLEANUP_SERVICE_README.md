# TP-Link路由器账号清理服务说明

## 服务简介

`shutdown_cleanup_service.py` 是一个Windows后台服务，用于在系统关机时自动清除TP-Link路由器中的宽带账号密码。

### 与主程序的关系

- **主程序** (`tp_link_broadband_dialer.py`)：负责连接拨号和手动断开
- **清理服务** (`shutdown_cleanup_service.py`)：负责关机时自动清理账号

两者相互独立，清理服务不负责连接拨号，只在关机时执行清理操作。

## 工作原理

1. 服务安装后会自动启动
2. 服务在后台持续运行，等待关机事件
3. 当系统关机时，服务会收到 `SERVICE_CONTROL_SHUTDOWN` 控制码
4. 服务自动连接到路由器，清除账号密码
5. 清理完成后允许系统关机

## 安装步骤

### 方法1：使用批处理文件（推荐）

双击运行 `manage_cleanup_service.bat`，选择"安装服务"。

### 方法2：使用命令行

```bash
# 安装服务
python shutdown_cleanup_service.py install

# 启动服务
net start TPLinkShutdownCleanup

# 查看服务状态
sc query TPLinkShutdownCleanup
```

## 服务管理命令

```bash
# 安装服务
python shutdown_cleanup_service.py install

# 卸载服务
python shutdown_cleanup_service.py remove

# 启动服务
python shutdown_cleanup_service.py start
# 或
net start TPLinkShutdownCleanup

# 停止服务
python shutdown_cleanup_service.py stop
# 或
net stop TPLinkShutdownCleanup

# 重启服务
python shutdown_cleanup_service.py restart

# 查看服务状态
python shutdown_cleanup_service.py status
# 或
sc query TPLinkShutdownCleanup
```

## 配置说明

服务默认使用以下配置：

```python
router_ip = "192.168.1.1"      # 路由器IP地址
router_password = "Cdu@123"    # 路由器管理员密码
```

如需修改，请编辑 `shutdown_cleanup_service.py` 文件中的 `RouterAccountCleaner` 类。

## 查看日志

服务日志保存在：

```
%TEMP%\tplink_cleanup\cleanup_service.log
```

通常完整路径是：
```
C:\Users\<你的用户名>\AppData\Local\Temp\tplink_cleanup\cleanup_service.log
```

## 故障排除

### 服务安装失败

1. 确保以管理员身份运行命令提示符
2. 检查是否已安装旧版本服务，如有需要先卸载
3. 确保Python环境正确配置

### 服务无法启动

1. 检查日志文件查看错误信息
2. 确保路由器IP地址和密码配置正确
3. 确保内置浏览器文件存在

### 关机时账号未清除

1. 检查服务是否正在运行
2. 查看服务日志确认清理过程
3. 确保路由器网络连接正常
4. 尝试手动运行清理服务测试

## 测试服务

### 手动测试清理功能

创建测试脚本 `test_cleanup.py`：

```python
from shutdown_cleanup_service import RouterAccountCleaner

cleaner = RouterAccountCleaner()
success = cleaner.clear_account()
print(f"清理结果: {'成功' if success else '失败'}")
```

### 关机测试

1. 确保服务正在运行
2. 启动主程序并连接拨号
3. 正常关机（不要强制关机）
4. 检查路由器管理界面确认账号已清除

## 注意事项

1. **正常关机**：请使用Windows的正常关机流程，避免强制关机
2. **网络连接**：确保关机时路由器网络连接正常
3. **服务状态**：定期检查服务是否正在运行
4. **日志查看**：遇到问题时查看日志文件

## 与旧版本的区别

### 旧版本（tp_link_broadband_dialer_service.py）

- 作为Windows服务运行
- 尝试在关机时拦截并清理账号
- 功能复杂，可靠性较低

### 新版本（shutdown_cleanup_service.py）

- 简化的服务设计
- 专注于关机清理功能
- 更可靠的清理流程
- 独立于主程序运行

## 技术细节

### Windows服务控制码

- `SERVICE_CONTROL_SHUTDOWN`：系统关机时发送
- 服务有最多3分钟（180秒）的时间完成清理

### 浏览器自动化

- 使用Playwright进行浏览器自动化
- 无头模式运行，无GUI
- 使用内置浏览器，不依赖系统环境

### 日志记录

- 所有操作都会记录到日志文件
- 日志包含时间戳和操作详情
- 便于故障排除和审计

## 常见问题

**Q: 服务会占用多少系统资源？**
A: 服务在空闲时几乎不占用资源，只在关机时才会启动浏览器执行清理。

**Q: 可以不安装服务吗？**
A: 可以，但关机时账号不会被自动清除，需要手动点击主程序的"断开连接"按钮。

**Q: 服务会影响关机速度吗？**
A: 清理过程通常需要10-15秒，会稍微延长关机时间，但确保了账号安全。

**Q: 如何确认服务正在工作？**
A: 可以查看服务状态和日志文件，或者在测试环境中连接后关机验证。

**Q: 服务支持哪些Windows版本？**
A: 支持Windows 7及以后的所有Windows版本。

## 许可证

本服务与主程序使用相同的许可证。

---

**版本**: 1.0
**更新日期**: 2026-03-18
**作者**: Kilo Code
