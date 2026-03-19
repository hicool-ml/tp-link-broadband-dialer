# 项目文件结构说明

## 打包前的完整文件列表

### 核心程序文件（必需）
```
tp_link_broadband_dialer.py     # 主程序 - GUI拨号工具
shutdown_cleanup_service.py     # 后台清理服务
service_installer.py            # 服务安装器（GUI）
test_cleanup.py                 # 测试脚本
```

### 配置文件（必需）
```
app.ico                         # 应用图标
connecting.ico                  # 连接中图标
error.ico                       # 错误图标
offline.ico                     # 离线图标
online.ico                      # 在线图标
```

### 打包配置（必需）
```
TP-Link_Dialer_main.spec        # 主程序打包配置
CleanupService.spec             # 清理服务打包配置
ServiceInstaller.spec           # 服务安装器打包配置
SetupScript.nsi                 # NSIS安装脚本
```

### 打包脚本（必需）
```
build_complete.bat              # 完整打包脚本
cleanup_project.bat             # 项目清理脚本
manage_cleanup_service.bat      # 服务管理（命令行）
启动服务管理工具.bat            # 服务管理（GUI启动器）
```

### 浏览器文件（必需）
```
chrome-win64/                   # Chrome浏览器（内置）
ms-playwright/                  # Playwright依赖
```

### 文档文件（必需）
```
README.md                       # 项目说明
CHANGELOG.md                    # 更新日志
CLEANUP_SERVICE_README.md       # 清理服务说明
help.txt                        # 帮助文件
license.txt                     # 许可证
使用说明.txt                    # 用户说明
```

### 临时/开发文件（可以删除）
```
build/                          # PyInstaller构建缓存
dist/                           # PyInstaller输出
__pycache__/                    # Python缓存
*.pyc                           # 编译的Python文件
edge_profile/                   # 测试用Edge配置
```

### 旧版本文件（可以删除）
```
555.py                          # 旧版测试文件
mytplink.py                     # 旧版脚本
tp_link_broadband_dialer_service.py  # 旧版服务
service_manager.py              # 旧版服务管理
test_service.py                 # 旧版测试
generate_icons.py               # 图标生成工具（已使用）
```

### 旧脚本文件（可以删除）
```
build.bat                       # 旧打包脚本
build_all.bat                   # 旧完整打包脚本
build_all_onedir.bat            # 旧单目录打包脚本
build_and_install_service.bat   # 旧服务安装脚本
build_exe.bat                   # 旧exe打包脚本
build_exe_onedir.bat            # 旧单目录exe打包脚本
build_installer.bat             # 旧安装包构建脚本
build_service.bat               # 旧服务打包脚本
install_service.bat             # 旧服务安装脚本
uninstall_service.bat           # 旧服务卸载脚本
prepare_browser.bat             # 旧浏览器准备脚本
run_test.bat                    # 旧测试脚本
make_installer.bat              # 旧安装包制作脚本
制作安装程序.bat                # 旧安装包脚本
最终打包脚本.bat                # 旧完整打包脚本
```

### 旧配置文件（可以删除）
```
TP-Link_Dialer.spec             # 旧主程序配置
installer.nsi                   # 旧安装脚本
TP-Link_Dialer.nsi              # 旧安装脚本
制作安装程序.nsi                # 旧安装脚本
```

### 旧文档文件（可以删除）
```
QUICKSTART_SERVICE.md           # 旧快速开始
SERVICE_README.md               # 旧服务说明
SERVICE_SUMMARY.md              # 旧服务总结
关机拦截功能说明.md             # 旧功能说明（已过时）
零依赖打包说明.md               # 旧打包说明
```

### 旧可执行文件（可以删除）
```
TP-Link_Dialer.exe              # 旧版本exe
Broadband_Dialer_Setup.exe      # 旧安装包
Broadband_Dialer_Setup_1.exe    # 旧安装包
chromedriver.exe                # ChromeDriver（不需要）
msedgedriver.exe                # EdgeDriver（不需要）
```

### 其他文件（可以删除）
```
13jiao.zip                      # 旧项目压缩包
```

## 清理后的项目结构

```
宽带拨号工具/
├── 核心文件/
│   ├── tp_link_broadband_dialer.py
│   ├── shutdown_cleanup_service.py
│   ├── service_installer.py
│   └── test_cleanup.py
│
├── 资源文件/
│   ├── chrome-win64/               # 浏览器（必需）
│   ├── ms-playwright/              # Playwright依赖（必需）
│   └── *.ico                       # 图标文件
│
├── 配置文件/
│   ├── TP-Link_Dialer_main.spec
│   ├── CleanupService.spec
│   ├── ServiceInstaller.spec
│   └── SetupScript.nsi
│
├── 脚本文件/
│   ├── build_complete.bat
│   ├── cleanup_project.bat
│   ├── manage_cleanup_service.bat
│   └── 启动服务管理工具.bat
│
├── 文档文件/
│   ├── README.md
│   ├── CHANGELOG.md
│   ├── CLEANUP_SERVICE_README.md
│   ├── PROJECT_STRUCTURE.md        # 本文件
│   ├── help.txt
│   ├── license.txt
│   └── 使用说明.txt
│
└── 输出目录（打包后生成）
    ├── build/                      # 构建缓存
    ├── dist/                       # 打包输出
    │   ├── TP-Link_Dialer/
    │   ├── CleanupService/
    │   └── ServiceInstaller.exe
    └── Release/
        └── Setup.exe               # 最终安装包
```

## 使用说明

### 1. 清理项目
```bash
cleanup_project.bat
```

### 2. 打包项目
```bash
build_complete.bat
```

### 3. 安装和测试
```bash
# 安装主程序
Release\Setup.exe

# 或单独测试组件
dist\TP-Link_Dialer\TP-Link_Dialer.exe
```

## 注意事项

1. **浏览器文件**：chrome-win64 和 ms-playwright 必须保留
2. **图标文件**：所有 .ico 文件必须保留
3. **配置文件**：.spec 和 .nsi 文件必须保留
4. **文档文件**：保留最新的 README 和相关说明

## 版本历史

- v2.0 (2026-03-18) - 重构项目，添加后台清理服务
- v1.x - 早期版本
