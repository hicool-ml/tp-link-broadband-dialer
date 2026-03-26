# 🎉 TP-Link Broadband Dialer v2.2.0 - 发布包

## 📦 发布信息

```
文件名: TP-Link_Broadband_Dialer_v2.2.0_20260325.zip
大小: 31 MB
发布日期: 2026-03-25
版本: 2.2.0
版权: Hicool & CMCC
状态: ✅ 正式发布
```

---

## 📋 包含文件

### ✅ 安装程序
```
Broadband_Dialer_Setup_2.2.0.exe (31 MB)
一键安装，包含所有功能
```

### ✅ 说明文档
```
README.txt - 安装使用说明（中文）
CHANGELOG.md - 版本更新日志（Markdown）
VERSION.txt - 版本信息
```

---

## 🚀 快速开始

### 1. 解压文件
```
TP-Link_Broadband_Dialer_v2.2.0_20260325.zip
└── Broadband_Dialer_Setup_2.2.0.exe
```

### 2. 安装程序
```
右键 → 以管理员身份运行
```

### 3. 桌面快捷方式
```
宽带连接.lnk
```

---

## ✨ 核心功能

### 主程序
- ✅ PPPoE自动拨号
- ✅ MAC地址设置
- ✅ 系统托盘图标
- ✅ 连接状态显示
- ✅ 配置自动保存

### 自动清理（重要）
- ✅ **关机时清除账号**
- ✅ **重启时清除账号**
- ✅ **注销时清除账号**
- ✅ 使用任务计划实现
- ✅ 完全避免1053错误

---

## 🎯 技术亮点

### 稳定性
```
✅ 任务计划（替代Windows服务）
✅ 无1053错误
✅ 纯HTTP API（无需浏览器）
✅ SYSTEM权限运行
```

### 用户体验
```
✅ 桌面快捷方式: 宽带连接
✅ 等待时间: 10秒（优化）
✅ 一键安装
✅ 完整卸载
```

### 安全性
```
✅ 关机/重启/注销自动清除
✅ 密码加密存储
✅ 日志完整记录
✅ 配置文件保护
```

---

## 📊 版本对比

| 特性 | v2.1.1 | v2.2.0 |
|------|--------|--------|
| 服务方式 | Windows服务 | 任务计划 ✅ |
| 1053错误 | ❌ 有问题 | ✅ 完全解决 |
| 清除触发 | 关机/重启 | 关机/重启/注销 ✅ |
| 等待时间 | 15秒 | 10秒 ✅ |
| 快捷方式 | 宽带拨号助手 | 宽带连接 ✅ |
| 卸载功能 | 不完整 | 完整清理 ✅ |

---

## 🔧 系统要求

### 最低要求
```
操作系统: Windows 10 (64位)
内存: 2GB RAM
磁盘: 100MB 可用空间
权限: 管理员权限
```

### 推荐配置
```
操作系统: Windows 11 (64位)
内存: 4GB RAM
路由器: TP-Link
网络: 稳定连接
```

---

## 📝 安装后结构

```
C:\Program Files\Broadband_Dialer\
├── broadband_dialer.exe       (主程序)
├── cleanup_http.exe            (清理程序)
├── cleanup.ps1                 (PowerShell脚本)
└── uninstall.exe               (卸载程序)

桌面快捷方式:
└── 宽带连接.lnk

开始菜单:
└── Broadband_Dialer\
    └── Broadband Dialer.lnk

任务计划:
├── TPLinkCleanup (关机/重启)
└── TPLinkCleanupLogoff (注销)

日志目录:
└── C:\ProgramData\BroadbandDialer\
    └── cleanup.log
```

---

## 🎯 使用流程

### 首次使用
```
1. 双击"宽带连接"
2. 配置路由器IP和密码
3. 填写宽带账号密码
4. 点击"连接"
5. 等待10秒连接成功
```

### 后续使用
```
1. 双击"宽带连接"
2. 自动填写上次账号
3. 点击"连接"
4. 完成！
```

### 自动清理
```
- 关机时自动清除（无需操作）
- 重启时自动清除（无需操作）
- 注销时自动清除（无需操作）
```

---

## 📞 技术支持

### 日志位置
```
C:\ProgramData\BroadbandDialer\cleanup.log
```

### 常用命令
```cmd
; 查看任务
schtasks /Query /TN "TPLinkCleanup"

; 手动触发
schtasks /Run /TN "TPLinkCleanup"

; 查看日志
type "C:\ProgramData\BroadbandDialer\cleanup.log"
```

### 卸载
```cmd
控制面板 → 程序和功能 → TP-Link Broadband Dialer → 卸载
```

---

## ✅ 质量保证

### 测试状态
- ✅ 编译成功（无警告）
- ✅ 功能测试通过
- ✅ 安装测试通过
- ✅ 卸载测试通过
- ✅ 任务计划测试通过

### 文档完整性
- ✅ README.txt
- ✅ CHANGELOG.md
- ✅ VERSION.txt
- ✅ 本文档

---

## 🚀 发布就绪

```
版本: 2.2.0
状态: ✅ RELEASE READY
文件: TP-Link_Broadband_Dialer_v2.2.0_20260325.zip
大小: 31 MB
```

---

## 📋 发布清单

- [x] 主程序编译成功
- [x] 清理程序编译成功
- [x] 安装程序编译成功
- [x] 功能测试通过
- [x] 文档完整
- [x] 打包完成
- [x] 无重大bug
- [x] 卸载功能完善

---

**🎉 TP-Link Broadband Dialer v2.2.0 正式发布！**

*制作: Hicool & CMCC*
*日期: 2026-03-25*
*版本: 2.2.0*
