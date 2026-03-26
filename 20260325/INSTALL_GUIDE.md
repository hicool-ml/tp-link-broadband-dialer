# TP-Link宽带拨号助手 v2.2.0 - 安装指南

## 📦 安装包信息

**文件名**: `Broadband_Dialer_Setup_2.2.0.exe`
**大小**: 31 MB
**版本**: 2.2.0
**发布日期**: 2026-03-25

---

## ✨ 新功能

### 🔥 关机自动清理（重要更新！）
- ✅ **无需Windows服务**，使用任务计划实现
- ✅ **完全解决1053错误**问题
- ✅ **系统级权限**，关机时自动执行
- ✅ **纯HTTP API**，无需浏览器，速度快
- ✅ **稳定性极高**，原生Windows机制

---

## 🚀 一键安装

### 方法1：双击安装（推荐）
1. 右键 `Broadband_Dialer_Setup_2.2.0.exe`
2. 选择 **"以管理员身份运行"**
3. 点击 **"下一步"** → **"安装"** → **"完成"**
4. ✅ 安装完成！桌面会有快捷方式

### 方法2：命令行安装
```cmd
Broadband_Dialer_Setup_2.2.0.exe /S /D=C:\Program Files\Broadband_Dialer
```

---

## 📋 安装内容

### 程序文件
| 文件 | 说明 |
|------|------|
| `broadband_dialer.exe` | 主程序（宽带拨号助手） |
| `cleanup_http.exe` | 关机清理程序（后台自动运行） |
| `cleanup.ps1` | PowerShell包装脚本 |

### 自动创建
- ✅ 桌面快捷方式
- ✅ 开始菜单项
- ✅ **Windows任务计划** `TPLinkCleanup`
- ✅ 日志目录 `C:\ProgramData\BroadbandDialer`

### 注册表
```
HKLM\Software\Broadband_Dialer
HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\TP-Link宽带拨号助手
```

---

## 🎯 使用方法

### 1. 首次使用
1. 双击桌面 **"宽带拨号助手"** 快捷方式
2. 填写路由器IP地址（默认：192.168.1.1）
3. 填写路由器管理员密码
4. 点击 **"连接"** 按钮
5. ✅ 完成！程序会自动保存配置

### 2. 关机自动清理（新功能）
- **无需任何操作**！关机时自动执行
- 清理内容：
  - ✅ 断开PPPoE连接
  - ✅ 清空宽带账号密码
  - ✅ 保存配置到路由器

### 3. 手动清理（可选）
```cmd
# 方法1：通过任务计划
schtasks /Run /TN "TPLinkCleanup"

# 方法2：直接运行
"C:\Program Files\Broadband_Dialer\cleanup_http.exe"
```

---

## 📊 验证安装

### 检查任务计划
```cmd
schtasks /Query /TN "TPLinkCleanup" /FO LIST
```

应该显示：
```
任务名:           TPLinkCleanup
触发器:          事件日志触发
系统:            SYSTEM
```

### 查看日志
```cmd
type "C:\ProgramData\BroadbandDialer\cleanup.log"
```

### 测试关机清理
```cmd
schtasks /Run /TN "TPLinkCleanup"
```

然后检查日志，应该看到：
```
2026-03-25 xx:xx:xx - INFO - === 开始执行关机清理 ===
2026-03-25 xx:xx:xx - INFO - 路由器IP: 192.168.1.1
2026-03-25 xx:xx:xx - INFO - [SUCCESS] 登录成功
2026-03-25 xx:xx:xx - INFO - ✅ PPPoE 已断开
2026-03-25 xx:xx:xx - INFO - ✅ 账号密码已清空
2026-03-25 xx:xx:xx - INFO - ✅ 配置已保存
2026-03-25 xx:xx:xx - INFO - 清理成功
```

---

## 🗑️ 卸载

### 方法1：控制面板
1. 打开 **"控制面板"** → **"程序和功能"**
2. 找到 **"TP-Link宽带拨号助手"**
3. 点击 **"卸载"**

### 方法2：通过安装目录
1. 进入 `C:\Program Files\Broadband_Dialer`
2. 双击 `uninstall.exe`

### 方法3：命令行
```cmd
"C:\Program Files\Broadband_Dialer\uninstall.exe" /S
```

### 卸载会自动清理
- ✅ 删除任务计划 `TPLinkCleanup`
- ✅ 删除程序文件
- ✅ 删除快捷方式
- ✅ 删除注册表项
- ✅ **保留日志文件**（用于调试）

---

## 🔧 故障排除

### 问题1：安装失败
**原因**: 没有管理员权限
**解决**: 右键安装程序，选择"以管理员身份运行"

### 问题2：任务计划未创建
**检查**:
```cmd
schtasks /Query /TN "TPLinkCleanup"
```

**手动创建**:
```cmd
schtasks /Create /TN "TPLinkCleanup" /TR "powershell.exe -ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File \"C:\Program Files\Broadband_Dialer\cleanup.ps1\"" /SC ONEVENT /EC System /MO "*[System[(EventID=1074 or EventID=6006)]]" /RU SYSTEM /RL HIGHEST /F
```

### 问题3：关机清理不工作
**检查1**: 任务是否存在
```cmd
schtasks /Query /TN "TPLinkCleanup"
```

**检查2**: 手动运行测试
```cmd
schtasks /Run /TN "TPLinkCleanup"
```

**检查3**: 查看日志
```cmd
type "C:\ProgramData\BroadbandDialer\cleanup.log"
```

### 问题4：找不到配置文件
主程序配置位置：
```
C:\Users\你的用户名\AppData\Local\Broadband_Dialer\config.json
```

如果重装系统，建议备份此文件。

---

## 📌 注意事项

### ⚠️ 重要
1. **必须以管理员身份运行安装程序**
2. **首次使用需要配置路由器信息**
3. **关机清理需要10-15秒**，请耐心等待
4. **确保路由器密码正确**，否则清理失败

### ✅ 优势
- ❌ **无需Windows服务**（避免1053错误）
- ✅ **任务计划原生支持**（稳定性高）
- ✅ **SYSTEM权限运行**（最高权限）
- ✅ **无浏览器依赖**（纯HTTP API）
- ✅ **日志完整**（便于调试）

---

## 📞 技术支持

### 日志位置
```
C:\ProgramData\BroadbandDialer\cleanup.log
```

### 常用命令
```cmd
# 查看任务详情
schtasks /Query /TN "TPLinkCleanup" /FO LIST

# 立即执行清理
schtasks /Run /TN "TPLinkCleanup"

# 删除任务
schtasks /Delete /TN "TPLinkCleanup" /F

# 查看日志
type "C:\ProgramData\BroadbandDialer\cleanup.log"
```

### 系统要求
- Windows 10/11（推荐）
- Windows Server 2016+
- 管理员权限

---

## 🎉 更新日志

### v2.2.0 (2026-03-25)
- 🔥 **重大更新**：使用任务计划替代Windows服务
- ✅ 完全解决1053错误问题
- ✅ 关机清理稳定性大幅提升
- ✅ 无需浏览器，使用HTTP API
- ✅ 一键安装，自动配置

### v2.1.1 (2025-03-20)
- 修复设置对话框保存按钮问题
- 修复MAC模式逻辑错误

### v2.1 (2025-03-xx)
- 初始发布版本

---

**祝您使用愉快！** 🎊

*Kilo Code*
*https://github.com/kilocode*
