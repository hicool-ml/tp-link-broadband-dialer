; TP-Link Broadband Dialer - Setup Script
; 使用关机脚本机制（GPO）- 真正可靠的方案
; UTF-8 with BOM encoding

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

; Finish page configuration
!define MUI_FINISHPAGE_RUN
!define MUI_FINISHPAGE_RUN_TEXT "运行宽带拨号助手"
!define MUI_FINISHPAGE_RUN_FUNCTION "RunApplication"

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

; Function to run application
Function RunApplication
  ExecShell "open" "$INSTDIR\broadband_dialer.exe"
FunctionEnd

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
  CreateShortCut "$DESKTOP\宽带连接.lnk" "$INSTDIR\broadband_dialer.exe"

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

  ; ✅ 关机脚本（GPO）- 真正可靠的方案
  DetailPrint "Registering shutdown script (GPO)..."

  ; 注册关机脚本
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Shutdown\0\0" "Script" "powershell.exe"
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Shutdown\0\0" "Parameters" '-ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File "$INSTDIR\cleanup.ps1"'

  ; 注册GPO-ID和RefCount
  WriteRegDWORD HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Shutdown\0\0" "GPO-ID" 0
  WriteRegDWORD HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Shutdown\0\0" "RefCount" 1

  DetailPrint "Shutdown script registered successfully!"

SectionEnd

; Uninstall section
Section Uninstall
  ; Delete shutdown script
  DetailPrint "Deleting shutdown script..."
  DeleteRegKey HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Shutdown\0"

  ; Delete files
  Delete "$INSTDIR\broadband_dialer.exe"
  Delete "$INSTDIR\cleanup_http.exe"
  Delete "$INSTDIR\cleanup.ps1"
  Delete "$INSTDIR\config.json"
  Delete "$INSTDIR\uninstall.exe"

  ; Delete shortcuts
  Delete "$DESKTOP\宽带连接.lnk"
  Delete "$SMPROGRAMS\Broadband_Dialer\Broadband Dialer.lnk"
  RMDir "$SMPROGRAMS\Broadband_Dialer"

  ; Delete registry
  DeleteRegKey HKLM "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"

  ; Delete install directory
  RMDir "$INSTDIR"
SectionEnd
