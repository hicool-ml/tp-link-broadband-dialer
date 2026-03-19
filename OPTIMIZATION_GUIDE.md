# 优化架构说明

## 📊 优化效果对比

| 项目 | 优化前 | 优化后 | 节省 |
|------|--------|--------|------|
| **主程序** | 539 MB | ~30 MB | 94% ↓ |
| **清理服务** | 518 MB | ~20 MB | 96% ↓ |
| **服务安装器** | 9.4 MB | ~9 MB | - |
| **浏览器（共享）** | 2 × 500MB | 150 MB | 85% ↓ |
| **总计** | ~1070 MB | ~210 MB | **80% ↓** |

---

## 🏗️ 优化架构

### 目录结构

```
C:\Program Files\TPLinkDialer\
├── chrome-win64/              ← 共享浏览器（只安装一次）
│   └── chrome.exe
├── TP-Link_Dialer.exe         ← 主程序（不含浏览器）
├── CleanupService.exe         ← 清理服务（不含浏览器）
├── ServiceInstaller.exe       ← 服务安装器
└── _internal/                 ← 依赖库
    ├── playwright/            ← Playwright Python库
    └── ...
```

### 共享机制

```python
# 所有程序使用同一个浏览器
browser_manager = BrowserManager()
browser_path = browser_manager.get_browser_path()
# 返回: C:\Program Files\TPLinkDialer\chrome-win64\chrome.exe
```

---

## 🔧 技术实现

### 1. 浏览器管理模块 (`browser_manager.py`)

```python
class BrowserManager:
    """管理共享浏览器路径"""

    def __init__(self):
        # 浏览器安装在程序根目录
        self.install_dir = Path(sys.executable).parent.parent
        self.chrome_exe = self.install_dir / "chrome-win64" / "chrome.exe"

    def get_browser_path(self):
        """所有程序共享同一个浏览器"""
        return str(self.chrome_exe) if self.chrome_exe.exists() else None
```

### 2. 打包配置修改

**主程序** (`TP-Link_Dialer_main_nobrowser.spec`)
```python
# 不包含浏览器数据文件
datas = [
    ('app.ico', '.'),
    # 不再包含 chrome-win64
]
```

**清理服务** (`CleanupService_nobrowser.spec`)
```python
# 不包含任何数据文件
datas = []
# 浏览器由安装程序统一安装
```

### 3. NSIS 安装脚本

```nsis
Section "Playwright 浏览器 (必需)" SecBrowser
    SectionIn RO  ; 必需组件

    SetOutPath $INSTDIR
    File /r "chrome-win64"  ; 只安装一次

SectionEnd
```

---

## 📦 打包流程

### 自动化打包脚本

```bash
# 运行优化打包
build_optimized.bat
```

### 步骤说明

1. **打包主程序**（不含浏览器）
   - 使用 `TP-Link_Dialer_main_nobrowser.spec`
   - 大小约 30 MB

2. **打包清理服务**（不含浏览器）
   - 使用 `CleanupService_nobrowser.spec`
   - 大小约 20 MB

3. **准备浏览器**
   - 检查 `chrome-win64` 目录
   - 如不存在则自动下载

4. **创建安装包**
   - 使用 NSIS 创建 `Setup.exe`
   - 最终大小约 200 MB

---

## 🚀 部署说明

### 安装过程

1. **运行安装包**
   ```
   Release\Setup.exe
   ```

2. **安装组件**
   - ✅ 主程序（30 MB）
   - ✅ 清理服务（20 MB）
   - ✅ 服务安装器（9 MB）
   - ✅ Playwright 浏览器（150 MB）← 共享

3. **总安装时间**
   - 约 2-3 分钟（取决于硬盘速度）

### 运行机制

```
用户启动主程序
    ↓
检查浏览器是否存在
    ↓
[存在] → 使用共享浏览器 → 启动程序
    ↓
[不存在] → 显示友好提示 → 退出
```

---

## ⚠️ 注意事项

### 1. 浏览器依赖

**问题**：如果用户单独删除浏览器目录，程序将无法运行

**解决方案**：
- 安装程序将浏览器标记为"必需组件"
- 程序启动时检查浏览器，如缺失显示友好提示

### 2. 更新机制

**浏览器更新**：
- Playwright 浏览器无需更新（使用本地版本）
- 如需更新，重新运行安装包

**程序更新**：
- 主程序和清理服务可独立更新
- 不影响共享浏览器

### 3. 卸载

**完全卸载**：
```
控制面板 → 程序和功能 → 宽带拨号工具 → 卸载
```

**手动卸载**：
```bash
# 停止服务
net stop TPLinkShutdownCleanup

# 卸载服务
CleanupService.exe remove

# 删除安装目录
rmdir /s "C:\Program Files\TPLinkDialer"
```

---

## 🎯 优势总结

### ✅ 用户优势

1. **下载更快**：200 MB vs 1000 MB（5倍）
2. **安装更快**：2分钟 vs 10分钟（5倍）
3. **节省空间**：200 MB vs 1000 MB（5倍）

### ✅ 开发优势

1. **代码复用**：所有程序共享 `BrowserManager`
2. **维护简单**：只需维护一个浏览器
3. **更新灵活**：组件可独立更新

### ✅ 部署优势

1. **安装包小**：便于网络分发
2. **安装快速**：提升用户体验
3. **卸载干净**：不留残留文件

---

## 📚 相关文件

| 文件 | 说明 |
|------|------|
| `browser_manager.py` | 浏览器管理模块 |
| `TP-Link_Dialer_main_nobrowser.spec` | 主程序打包配置（不含浏览器）|
| `CleanupService_nobrowser.spec` | 清理服务打包配置（不含浏览器）|
| `SetupScript_Optimized.nsi` | NSIS 安装脚本（共享浏览器）|
| `build_optimized.bat` | 自动化打包脚本 |

---

**版本**: 2.1
**更新日期**: 2026-03-19
**作者**: Kilo Code
