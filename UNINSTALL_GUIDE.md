# 卸载功能说明

## 🎯 卸载功能概览

安装包包含完整的卸载程序，确保程序能够完全从系统中移除。

---

## 📋 卸载功能特性

### ✅ 自动化清理

卸载程序会自动执行以下操作：

1. **停止并卸载 Windows 服务**
   ```
   - 停止 TPLinkShutdownCleanup 服务
   - 调用 CleanupService.exe remove 卸载服务
   - 等待服务完全停止
   ```

2. **终止运行进程**
   ```
   - 终止 TP-Link_Dialer.exe
   - 终止 CleanupService.exe
   - 终止 ServiceInstaller.exe
   ```

3. **删除程序文件**
   ```
   - 删除整个安装目录: C:\Program Files\TPLinkDialer\
   - 删除所有子目录和文件
   ```

4. **删除快捷方式**
   ```
   - 删除桌面快捷方式
   - 删除开始菜单项
   ```

5. **清理注册表**
   ```
   - HKLM\Software\TPLinkDialer
   - HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\TPLinkDialer
   ```

### 🔒 用户数据保护

以下数据**不会被删除**：

- ✅ **配置文件**: `%USERPROFILE%\.tplink_dialer\config.json`
  - 包含路由器IP和管理密码
  - 重新安装时自动使用

- ✅ **服务日志**: `%TEMP%\tplink_cleanup\cleanup_service.log`
  - 便于问题排查

---

## 🚀 卸载方法

### 方法 1: 控制面板（推荐）

```
1. 打开"控制面板"
2. 点击"程序和功能"（或"卸载程序"）
3. 找到"Broadband Dial Tool"
4. 右键点击 → 选择"卸载"
5. 确认卸载
```

### 方法 2: 运行卸载程序

```
1. 打开安装目录: C:\Program Files\TPLinkDialer\
2. 双击运行: uninstall.exe
3. 确认卸载
```

### 方法 3: 命令行

```bash
# 静默卸载（无提示）
"C:\Program Files\TPLinkDialer\uninstall.exe" /S

# 正常卸载（有提示）
"C:\Program Files\TPLinkDialer\uninstall.exe"
```

---

## 📊 卸载流程详解

### 阶段 1: 确认

```
┌─────────────────────────────────┐
│  卸载确认对话框                  │
│                                 │
│  确定要卸载宽带拨号工具吗？      │
│                                 │
│  这将：                         │
│  ✓ 停止并移除清理服务           │
│  ✓ 删除所有程序文件             │
│  ✓ 移除快捷方式和注册表项       │
│                                 │
│  注意：您的路由器配置将被保留    │
│                                 │
│  [取消]          [确定]          │
└─────────────────────────────────┘
```

### 阶段 2: 执行

```
步骤 1/6: 停止清理服务
  → 执行: net stop TPLinkShutdownCleanup
  → 等待: 3 秒

步骤 2/6: 卸载 Windows 服务
  → 执行: CleanupService.exe remove
  → 等待: 2 秒

步骤 3/6: 终止运行进程
  → 执行: taskkill /F /IM TP-Link_Dialer.exe
  → 执行: taskkill /F /IM CleanupService.exe
  → 等待: 2 秒

步骤 4/6: 删除程序文件
  → 删除: C:\Program Files\TPLinkDialer\

步骤 5/6: 删除快捷方式
  → 删除: 桌面快捷方式
  → 删除: 开始菜单项

步骤 6/6: 清理注册表
  → 删除: HKLM\Software\TPLinkDialer
  → 删除: 卸载信息
```

### 阶段 3: 完成

```
┌─────────────────────────────────┐
│  卸载完成                       │
│                                 │
│  宽带拨号工具已成功卸载！        │
│                                 │
│  已删除：                       │
│  ✓ 程序文件和清理服务           │
│  ✓ 桌面和开始菜单快捷方式       │
│  ✓ 注册表项                     │
│                                 │
│  已保留：                       │
│  ✓ 配置文件:                    │
│    %USERPROFILE%\.tplink_dialer\ │
│    \config.json                 │
│  ✓ 服务日志:                    │
│    %TEMP%\tplink_cleanup\       │
│                                 │
│  [确定]                          │
└─────────────────────────────────┘
```

---

## ⚠️ 注意事项

### 卸载前

1. **保存重要数据**
   - 虽然配置文件会保留，但建议手动备份

2. **关闭程序**
   - 关闭正在运行的宽带拨号工具
   - 虽然卸载程序会自动关闭，但手动关闭更安全

3. **管理员权限**
   - 卸载需要管理员权限
   - 系统会提示 UAC 对话框

### 卸载中

1. **不要中断**
   - 卸载过程中不要关闭计算机
   - 等待卸载完成

2. **查看日志**
   - 卸载日志会显示详细进度
   - 如有错误会显示在日志中

### 卸载后

1. **验证清理**
   - 检查安装目录是否已删除
   - 检查服务是否已卸载
   - 检查快捷方式是否已删除

2. **保留配置**
   - 配置文件保留在用户目录
   - 重新安装时无需重新配置

3. **删除残留文件（可选）**
   ```
   # 如需彻底删除配置文件
   rmdir /s "%USERPROFILE%\.tplink_dialer"

   # 如需彻底删除日志
   rmdir /s "%TEMP%\tplink_cleanup"
   ```

---

## 🔧 故障排除

### 问题 1: 卸载程序无法运行

**原因**: 缺少管理员权限

**解决**:
```
右键 uninstall.exe → 以管理员身份运行
```

### 问题 2: 服务无法停止

**原因**: 服务正在执行清理操作

**解决**:
```
手动停止服务:
net stop TPLinkShutdownCleanup

然后重新运行卸载程序
```

### 问题 3: 文件无法删除

**原因**: 文件被占用或权限不足

**解决**:
```
1. 重启计算机
2. 以管理员身份运行卸载程序
3. 或手动删除安装目录
```

### 问题 4: 注册表残留

**原因**: 卸载程序被中断

**解决**:
```
手动删除注册表项:
reg delete "HKLM\Software\TPLinkDialer" /f
reg delete "HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\TPLinkDialer" /f
```

---

## 📋 完整卸载验证

### 验证清单

卸载完成后，验证以下内容：

#### 文件系统
- [ ] `C:\Program Files\TPLinkDialer\` 已删除
- [ ] 桌面快捷方式已删除
- [ ] 开始菜单项已删除

#### Windows 服务
- [ ] `TPLinkShutdownCleanup` 服务已停止
- [ ] `TPLinkShutdownCleanup` 服务已卸载
  ```bash
  sc query TPLinkShutdownCleanup
  # 应显示: "指定的服务未安装"
  ```

#### 注册表
- [ ] `HKLM\Software\TPLinkDialer` 已删除
- [ ] `HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\TPLinkDialer` 已删除

#### 进程
- [ ] `TP-Link_Dialer.exe` 未运行
- [ ] `CleanupService.exe` 未运行
- [ ] `ServiceInstaller.exe` 未运行

#### 用户数据（应保留）
- [ ] `%USERPROFILE%\.tplink_dialer\config.json` 存在
- [ ] `%TEMP%\tplink_cleanup\cleanup_service.log` 存在

---

## 🎯 技术细节

### NSIS 卸载脚本特点

1. **详细的进度显示**
   - 每个步骤都有详细日志
   - 用户可以看到卸载进度

2. **完善的错误处理**
   - 服务停止失败时等待并重试
   - 文件删除失败时显示警告

3. **进程终止机制**
   - 使用 taskkill /F 强制终止
   - 确保所有进程都已停止

4. **用户数据保护**
   - 明确说明哪些数据会保留
   - 避免用户数据丢失

5. **分步卸载流程**
   - 清晰的6步卸载流程
   - 每步都有独立的验证

---

**版本**: 2.1
**更新日期**: 2026-03-19
**作者**: Kilo Code
