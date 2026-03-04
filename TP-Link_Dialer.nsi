; TP-Link Broadband Dialer Tool - Installer Script
; Compiled with NSIS (Nullsoft Scriptable Install System)
; Encoding: UTF-8 with BOM (save file as UTF-8 with BOM)

; Enable Unicode support (required for Chinese characters)
Unicode true

; Application Information
!define APP_NAME "宽带拨号"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "Kilo Code"
!define APP_EXE "TP-Link_Dialer.exe"
!define APP_DIR "BroadbandDialer"
!define APP_ICON "app.ico"

; Installer Configuration
Name "${APP_NAME}"
OutFile "Release\宽带拨号工具_Setup.exe"
InstallDir "$PROGRAMFILES64\${APP_DIR}"
InstallDirRegKey HKLM "Software\${APP_DIR}" "InstallPath"
RequestExecutionLevel admin
SetCompressor /SOLID lzma
ShowInstDetails show
ShowUninstDetails show

; Interface Settings
!include "MUI2.nsh"

!define MUI_ABORTWARNING
!define MUI_COMPONENTSPAGE_NODESC

; License Data
LicenseData "license.txt"

; Welcome Page
!insertmacro MUI_PAGE_WELCOME
; License Page
!insertmacro MUI_PAGE_LICENSE "license.txt"
; Directory Page
!insertmacro MUI_PAGE_DIRECTORY
; Installation Page
!insertmacro MUI_PAGE_INSTFILES
; Finish Page
!insertmacro MUI_PAGE_FINISH

; Language Settings (Must be after all pages)
!insertmacro MUI_LANGUAGE "SimpChinese"

; Installation Section
Section "主程序" SecMain
  SectionIn RO
  
  SetOutPath $INSTDIR
  
  DetailPrint "正在复制程序文件..."
  
  ; Copy entire dist directory (onedir mode)
  File /r "dist\TP-Link_Dialer\*.*"
  
  ; Copy icon files
  File "app.ico"
  File "connecting.ico"
  File "error.ico"
  File "offline.ico"
  File "online.ico"
  
  ; Copy documentation
  File "license.txt"
  
  SetOutPath $INSTDIR
  
  ; Create desktop shortcut
  DetailPrint "正在创建桌面快捷方式..."
  CreateShortCut "$DESKTOP\宽带链接.lnk" "$INSTDIR\TP-Link_Dialer\${APP_EXE}" "" "$INSTDIR\${APP_ICON}" 0
  
  ; Create start menu shortcuts
  DetailPrint "正在创建开始菜单快捷方式..."
  CreateDirectory "$SMPROGRAMS\宽带拨号工具"
  CreateShortCut "$SMPROGRAMS\宽带拨号工具\宽带链接.lnk" "$INSTDIR\TP-Link_Dialer\${APP_EXE}" "" "$INSTDIR\${APP_ICON}" 0
  CreateShortCut "$SMPROGRAMS\宽带拨号工具\卸载.lnk" "$INSTDIR\uninstall.exe"
  
  ; Write registry entries
  DetailPrint "正在写入注册表..."
  WriteRegStr HKLM "Software\${APP_DIR}" "InstallPath" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayVersion" "${APP_VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "Publisher" "${APP_PUBLISHER}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoRepair" 1
  
  ; Create uninstaller
  DetailPrint "正在创建卸载程序..."
  WriteUninstaller "$INSTDIR\uninstall.exe"
  
  DetailPrint "安装完成！"
SectionEnd

; Uninstallation Section
Section "Uninstall"
  ; Delete files
  DetailPrint "正在删除程序文件..."
  
  ; Delete entire dist directory
  RMDir /r "$INSTDIR\TP-Link_Dialer"
  
  ; Delete icon files
  Delete "$INSTDIR\${APP_ICON}"
  Delete "$INSTDIR\connecting.ico"
  Delete "$INSTDIR\error.ico"
  Delete "$INSTDIR\offline.ico"
  Delete "$INSTDIR\online.ico"
  Delete "$INSTDIR\license.txt"
  Delete "$INSTDIR\uninstall.exe"
  
  ; Delete shortcuts
  DetailPrint "正在删除快捷方式..."
  Delete "$DESKTOP\宽带链接.lnk"
  RMDir /r "$SMPROGRAMS\宽带拨号工具"
  
  ; Delete registry entries
  DetailPrint "正在清理注册表..."
  DeleteRegKey HKLM "Software\${APP_DIR}"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
  
  ; Delete installation directory
  DetailPrint "正在删除安装目录..."
  RMDir "$INSTDIR"
  
  DetailPrint "卸载完成！"
SectionEnd

