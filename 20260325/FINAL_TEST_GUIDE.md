# 🔧 GPO关机脚本 - 最终测试指南

## ✅ 方案简化

根据用户要求：
- ✅ **只支持关机和重启**
- ❌ 不支持注销
- ✅ 使用PowerShell（微软官方推荐）
- ✅ GPO机制（企业级可靠）

---

## 📋 当前系统状态

### **已完成的配置**
```powershell
# GPO注册表（关机脚本）
Script: powershell.exe
Parameters: -ExecutionPolicy Bypass -File "C:\Program Files (x86)\Broadband_Dialer\cleanup.ps1"
IsPowershell: 1

# 日志文件分离
cleanup.ps1 → cleanup.log (PowerShell日志)
cleanup_http.exe → cleanup_http.log (Python程序日志)
```

### **已刷新组策略**
```cmd
gpupdate /Force  ✅ 已执行
```

---

## 🚨 关键提示

### **GPO脚本更改需要重启才能生效！**

即使注册表已配置、组策略已刷新，**Windows仍然需要重启后才会执行新的GPO关机脚本**。

这是Windows GPO机制的**设计特性**，不是bug。

---

## 🧪 测试步骤

### **步骤1：清空日志**
```cmd
echo. > "C:\ProgramData\BroadbandDialer\cleanup.log"
if exist "C:\ProgramData\BroadbandDialer\cleanup_http.log" del "C:\ProgramData\BroadbandDialer\cleanup_http.log"
```

### **步骤2：重启计算机**
```cmd
shutdown /r /t 0
```

**⚠️ 注意：必须重启，不能只注销！**

### **步骤3：重新登录后检查日志**
```cmd
type "C:\ProgramData\BroadbandDialer\cleanup.log"
type "C:\ProgramData\BroadbandDialer\cleanup_http.log"
```

### **步骤4：验证路由器状态**
- 访问 http://192.168.1.1
- 检查PPPoE连接是否断开
- 检查账号密码是否清空

---

## 📊 预期结果

### **cleanup.log（PowerShell脚本）**
```
2026-03-26 14:30:15 - === Shutdown cleanup triggered ===
2026-03-26 14:30:15 - Script location: C:\Program Files (x86)\Broadband_Dialer\cleanup.ps1
2026-03-26 14:30:15 - Base directory: C:\Program Files (x86)\Broadband_Dialer
2026-03-26 14:30:15 - Looking for exe: C:\Program Files (x86)\Broadband_Dialer\cleanup_http.exe
2026-03-26 14:30:15 - ✅ Found cleanup_http.exe, starting...
2026-03-26 14:30:26 - ✅ cleanup_http.exe finished
```

### **cleanup_http.log（Python程序）**
```
2026-03-26 14:30:15,123 - INFO - === 开始执行关机清理 ===
2026-03-26 14:30:15,234 - INFO - 路由器IP: 192.168.1.1
2026-03-26 14:30:15,234 - INFO - ============================================================
2026-03-26 14:30:15,234 - INFO - 开始执行路由器账号清理...
2026-03-26 14:30:15,234 - INFO - ============================================================
2026-03-26 14:30:15,345 - INFO - [INFO] 正在登录路由器...
2026-03-26 14:30:16,456 - INFO - [INFO] 登录成功，stok=...
2026-03-26 14:30:16,567 - INFO - 🔌 正在断开 PPPoE 连接...
2026-03-26 14:30:16,789 - INFO - ✅ PPPoE 已断开
2026-03-26 14:30:17,901 - INFO - 🗑️ 正在清空账号密码...
2026-03-26 14:30:18,012 - INFO - ✅ 账号密码已清空
2026-03-26 14:30:19,123 - INFO - 💾 正在保存配置...
2026-03-26 14:30:19,345 - INFO - ✅ 配置已保存
2026-03-26 14:30:20,456 - INFO - ============================================================
2026-03-26 14:30:20,456 - INFO - ✅ 清理完成！
2026-03-26 14:30:20,456 - INFO - ============================================================
```

### **路由器状态**
- ✅ PPPoE连接已断开
- ✅ 账号密码已清空
- ✅ 路由器无法拨号

---

## 🔍 验证GPO注册

### **检查注册表**
```cmd
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Shutdown\0" /s
```

### **预期输出**
```
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Shutdown\0
    DisplayName    REG_SZ    Broadband Dialer Cleanup
    List    REG_MULTI_SZ    0\0
    FileSysPath    REG_SZ    C:\Program Files (x86)\Broadband_Dialer

    HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Shutdown\0\0
        ExecTime    REG_BINARY    0000000000000000
        IsPowershell    REG_DWORD    0x1
        Parameters    REG_SZ    -ExecutionPolicy Bypass -File "C:\Program Files (x86)\Broadband_Dialer\cleanup.ps1"
        Script    REG_SZ    powershell.exe
```

---

## ❓ 如果仍然没有日志

### **可能原因**

1. **需要重启才能生效**
   - GPO脚本更改后必须重启
   - 注销不够，必须是重启或关机

2. **路由器连接问题**
   - 路由器IP不正确
   - 网络未连接
   - 路由器未开机

3. **config.json配置问题**
   - 检查 `C:\Program Files (x86)\Broadband_Dialer\config.json`
   - 确认router_ip和router_password正确

### **调试方法**

1. **手动测试cleanup.ps1**
   ```cmd
   powershell -ExecutionPolicy Bypass -File "C:\Program Files (x86)\Broadband_Dialer\cleanup.ps1"
   ```

2. **手动测试cleanup_http.exe**
   ```cmd
   "C:\Program Files (x86)\Broadband_Dialer\cleanup_http.exe"
   ```

3. **检查Windows事件日志**
   - 打开"事件查看器"
   - 查看"Windows日志" → "系统"
   - 搜索"Group Policy"或"脚本"

---

## 📦 新安装程序

```
文件名: Broadband_Dialer_Setup_2.2.0.exe
大小: 32 MB
包含文件:
  - broadband_dialer.exe
  - cleanup_http.exe (使用cleanup_http.log)
  - cleanup.ps1 (使用cleanup.log)

GPO注册:
  - Shutdown脚本 → cleanup.ps1 → cleanup_http.exe
  - 无Logoff脚本
  - 完整的Scripts和State注册表
```

---

## 🎯 总结

### **当前方案**
- ✅ GPO关机脚本（企业级可靠）
- ✅ 只支持关机和重启
- ✅ 使用PowerShell（微软官方推荐）
- ✅ 日志文件分离（无冲突）

### **下一步**
1. **重启计算机**（必须！）
2. **检查日志**
3. **验证路由器状态**

### **关键点**
⚠️ **GPO脚本更改必须重启后才会生效！**

---

**🔧 最终稳定版准备就绪！**

*版本: 2.2.0 Final*
*方案: GPO Shutdown Script (PowerShell)*
*范围: 关机 + 重启*
*状态: 已配置，等待重启测试*
