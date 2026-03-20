# 浏览器路径问题修复

## 问题描述
程序打包后找不到内置浏览器，提示：
```
Executable doesn't exist at C:\Program Files\TPLinkDialer\_internal\playwright\...
```

## 原因
程序打包后，浏览器文件位于 `_internal/chrome-win64/chrome.exe`，但代码没有正确查找这个路径。

## 解决方案

### 方案1：直接替换文件（快速修复）

如果您已经安装了程序，只需替换主程序文件：

1. 关闭正在运行的程序
2. 将新版本的主程序复制到安装目录
   ```
   源文件: dist\TP-Link_Dialer\TP-Link_Dialer.exe
   目标位置: C:\Program Files\TPLinkDialer\TP-Link_Dialer.exe
   ```
3. 重新启动程序

### 方案2：重新安装（完整修复）

等待新安装包生成后，重新运行安装程序。

## 修复内容

更新了 `browser_manager.py`，增加了以下查找路径：
- `_internal/chrome-win64/chrome.exe` (打包后的标准位置)
- `chrome-win64/chrome.exe` (开发环境位置)
- 以及其他可能的浏览器路径

## 验证

修复后，程序应该能正常启动内置浏览器并连接路由器。

如果仍有问题，请检查：
1. 浏览器文件是否存在
2. 文件权限是否正确
3. 防病毒软件是否阻止
