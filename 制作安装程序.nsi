; 宽带拨号工具 - 安装程序脚本
; 使用 NSIS (Nullsoft Scriptable Install System) 编译
; 编码：UTF-8 with BOM

!define UNICODE
!define _UNICODE

!define APP_NAME "宽带拨号"
!define APP_VERSION "1.0"
!define APP_PUBLISHER "Hicool & CMCC"
!define APP_EXE "宽带拨号.exe"
!define APP_DIR "Broadband_Dialer"

; 安装程序配置
Name "${APP_NAME}"
OutFile "发布包\宽带拨号工具-安装程序.exe"
InstallDir "$PROGRAMFILES\${APP_DIR}"
InstallDirRegKey HKLM "Software\${APP_DIR}" "InstallPath"
RequestExecutionLevel admin

; 安装程序界面设置
!include "MUI2.nsh"

; 界面设置
!define MUI_ABORTWARNING
!define MUI_ICON "app.ico"           ; 安装程序图标
!define MUI_UNICON "app.ico"         ; 卸载程序图标

; 欢迎页面
!insertmacro MUI_PAGE_WELCOME
; 许可协议页面（可选）
;!insertmacro MUI_PAGE_LICENSE "license.txt"
; 安装目录选择页面
!insertmacro MUI_PAGE_DIRECTORY
; 安装进度页面
!insertmacro MUI_PAGE_INSTFILES
; 完成页面
!insertmacro MUI_PAGE_FINISH

; 语言设置
!insertmacro MUI_LANGUAGE "SimpChinese"

; 安装部分
Section "主程序" SecMain
  SectionIn RO

  ; 设置输出路径到安装目录
  SetOutPath $INSTDIR

  ; 显示安装详情
  DetailPrint "正在复制程序文件..."

  ; 复制所有文件和文件夹
  File /r "dist\${APP_DIR}\*.*"

  ; 复制图标文件
  File "app.ico"

  ; 创建桌面快捷方式
  DetailPrint "正在创建桌面快捷方式..."
  CreateShortCut "$DESKTOP\拨号上网.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\app.ico" 0

  ; 创建开始菜单快捷方式
  DetailPrint "正在创建开始菜单快捷方式..."
  CreateDirectory "$SMPROGRAMS\${APP_NAME}"
  CreateShortCut "$SMPROGRAMS\${APP_NAME}\拨号上网.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\app.ico" 0
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

  ; 完成安装
  DetailPrint "安装完成！"
SectionEnd

; 卸载部分
Section "Uninstall"
  ; 删除文件
  DetailPrint "正在删除程序文件..."
  RMDir /r "$INSTDIR"

  ; 删除快捷方式
  DetailPrint "正在删除快捷方式..."
  Delete "$DESKTOP\拨号上网.lnk"
  RMDir /r "$SMPROGRAMS\${APP_NAME}"

  ; 删除注册表项
  DetailPrint "正在清理注册表..."
  DeleteRegKey HKLM "Software\${APP_DIR}"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"

  ; 完成卸载
  DetailPrint "卸载完成！"
SectionEnd
