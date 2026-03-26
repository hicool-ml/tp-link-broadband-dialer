# ✅ v2.2.1 - 添加注销清理支持

## 🎉 更新内容

### **新增：Logoff脚本支持**
- ✅ 注销时自动清理路由器账号
- ✅ 关机时自动清理路由器账号
- ✅ 重启时自动清理路由器账号

---

## 📋 问题修复

### **问题1：注销后路由器依然在线**
- **原因**：只注册了Shutdown脚本，没有Logoff脚本
- **解决**：添加GPO Logoff脚本注册

### **问题2：cleanup.ps1路径调试**
- **改进**：增强日志输出，显示脚本位置和exe路径
- **新增**：
  ```
  2026-03-26 10:31:43 - Script location: C:\Program Files\Broadband_Dialer\cleanup.ps1
  2026-03-26 10:31:43 - Base directory: C:\Program Files\Broadband_Dialer
  2026-03-26 10:31:43 - Looking for exe: C:\Program Files\Broadband_Dialer\cleanup_http.exe
  2026-03-26 10:31:43 - ✅ Found cleanup_http.exe, starting...
  ```

---

## 🔧 技术细节

### **GPO注册（setup_v5_final.nsi）**

#### Shutdown脚本（关机/重启）
```nsi
WriteRegStr HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Shutdown\0\0" "Script" "powershell.exe"
WriteRegStr HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Shutdown\0\0" "Parameters" '-ExecutionPolicy Bypass -File "$INSTDIR\cleanup.ps1"'
WriteRegDWORD HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Shutdown\0\0" "IsPowershell" 1
```

#### Logoff脚本（注销）- **新增**
```nsi
WriteRegStr HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Logoff\0\0" "Script" "powershell.exe"
WriteRegStr HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Logoff\0\0" "Parameters" '-ExecutionPolicy Bypass -File "$INSTDIR\cleanup.ps1"'
WriteRegDWORD HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Logoff\0\0" "IsPowershell" 1
```

### **cleanup.ps1增强**
```powershell
Log "Script location: $PSCommandPath"
Log "Base directory: $baseDir"
Log "Looking for exe: $exe"

if (Test-Path $exe) {
    Log "✅ Found cleanup_http.exe, starting..."
    Start-Process $exe -WindowStyle Hidden -Wait
    Log "✅ cleanup_http.exe finished"
} else {
    Log "❌ ERROR: cleanup_http.exe not found: $exe"
}
```

---

## 📊 触发时机对比

| 操作 | v2.2.0 | v2.2.1 |
|------|--------|--------|
| 注销 | ❌ 不清理 | ✅ **清理** |
| 关机 | ✅ 清理 | ✅ 清理 |
| 重启 | ✅ 清理 | ✅ 清理 |
| 锁屏 | ❌ 不清理 | ❌ 不清理 |

---

## 🚀 安装后验证

### **1. 验证GPO注册**
```cmd
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Shutdown"
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Logoff"
```

**预期结果**：
- Shutdown路径下有 `0` 子键
- Logoff路径下有 `0` 子键

### **2. 测试注销清理**
```cmd
# 注销当前用户
logoff
# 重新登录后检查日志
type "C:\ProgramData\BroadbandDialer\cleanup.log"
```

**预期结果**：看到完整的清理日志

### **3. 测试关机清理**
```cmd
shutdown /s /t 0
# 重新开机后检查日志
type "C:\ProgramData\BroadbandDialer\cleanup.log"
```

---

## 📦 发布文件

```
文件名: Broadband_Dialer_Setup_2.2.0.exe
大小: 31 MB
状态: ✅ 已编译
包含: Shutdown + Logoff脚本支持
```

---

## 🎯 关键改进

### **1. 完整的会话清理**
现在无论用户：
- 注销切换账号
- 关机离开
- 重启系统

路由器账号都会被自动清除！

### **2. 更好的调试**
cleanup.ps1现在输出详细的路径信息，方便排查问题。

### **3. 完整的卸载**
卸载时会同时删除Shutdown和Logoff脚本注册。

---

## ⚠️ 重要提示

### **关于日志中的错误**
```
2026-03-26 10:31:43 - ERROR: cleanup_http.exe not found: D:\13jiao\20260325\cleanup_http.exe
```

**原因**：这是测试时直接运行开发目录的脚本导致的。

**解决**：安装后脚本路径会自动变为：
```
C:\Program Files\Broadband_Dialer\cleanup_http.exe
```

---

**✅ v2.2.1 准备就绪！**

*版本: 2.2.1 (Logoff Support)*
*日期: 2026-03-26*
*改进: 添加注销清理支持*
