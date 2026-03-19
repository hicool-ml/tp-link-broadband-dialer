# 项目更新说明

## 更新日期：2026-03-18

## 主要变更

### 1. 新增文件

- **shutdown_cleanup_service.py** - 新的后台清理服务
  - 独立的Windows服务
  - 专注于关机时清理路由器账号
  - 更可靠的清理流程

- **manage_cleanup_service.bat** - 服务管理批处理文件
  - 提供菜单式的服务管理界面
  - 支持安装、卸载、启动、停止等操作

- **service_installer.py** - 图形化服务管理工具
  - 友好的GUI界面
  - 实时查看服务状态
  - 查看服务日志

- **test_cleanup.py** - 清理功能测试脚本
  - 用于测试清理服务是否正常工作

- **启动服务管理工具.bat** - 快速启动图形化管理工具

- **CLEANUP_SERVICE_README.md** - 清理服务详细说明文档

### 2. 修改的文件

- **tp_link_broadband_dialer.py** (主程序)
  - 删除了 `register_shutdown_block()` 方法
  - 删除了 `on_shutdown_query()` 方法
  - 简化了 `on_closing()` 方法，不再自动断开和清除
  - 删除了关机事件监听 `WM_QUERYENDSESSION`
  - 更新了界面提示文字

### 3. 删除的功能

以下功能已从主程序中删除，因为它们不可靠：

- ❌ Windows关机拦截功能
- ❌ 关机时自动断开并清除账号
- ❌ 窗口关闭时自动断开并清除账号
- ❌ 关机超时控制

### 4. 替代方案

使用新的后台清理服务来替代删除的功能：

- ✅ 独立的Windows服务运行
- ✅ 系统关机时自动清理路由器账号
- ✅ 更可靠的清理流程
- ✅ 独立于主程序，不受主程序状态影响

## 使用方法

### 安装清理服务

**方法1：使用图形化管理工具（推荐）**

1. 双击 `启动服务管理工具.bat`
2. 点击"安装服务"按钮
3. 点击"启动服务"按钮

**方法2：使用批处理文件**

1. 双击 `manage_cleanup_service.bat`
2. 选择"安装服务"
3. 选择"启动服务"

**方法3：使用命令行**

```bash
python shutdown_cleanup_service.py install
net start TPLinkShutdownCleanup
```

### 验证服务是否正常工作

1. 运行 `test_cleanup.py` 测试清理功能
2. 或者查看服务日志：
   ```
   %TEMP%\tplink_cleanup\cleanup_service.log
   ```

### 使用主程序

1. 运行主程序 `tp_link_broadband_dialer.py`
2. 输入账号密码，点击"开始连接"
3. 使用完成后，可以选择：
   - 手动点击"断开连接"按钮清除账号
   - 直接关闭窗口，关机时服务会自动清理

## 注意事项

1. **管理员权限**：安装和管理服务需要管理员权限
2. **服务依赖**：清理服务需要内置浏览器文件
3. **网络连接**：确保关机时路由器网络连接正常
4. **正常关机**：请使用Windows的正常关机流程

## 文件结构

```
D:\13jiao\
├── tp_link_broadband_dialer.py        # 主程序（已修改）
├── shutdown_cleanup_service.py        # 后台清理服务（新增）
├── service_installer.py               # 服务管理GUI工具（新增）
├── manage_cleanup_service.bat         # 服务管理批处理（新增）
├── 启动服务管理工具.bat               # 快速启动工具（新增）
├── test_cleanup.py                    # 测试脚本（新增）
├── CLEANUP_SERVICE_README.md          # 服务说明文档（新增）
├── CHANGELOG.md                       # 更新说明（本文件）
└── 关机拦截功能说明.md                # 旧版本文档（已过时）
```

## 与旧版本的区别

### 旧版本
- 主程序尝试拦截关机事件
- 关机时弹出对话框询问用户
- 依赖用户交互
- 可靠性较低

### 新版本
- 独立的后台服务
- 自动在关机时清理
- 不需要用户交互
- 更高的可靠性

## 故障排除

### 服务无法启动

1. 检查是否以管理员身份运行
2. 查看服务日志：`%TEMP%\tplink_cleanup\cleanup_service.log`
3. 确保内置浏览器文件存在

### 关机时账号未清除

1. 检查服务是否正在运行：`sc query TPLinkShutdownCleanup`
2. 查看服务日志确认清理过程
3. 确保路由器IP和密码配置正确

## 技术细节

### 服务配置

- 服务名称：`TPLinkShutdownCleanup`
- 显示名称：`TP-Link路由器账号清理服务`
- 启动类型：自动
- 关机超时：最长3分钟（180秒）

### 清理流程

1. 接收到 `SERVICE_CONTROL_SHUTDOWN` 控制码
2. 启动无头浏览器连接到路由器
3. 登录路由器管理界面
4. 断开网络连接
5. 清空账号密码输入框
6. 保存配置
7. 验证账号已清除
8. 关闭浏览器
9. 允许系统关机

## 开发者信息

- **版本**: 2.0
- **更新日期**: 2026-03-18
- **作者**: Kilo Code

## 许可证

与主程序使用相同的许可证。
