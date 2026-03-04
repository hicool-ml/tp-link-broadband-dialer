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
!define APP_ICON "app.ico"

; Installer configuration
Name "${APP_NAME}"
OutFile "Release\Broadband-Dialer-Setup.exe"
InstallDir "C:\Program Files\${APP_DIR}"
InstallDirRegKey HKLM "Software\${APP_DIR}" "InstallPath"
RequestExecutionLevel admin

; Interface settings
!include "MUI2.nsh"

!define MUI_ABORTWARNING

; Welcome page
!insertmacro MUI_PAGE_WELCOME
; Directory page
!insertmacro MUI_PAGE_DIRECTORY
; Installation page
!insertmacro MUI_PAGE_INSTFILES
; Finish page
!insertmacro MUI_PAGE_FINISH

; Language
!insertmacro MUI_LANGUAGE "SimpChinese"

; Installation section
Section "Main Program" SecMain
  SectionIn RO

  SetOutPath $INSTDIR

  DetailPrint "Copying program files..."

  ; Copy all files and folders
  File /r "dist\${APP_DIR}\*.*"
  
  ; Copy icon file
  File "app.ico"

  ; Create desktop shortcut
  DetailPrint "Creating desktop shortcut..."
  CreateShortCut "$DESKTOP\拨号上网.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\${APP_ICON}" 0

  ; Create start menu shortcut
  DetailPrint "Creating start menu shortcut..."
  CreateDirectory "$SMPROGRAMS\${APP_NAME}"
  CreateShortCut "$SMPROGRAMS\${APP_NAME}\拨号上网.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\${APP_ICON}" 0
  CreateShortCut "$SMPROGRAMS\${APP_NAME}\卸载.lnk" "$INSTDIR\uninstall.exe"

  ; Write registry
  DetailPrint "Writing registry..."
  WriteRegStr HKLM "Software\${APP_DIR}" "InstallPath" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayVersion" "${APP_VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "Publisher" "${APP_PUBLISHER}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoRepair" 1

  ; Create uninstaller
  DetailPrint "Creating uninstaller..."
  WriteUninstaller "$INSTDIR\uninstall.exe"

  DetailPrint "Installation complete"
SectionEnd

; Uninstallation section
Section "Uninstall"
  ; Delete files
  DetailPrint "Deleting program files..."
  RMDir /r "$INSTDIR"

  ; Delete shortcuts
  DetailPrint "Deleting shortcuts..."
  Delete "$DESKTOP\拨号上网.lnk"
  RMDir /r "$SMPROGRAMS\${APP_NAME}"

  ; Delete registry
  DetailPrint "Cleaning registry..."
  DeleteRegKey HKLM "Software\${APP_DIR}"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"

  DetailPrint "Uninstallation complete"
SectionEnd
