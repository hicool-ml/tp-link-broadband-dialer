# ✅ TP-Link Broadband Dialer v2.2.0 - 正式发布

## 🎉 **重要更新**

### 🔥 **修复关机清理机制**
- ❌ **移除**: 任务计划ONEVENT触发（不可靠）
- ✅ **采用**: GPO关机脚本机制（⭐⭐⭐⭐⭐）

### 📦 **发布包**
```
文件名: TP-Link_Broadband_Dialer_v2.2.0_GPO.zip
大小: 31 MB
状态: ✅ 正式发布
```

---

## ✨ **核心功能**

### **主程序**
- ✅ PPPoE自动拨号
- ✅ MAC地址设置
- ✅ 系统托盘图标
- ✅ 等待时间优化（10秒）

### **关机清理**（重要！）
- ✅ **关机时自动清除账号**
- ✅ **重启时自动清除账号**
- ✅ 使用GPO机制（真正可靠）

---

## 🎯 **技术改进**

### **方案对比**
| 特性 | 旧方案（任务计划） | 新方案（GPO） |
|------|------------------|--------------|
| 触发时机 | ❌ 太晚 | ✅ 关机早期 |
| 执行可靠性 | ❌ 不稳定 | ✅⭐⭐⭐⭐⭐ |
| 系统保证 | ❌ 无 | ✅ 有保证 |

### **代码改进**
```powershell
# cleanup.ps1
$exe = Join-Path $PSScriptRoot "cleanup_http.exe"
Start-Process $exe -WindowStyle Hidden -Wait
```

```nsi
; NSI 安装脚本
WriteRegStr HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Shutdown\0\0" "Script" "powershell.exe"
WriteRegStr HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Shutdown\0\0" "Parameters" '-ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File "$INSTDIR\cleanup.ps1"'
```

---

## 📋 **使用说明**

### **1. 安装**
```
1. 解压 TP-Link_Broadband_Dialer_v2.2.0_GPO.zip
2. 右键 Broadband_Dialer_Setup_2.2.0.exe
3. 选择"以管理员身份运行"
4. 点击"完成"时勾选"运行宽带拨号助手"
```

### **2. 验证GPO注册**
```cmd
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Shutdown"
```

### **3. 测试关机清理**
```cmd
shutdown /s /t 0
# 重新开机后检查日志
type "C:\ProgramData\BroadbandDialer\cleanup.log"
```

---

## 📊 **版本历史**

### v2.2.0 (2026-03-26) - GPO版本
- 🔥 重大修复：使用GPO关机脚本机制
- ✅ 修复cleanup.ps1路径问题
- ✅ 添加安装后运行选项
- ✅ 等待时间优化为10秒
- ✅ 桌面快捷方式：宽带连接

### v2.1.1 (2025-03-20)
- ✅ 修复设置对话框问题
- ✅ 修复MAC模式逻辑

---

## 🚀 **安装后结构**

```
C:\Program Files\Broadband_Dialer\
├── broadband_dialer.exe       (主程序)
├── cleanup_http.exe            (清理程序)
├── cleanup.ps1                 (关机脚本)
└── uninstall.exe               (卸载程序)

桌面快捷方式:
└── 宽带连接.lnk

注册表:
└── HKLM\...\Group Policy\Scripts\Shutdown\0\0
    ├── Script: powershell.exe
    └── Parameters: -ExecutionPolicy Bypass...
```

---

## ✅ **质量保证**

### 测试状态
- ✅ GPO脚本注册成功
- ✅ 编译无警告
- ✅ 功能测试通过
- ✅ 卸载测试通过
- ✅ 关机清理验证通过

### 文档完整性
- ✅ README.txt
- ✅ CHANGELOG.md
- ✅ VERSION.txt
- ✅ GPO_VERSION.md

---

## 📞 **技术支持**

### 日志位置
```
C:\ProgramData\BroadbandDialer\cleanup.log
```

### 常用命令
```cmd
; 查看GPO注册
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Shutdown"

; 强制更新GPO
gpupdate /force

; 查看日志
type "C:\ProgramData\BroadbandDialer\cleanup.log"
```

---

## 🎉 **发布就绪**

```
版本: 2.2.0 (GPO)
状态: ✅ 正式发布
文件: TP-Link_Broadband_Dialer_v2.2.0_GPO.zip
大小: 31 MB
```

---

**✅ 所有问题已修复，使用GPO机制更加可靠！**

*制作: Hicool & CMCC*
*日期: 2026-03-26*
*版本: 2.2.0 (GPO)*
