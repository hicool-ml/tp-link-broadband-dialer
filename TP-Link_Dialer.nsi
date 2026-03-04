; TP-Link宽带拨号工具 - 安装程序脚本
; 使用 NSIS (Nullsoft Scriptable Install System) 编译
; 编码：UTF-8 with BOM
; 注意：请使用支持UTF-8的编辑器编辑此文件

; 设置Unicode支持
!define UNICODE
!define _UNICODE

; 应用程序信息
!define APP_NAME "TP-Link宽带拨号"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "Kilo Code"
!define APP_EXE "TP-Link_Dialer.exe"
!define APP_DIR "TP-Link_Dialer"
!define APP_ICON "app.ico"

; 安装程序配置
Name "${APP_NAME}"
OutFile "发布包\TP-Link_Dialer_Setup.exe"
InstallDir "$PROGRAMFILES64\${APP_DIR}"
InstallDirRegKey HKLM "Software\${APP_DIR}" "InstallPath"
RequestExecutionLevel admin
Compress /SOLID LZMA
ShowInstDetails show
ShowUninstDetails show

; 界面设置
!include "MUI2.nsh"

!define MUI_ABORTWARNING
!define MUI_COMPONENTSPAGE_NODESC

; 欢迎页面
!insertmacro MUI_PAGE_WELCOME
; 许可协议页面
!insertmacro MUI_PAGE_LICENSE
; 组件页面（可选）
;!insertmacro MUI_PAGE_COMPONENTS
; 安装目录页面
!insertmacro MUI_PAGE_DIRECTORY
; 安装过程页面
!insertmacro MUI_PAGE_INSTFILES
; 完成页面
!insertmacro MUI_PAGE_FINISH

; 语言设置
!insertmacro MUI_LANGUAGE "SimpChinese"

; 许可协议文本
LicenseData "使用说明.txt"

; 安装部分
Section "主程序" SecMain
  SectionIn RO
  
  SetOutPath $INSTDIR
  
  DetailPrint "正在复制程序文件..."
  
  ; 复制主程序文件
  File "dist\${APP_EXE}"
  
  ; 复制图标文件
  File "app.ico"
  File "connecting.ico"
  File "error.ico"
  File "offline.ico"
  File "online.ico"
  
  ; 复制说明文件
  File "使用说明.txt"
  
  ; 创建桌面快捷方式
  DetailPrint "正在创建桌面快捷方式..."
  CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\${APP_ICON}" 0
  
  ; 创建开始菜单快捷方式
  DetailPrint "正在创建开始菜单快捷方式..."
  CreateDirectory "$SMPROGRAMS\${APP_NAME}"
  CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\${APP_ICON}" 0
  CreateShortCut "$SMPROGRAMS\${APP_NAME}\卸载.lnk" "$INSTDIR\uninstall.exe"
  
  ; 写入注册表
  DetailPrint "正在写入注册表..."
  WriteRegStr HKLM "Software\${APP_DIR}" "InstallPath" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayVersion" "${APP_VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "Publisher" "${APP_PUBLISHER}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoRepair" 1
  
  ; 创建卸载程序
  DetailPrint "正在创建卸载程序..."
  WriteUninstaller "$INSTDIR\uninstall.exe"
  
  DetailPrint "安装完成！"
SectionEnd

; 卸载部分
Section "Uninstall"
  ; 删除文件
  DetailPrint "正在删除程序文件..."
  Delete "$INSTDIR\${APP_EXE}"
  Delete "$INSTDIR\${APP_ICON}"
  Delete "$INSTDIR\connecting.ico"
  Delete "$INSTDIR\error.ico"
  Delete "$INSTDIR\offline.ico"
  Delete "$INSTDIR\online.ico"
  Delete "$INSTDIR\使用说明.txt"
  Delete "$INSTDIR\uninstall.exe"
  
  ; 删除快捷方式
  DetailPrint "正在删除快捷方式..."
  Delete "$DESKTOP\${APP_NAME}.lnk"
  RMDir /r "$SMPROGRAMS\${APP_NAME}"
  
  ; 删除注册表
  DetailPrint "正在清理注册表..."
  DeleteRegKey HKLM "Software\${APP_DIR}"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
  
  ; 删除安装目录
  DetailPrint "正在删除安装目录..."
  RMDir "$INSTDIR"
  
  DetailPrint "卸载完成！"
SectionEnd
