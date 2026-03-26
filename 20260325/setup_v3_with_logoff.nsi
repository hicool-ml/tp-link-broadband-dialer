; TP-Link Broadband Dialer - Setup Script
; 支持：关机、重启、注销都触发清除

!define PRODUCT_NAME "TP-Link Broadband Dialer"
!define PRODUCT_VERSION "2.2.0"
!define PRODUCT_PUBLISHER "Hicool & CMCC"
!define PRODUCT_WEB_SITE "https://github.com/kilocode"
!define PRODUCT_DIR_REGKEY "Software\Broadband_Dialer"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\Broadband_Dialer"

; Setup configuration
Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "Broadband_Dialer_Setup_${PRODUCT_VERSION}.exe"
InstallDir "$PROGRAMFILES\Broadband_Dialer"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

; Modern UI
!include "MUI2.nsh"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "license.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Language
!insertmacro MUI_LANGUAGE "SimpChinese"

; Installation section
Section "MainSection" SEC01
  SetOutPath "$INSTDIR"

  ; Program files
  File "dist\broadband_dialer.exe"
  File "dist\cleanup_http.exe"
  File "cleanup.ps1"

  ; Create shortcuts
  CreateDirectory "$SMPROGRAMS\Broadband_Dialer"
  CreateShortCut "$SMPROGRAMS\Broadband_Dialer\Broadband Dialer.lnk" "$INSTDIR\broadband_dialer.exe"

  ; Desktop shortcut - Chinese name only!
  CreateShortCut "$DESKTOP\宽带拨号助手.lnk" "$INSTDIR\broadband_dialer.exe"

  ; Registry
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\broadband_dialer.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "Version" "${PRODUCT_VERSION}"

  ; Uninstall information
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayName" "${PRODUCT_NAME}"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegDWORD HKLM "${PRODUCT_UNINST_KEY}" "NoModify" 1
  WriteRegDWORD HKLM "${PRODUCT_UNINST_KEY}" "NoRepair" 1

  ; Uninstaller
  WriteUninstaller "$INSTDIR\uninstall.exe"

  ; Log directory
  CreateDirectory "$WINDIR\..\ProgramData\BroadbandDialer"

  ; ✅ 1. 任务计划：关机和重启
  DetailPrint "Creating scheduled task for shutdown/restart cleanup..."
  ExecWait 'schtasks /Delete /TN "TPLinkCleanup" /F'
  ExecWait 'schtasks /Create /TN "TPLinkCleanup" /TR "powershell.exe -ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File \"$INSTDIR\cleanup.ps1\"" /SC ONEVENT /EC System /MO "*[System[(EventID=1074 or EventID=6006)]]" /RU SYSTEM /RL HIGHEST /F'
  DetailPrint "Scheduled task created!"

  ; ✅ 2. 组策略：注销脚本
  DetailPrint "Creating logoff script..."
  ; 创建注销脚本包装器
  FileOpen $0 "$INSTDIR\cleanup_logoff.cmd" w
  FileWrite $0 "@echo off$\r$\n"
  FileWrite $0 "REM Logoff cleanup script$\r$\n"
  FileWrite $0 "powershell.exe -ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File \"$INSTDIR\cleanup.ps1\"$\r$\n"
  FileClose $0

  ; 注册为注销脚本（通过注册表）
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Logoff\0" "Script" "$INSTDIR\cleanup_logoff.cmd"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Logoff\0" "GPO-ID" "LocalGPO"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Logoff\0" "DisplayName" "Broadband Dialer Cleanup"

  ; 备用方案：用户级注销脚本
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Logoff\0" "Script" "$INSTDIR\cleanup_logoff.cmd"
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Logoff\0" "GPO-ID" "LocalGPO"
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Logoff\0" "DisplayName" "Broadband Dialer Cleanup"

  DetailPrint "Logoff script created!"

SectionEnd

; Uninstall section
Section Uninstall
  ; Delete scheduled task
  DetailPrint "Deleting scheduled task..."
  ExecWait 'schtasks /Delete /TN "TPLinkCleanup" /F'

  ; Delete logoff scripts from registry
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Logoff\0"
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Logoff\0"

  ; Delete files
  Delete "$INSTDIR\broadband_dialer.exe"
  Delete "$INSTDIR\cleanup_http.exe"
  Delete "$INSTDIR\cleanup.ps1"
  Delete "$INSTDIR\cleanup_logoff.cmd"
  Delete "$INSTDIR\config.json"
  Delete "$INSTDIR\uninstall.exe"

  ; Delete shortcuts
  Delete "$DESKTOP\宽带拨号助手.lnk"
  Delete "$SMPROGRAMS\Broadband_Dialer\Broadband Dialer.lnk"
  RMDir "$SMPROGRAMS\Broadband_Dialer"

  ; Delete registry
  DeleteRegKey HKLM "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"

  ; Delete install directory
  RMDir "$INSTDIR"
SectionEnd
