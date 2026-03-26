; TP-Link Broadband Dialer - Setup Script
; 使用GPO关机脚本机制（企业级可靠）

!define PRODUCT_NAME "TP-Link Broadband Dialer"
!define PRODUCT_VERSION "2.2.0"
!define PRODUCT_PUBLISHER "Hicool & CMCC"
!define PRODUCT_DIR_REGKEY "Software\Broadband_Dialer"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\Broadband_Dialer"

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "Broadband_Dialer_Setup_${PRODUCT_VERSION}.exe"
InstallDir "$PROGRAMFILES\Broadband_Dialer"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

!include "MUI2.nsh"

!define MUI_FINISHPAGE_RUN
!define MUI_FINISHPAGE_RUN_TEXT "运行宽带拨号助手"
!define MUI_FINISHPAGE_RUN_FUNCTION "RunApplication"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "license.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "SimpChinese"

Function RunApplication
  ExecShell "open" "$INSTDIR\broadband_dialer.exe"
FunctionEnd

Section "MainSection" SEC01
  SetOutPath "$INSTDIR"

  File "dist\broadband_dialer.exe"
  File "dist\cleanup_http.exe"
  File "cleanup.ps1"

  CreateDirectory "$SMPROGRAMS\Broadband_Dialer"
  CreateShortCut "$SMPROGRAMS\Broadband_Dialer\Broadband Dialer.lnk" "$INSTDIR\broadband_dialer.exe"
  CreateShortCut "$DESKTOP\宽带连接.lnk" "$INSTDIR\broadband_dialer.exe"

  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\broadband_dialer.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "Version" "${PRODUCT_VERSION}"

  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayName" "${PRODUCT_NAME}"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegDWORD HKLM "${PRODUCT_UNINST_KEY}" "NoModify" 1
  WriteRegDWORD HKLM "${PRODUCT_UNINST_KEY}" "NoRepair" 1

  WriteUninstaller "$INSTDIR\uninstall.exe"

  CreateDirectory "$WINDIR\..\ProgramData\BroadbandDialer"

  ; GPO关机脚本（企业级可靠）
  DetailPrint "Registering GPO shutdown script..."
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Shutdown\0\0" "Script" "powershell.exe"
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Shutdown\0\0" "Parameters" '-ExecutionPolicy Bypass -File "$INSTDIR\cleanup.ps1"'
  WriteRegDWORD HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Shutdown\0\0" "IsPowershell" 1
  DetailPrint "GPO shutdown script registered!"

SectionEnd

Section Uninstall
  DetailPrint "Deleting GPO shutdown script..."
  DeleteRegKey HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Shutdown\0\0"

  Delete "$INSTDIR\broadband_dialer.exe"
  Delete "$INSTDIR\cleanup_http.exe"
  Delete "$INSTDIR\cleanup.ps1"
  Delete "$INSTDIR\config.json"
  Delete "$INSTDIR\uninstall.exe"

  Delete "$DESKTOP\宽带连接.lnk"
  Delete "$SMPROGRAMS\Broadband_Dialer\Broadband Dialer.lnk"
  RMDir "$SMPROGRAMS\Broadband_Dialer"

  DeleteRegKey HKLM "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"

  RMDir "$INSTDIR"
SectionEnd
