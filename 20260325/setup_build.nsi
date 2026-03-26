; Broadband Dialer Helper - NSIS Installer
; Unicode support for Chinese characters
Unicode true

!include "MUI2.nsh"
!include "x64.nsh"

; ============================================
; Configuration
; ============================================
Name "Broadband Dialer"
OutFile "Broadband_Dialer_Setup.exe"
InstallDir "$PROGRAMFILES\Broadband_Dialer"
RequestExecutionLevel admin

; Version
VIProductVersion "1.0.0.0"
VIAddVersionKey "ProductName" "Broadband Dialer"
VIAddVersionKey "FileDescription" "TP-Link Broadband Dialer Setup"
VIAddVersionKey "FileVersion" "1.0.0.0"
VIAddVersionKey "ProductVersion" "1.0.0.0"
VIAddVersionKey "LegalCopyright" "2025"

; Compress
SetCompressor /SOLID lzma

; ============================================
; Pages
; ============================================
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "license.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\broadband_dialer.exe"
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Language
!insertmacro MUI_LANGUAGE "SimpChinese"

; ============================================
; Sections
; ============================================

Section "Main Program" SecMain
  SectionIn RO

  SetOutPath $INSTDIR

  ; Main program
  File /oname=broadband_dialer.exe dist\broadband_dialer.exe

  ; Icons
  File app.ico
  File online.ico
  File offline.ico
  File connecting.ico
  File error.ico

  ; Shortcuts
  CreateShortcut "$DESKTOP\宽带拨号.lnk" "$INSTDIR\broadband_dialer.exe"
  CreateDirectory "$SMPROGRAMS\Broadband_Dialer"
  CreateShortcut "$SMPROGRAMS\Broadband_Dialer\Broadband_Dialer.lnk" "$INSTDIR\broadband_dialer.exe"

  ; Registry
  WriteRegStr HKLM "Software\Broadband_Dialer" "Install_Dir" $INSTDIR
  WriteRegStr HKLM "Software\Broadband_Dialer" "Version" "1.0.0"

  ; Uninstall
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Broadband_Dialer" "DisplayName" "Broadband Dialer"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Broadband_Dialer" "UninstallString" "$INSTDIR\uninstall.exe"

SectionEnd

Section "System Service" SecService
  SectionIn RO

  SetOutPath $INSTDIR

  ; Service program
  File "/oname=TPLinkCleanupService.exe" "dist\TPLinkCleanupService.exe"

  ; Install and start service
  DetailPrint "Installing shutdown cleanup service..."
  nsExec::ExecToLog '"$INSTDIR\TPLinkCleanupService.exe" install'
  Pop $0
  ${If} $0 != "0"
    DetailPrint "Warning: Service install returned code $0"
  ${EndIf}

  Sleep 2000

  DetailPrint "Starting service..."
  nsExec::ExecToLog 'net start TPLinkShutdownCleanup'
  Pop $1
  ${If} $1 != "0"
    DetailPrint "Warning: Service start returned code $1"
  ${EndIf}

  DetailPrint "Service installed successfully!"
  nsExec::ExecToLog 'sc query TPLinkShutdownCleanup'

SectionEnd

Section -Post

  WriteUninstaller "$INSTDIR\uninstall.exe"

  DetailPrint "=========================================="
  DetailPrint "Installation Complete!"
  DetailPrint "=========================================="
  DetailPrint "Main Program: $INSTDIR\broadband_dialer.exe"
  DetailPrint "Service: TPLinkShutdownCleanup"
  DetailPrint ""

SectionEnd

; ============================================
; Uninstall
; ============================================

Section "Uninstall"

  DetailPrint "Stopping service..."
  nsExec::ExecToLog 'net stop TPLinkShutdownCleanup'
  Sleep 1000

  DetailPrint "Removing service..."
  nsExec::ExecToLog '"$INSTDIR\TPLinkCleanupService.exe" remove'
  Sleep 1000

  DetailPrint "Stopping processes..."
  nsExec::ExecToLog 'taskkill /F /IM broadband_dialer.exe'
  nsExec::ExecToLog 'taskkill /F /IM TPLinkCleanupService.exe'
  Sleep 1000

  DetailPrint "Deleting files..."
  Delete /REBOOTOK "$INSTDIR\broadband_dialer.exe"
  Delete /REBOOTOK "$INSTDIR\TPLinkCleanupService.exe"
  Delete /REBOOTOK "$INSTDIR\app.ico"
  Delete /REBOOTOK "$INSTDIR\online.ico"
  Delete /REBOOTOK "$INSTDIR\offline.ico"
  Delete /REBOOTOK "$INSTDIR\connecting.ico"
  Delete /REBOOTOK "$INSTDIR\error.ico"
  Delete /REBOOTOK "$INSTDIR\uninstall.exe"
  Delete /REBOOTOK "$INSTDIR\license.txt"

  RMDir /REBOOTOK "$INSTDIR"

  DetailPrint "Deleting shortcuts..."
  Delete "$DESKTOP\宽带拨号.lnk"
  RMDir /r "$SMPROGRAMS\Broadband_Dialer"

  DetailPrint "Cleaning registry..."
  DeleteRegKey HKLM "Software\Broadband_Dialer"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Broadband_Dialer"

  DetailPrint "=========================================="
  DetailPrint "Uninstall Complete!"
  DetailPrint "=========================================="

SectionEnd

; ============================================
; Component Descriptions
; ============================================

LangString DESC_SecMain ${LANG_SIMPCHINESE} "Main program with GUI for broadband dialing"
LangString DESC_SecService ${LANG_SIMPCHINESE} "Windows service for automatic router cleanup on shutdown"

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SecMain} $(DESC_SecMain)
  !insertmacro MUI_DESCRIPTION_TEXT ${SecService} $(DESC_SecService)
!insertmacro MUI_FUNCTION_DESCRIPTION_END
