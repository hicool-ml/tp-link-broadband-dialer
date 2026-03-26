# TP-Link宽带拨号助手 - 关机清理解决方案

## 问题背景

之前使用Windows服务实现关机清理，但遇到**1053错误**：
- PyInstaller编译的exe作为服务无法启动
- 原因：Python + PyInstaller + Windows Service 兼容性问题

## 最终解决方案

### 架构设计

```
用户客户端 exe（填写账号）
        ↓
config.json（保存配置）
        ↓
cleanup_http.exe（纯HTTP清理程序）
        ↓
Windows 任务计划（关机触发）
```

### 核心组件

#### 1. cleanup_http.py
- 独立的清理程序
- 使用HTTP API与路由器通信
- 无需浏览器，启动快，稳定性高
- 打包为 `cleanup_http.exe`

#### 2. cleanup.ps1
- PowerShell包装脚本
- 任务计划程序的入口点
- 静默执行cleanup_http.exe

#### 3. Windows任务计划
- **任务名称**: TPLinkCleanup
- **触发条件**: 系统关机/重启事件（EventID 1074或6006）
- **运行权限**: SYSTEM（最高权限）
- **优点**:
  - ❌ 没有1053错误
  - ❌ 没有Session 0问题
  - ✔️ Windows原生机制，稳定性极高

## 文件清单

### 核心文件
| 文件 | 说明 |
|------|------|
| `cleanup_http.py` | 清理程序源码 |
| `cleanup.ps1` | PowerShell包装脚本 |
| `config_manager.py` | 配置管理器 |
| `tplink_http_cleaner.py` | HTTP清理器 |

### 编译文件
| 文件 | 说明 |
|------|------|
| `build_cleanup.spec` | PyInstaller配置 |
| `dist/cleanup_http.exe` | 编译后的清理程序 |

### 安装文件
| 文件 | 说明 |
|------|------|
| `install_task.py` | 任务计划创建脚本 |
| `setup_final.nsi` | NSIS安装脚本（UTF-8 with BOM） |

## 使用方法

### 1. 编译cleanup_http.exe
```bash
cd d:\13jiao\20260325
python -m PyInstaller --clean --noconfirm build_cleanup.spec
```

### 2. 创建任务计划
```bash
python install_task.py
```

### 3. 测试清理
```bash
# 手动运行
dist\cleanup_http.exe

# 或通过任务计划触发
schtasks /Run /TN TPLinkCleanup

# 查看日志
type C:\ProgramData\BroadbandDialer\cleanup.log
```

### 4. 集成到NSIS安装程序
```nsis
; 安装区段
Section "MainSection" SEC01
  SetOutPath "$INSTDIR"

  ; 复制文件
  File "broadband_dialer.exe"
  File /oname=cleanup_http.exe "dist\cleanup_http.exe"
  File "cleanup.ps1"

  ; 创建关机清理任务
  nsExec::ExecToLog 'schtasks /Delete /TN "TPLinkCleanup" /F'
  nsExec::ExecToLog 'schtasks /Create /TN "TPLinkCleanup" /TR "powershell.exe -ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File \"$INSTDIR\cleanup.ps1\"" /SC ONEVENT /EC System /MO "*[System[(EventID=1074 or EventID=6006)]]" /RU SYSTEM /RL HIGHEST /F'

SectionEnd

; 卸载区段
Section Uninstall
  ; 删除任务计划
  nsExec::ExecToLog 'schtasks /Delete /TN "TPLinkCleanup" /F'

  ; 删除文件
  Delete "$INSTDIR\cleanup_http.exe"
  Delete "$INSTDIR\cleanup.ps1"
SectionEnd
```

## 日志

### 日志位置
```
C:\ProgramData\BroadbandDialer\cleanup.log
```

### 日志内容
```
2026-03-25 16:25:27 - INFO - === 开始执行关机清理 ===
2026-03-25 16:25:27 - INFO - 路由器IP: 192.168.1.1
2026-03-25 16:25:27 - INFO - [SUCCESS] 登录成功
2026-03-25 16:25:27 - INFO - [OK] PPPoE 已断开
2026-03-25 16:25:28 - INFO - [OK] 账号密码已清空
2026-03-25 16:25:29 - INFO - [OK] 配置已保存
2026-03-25 16:25:30 - INFO - 清理成功
```

## 管理命令

```bash
# 查看任务
schtasks /Query /TN TPLinkCleanup /FO LIST

# 运行任务
schtasks /Run /TN TPLinkCleanup

# 删除任务
schtasks /Delete /TN TPLinkCleanup /F

# 查看日志
type C:\ProgramData\BroadbandDialer\cleanup.log
```

## 优势对比

| 方案 | 稳定性 | 复杂度 | 1053问题 | 推荐 |
|------|--------|--------|----------|------|
| Python Service | ❌ | ❌ | ❌ 有问题 | ❌ |
| PyInstaller EXE服务 | ❌ | ❌ | ❌ 必现 | ❌ |
| **任务计划方案** | ✅✅ | ✅ | ✅ 无问题 | ✅✅✅ |

## 关键注意事项

### 1. config.json 路径
建议统一使用：
```
C:\ProgramData\BroadbandDialer\config.json
```
SYSTEM用户也能访问。

### 2. cleanup_http.exe 不依赖相对路径
所有路径使用绝对路径。

### 3. NSIS脚本编码
**必须使用 UTF-8 with BOM** 编码！

### 4. 防火墙/网络延迟
设置超时为3秒：
```python
timeout=3
```

## 总结

通过使用**Windows任务计划**替代**Windows服务**，完全解决了1053错误问题：

- ✅ 稳定性极高
- ✅ 无兼容性问题
- ✅ 调试简单
- ✅ 体积更小
- ✅ 易于维护

**这是最佳的关机清理解决方案！**

---

*文档创建日期: 2026-03-25*
*版本: 2.2.0*
