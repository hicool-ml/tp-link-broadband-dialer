; Broadband Dialing Tool - Installer Script
; Use NSIS to create Windows installer package

!define APP_NAME "Broadband Dialing Tool"
!define APP_NAME_CN "宽带拨号工具"
!define APP_VERSION "2.0"
!define APP_PUBLISHER "Kilo Code"
!define APP_EXE "TP-Link_Dialer.exe"

; Request admin privileges
RequestExecutionLevel admin

; Set compression algorithm
SetCompressor lzma

; Installer settings
Name "${APP_NAME_CN}"
OutFile "Release\Setup.exe"
InstallDir "$PROGRAMFILES64\BroadbandDialer"
InstallDirRegKey HKLM "Software\${APP_NAME}" "InstallLocation"
ShowInstDetails show
ShowUnInstDetails show

; Modern UI
!include "MUI2.nsh"

; UI configuration
!define MUI_ABORTWARNING
!define MUI_ICON "app.ico"
!define MUI_UNICON "app.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "app.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "app.ico"

; Welcome page
!insertmacro MUI_PAGE_WELCOME
; License page
!insertmacro MUI_PAGE_LICENSE "license.txt"
; Directory page
!insertmacro MUI_PAGE_DIRECTORY
; Installation page
!insertmacro MUI_PAGE_INSTFILES
; Finish page
!insertmacro MUI_PAGE_FINISH

; Language settings
!insertmacro MUI_LANGUAGE "SimpChinese"

; Installation section
Section "Main Program" SecMain
  SectionIn RO

  SetOutPath $INSTDIR

  ; Main program files
  File /r "dist\TP-Link_Dialer\*"

  ; Cleanup service
  File /r "dist\CleanupService\*"

  ; Service installer
  File "dist\ServiceInstaller.exe"

  ; Documentation
  File "README.md"
  File "CLEANUP_SERVICE_README.md"
  File "Release\快速使用指南.md"
  File "Release\部署说明.md"

  ; Create shortcuts
  CreateDirectory "$SMPROGRAMS\${APP_NAME_CN}"
  CreateShortCut "$SMPROGRAMS\${APP_NAME_CN}\宽带拨号工具.lnk" "$INSTDIR\TP-Link_Dialer\TP-Link_Dialer.exe" "" "$INSTDIR\TP-Link_Dialer\TP-Link_Dialer.exe" 0
  CreateShortCut "$SMPROGRAMS\${APP_NAME_CN}\服务管理工具.lnk" "$INSTDIR\ServiceInstaller.exe" "" "$INSTDIR\ServiceInstaller.exe" 0
  CreateShortCut "$SMPROGRAMS\${APP_NAME_CN}\卸载.lnk" "$INSTDIR\uninstall.exe"

  ; Desktop shortcut
  CreateShortCut "$DESKTOP\宽带拨号工具.lnk" "$INSTDIR\TP-Link_Dialer\TP-Link_Dialer.exe" "" "$INSTDIR\TP-Link_Dialer\TP-Link_Dialer.exe" 0

  ; Write registry
  WriteRegStr HKLM "Software\${APP_NAME}" "InstallLocation" $INSTDIR
  WriteRegStr HKLM "Software\${APP_NAME}" "Version" "${APP_VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME_CN}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayVersion" "${APP_VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "Publisher" "${APP_PUBLISHER}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "QuietUninstallString" "$INSTDIR\uninstall.exe /S"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoRepair" 1

  ; Create uninstaller
  WriteUninstaller "$INSTDIR\uninstall.exe"

SectionEnd

; Install cleanup service section
Section "Cleanup Service" SecService
  SectionIn RO

  DetailPrint "Installing cleanup service..."
  ExecWait '"$INSTDIR\CleanupService\CleanupService.exe" install' $0
  DetailPrint "Service install return code: $0"

  DetailPrint "Starting cleanup service..."
  ExecWait '"$INSTDIR\CleanupService\CleanupService.exe" start' $0
  DetailPrint "Service start return code: $0"

  ; Show service installation result
  DetailPrint "Cleanup service has been installed and started"
  DetailPrint "This service will automatically clear router credentials on shutdown"

SectionEnd

; Post-install actions
Function .onInstSuccess
  ; Ask to launch main program
  MessageBox MB_YESNO "Installation completed!$\r$\n$\r$\nDo you want to launch the Broadband Dialing Tool now?" IDNO NoRun
    ExecShell "" "$SMPROGRAMS\${APP_NAME_CN}\宽带拨号工具.lnk"
  NoRun:
FunctionEnd

; Uninstall section
Section "Uninstall"

  ; Stop and uninstall service
  DetailPrint "Stopping cleanup service..."
  ExecWait '"$INSTDIR\CleanupService\CleanupService.exe" stop' $0
  DetailPrint "Service stop return code: $0"

  DetailPrint "Uninstalling cleanup service..."
  ExecWait '"$INSTDIR\CleanupService\CleanupService.exe" remove' $0
  DetailPrint "Service uninstall return code: $0"

  ; Delete files
  RMDir /r "$INSTDIR\*"

  ; Delete shortcuts
  RMDir /r "$SMPROGRAMS\${APP_NAME_CN}"
  Delete "$DESKTOP\宽带拨号工具.lnk"

  ; Delete registry
  DeleteRegKey HKLM "Software\${APP_NAME}"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"

SectionEnd
