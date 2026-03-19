; TPLink Dialer - Fast Setup Script
; Quick build for testing

!include "MUI2.nsh"

; Installer Configuration
Name "Broadband Dial Tool v2.1"
OutFile "Release\Setup.exe"
InstallDir "$PROGRAMFILES\TPLinkDialer"
InstallDirRegKey HKLM "Software\TPLinkDialer" "InstallPath"
RequestExecutionLevel admin

; Use faster compression (zlib)
SetCompressor zlib

; Version Info
VIProductVersion "2.1.0.0"
VIAddVersionKey "ProductName" "Broadband Dial Tool"
VIAddVersionKey "CompanyName" "Kilo Code"
VIAddVersionKey "FileDescription" "TP-Link Broadband Dial Tool Installer"
VIAddVersionKey "FileVersion" "2.1.0.0"
VIAddVersionKey "ProductVersion" "2.1.0.0"
VIAddVersionKey "LegalCopyright" "2026"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "license.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\TP-Link_Dialer.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Launch Broadband Dial Tool"
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

; Sections
Section "Main Program" SecMain
    SectionIn RO
    SetOutPath $INSTDIR
    File /r "dist\TP-Link_Dialer\*"
    CreateShortCut "$DESKTOP\Broadband Dial Tool.lnk" "$INSTDIR\TP-Link_Dialer.exe" "" "$INSTDIR\app.ico" 0
    CreateDirectory "$SMPROGRAMS\Broadband Dial Tool"
    CreateShortCut "$SMPROGRAMS\Broadband Dial Tool\Broadband Dial Tool.lnk" "$INSTDIR\TP-Link_Dialer.exe" "" "$INSTDIR\app.ico" 0
    CreateShortCut "$SMPROGRAMS\Broadband Dial Tool\Uninstall.lnk" "$INSTDIR\uninstall.exe"
    WriteRegStr HKLM "Software\TPLinkDialer" "InstallPath" $INSTDIR
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TPLinkDialer" "DisplayName" "Broadband Dial Tool"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TPLinkDialer" "UninstallString" "$INSTDIR\uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TPLinkDialer" "Publisher" "Kilo Code"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TPLinkDialer" "DisplayVersion" "2.1.0.0"
SectionEnd

Section "Cleanup Service" SecService
    SetOutPath $INSTDIR
    File /r "dist\CleanupService\*"
    File "dist\ServiceInstaller.exe"
    WriteRegStr HKLM "Software\TPLinkDialer" "CleanupService" "$INSTDIR\CleanupService.exe"
SectionEnd

Section "Playwright Browser" SecBrowser
    SectionIn RO
    SetOutPath $INSTDIR
    File /r "chrome-win64\*"
    WriteUninstaller "$INSTDIR\uninstall.exe"
    WriteRegStr HKLM "Software\TPLinkDialer" "BrowserInstalled" "1"
SectionEnd

Section "-PostInstall"
    IfFileExists "$INSTDIR\CleanupService.exe" 0 +2
    ExecWait '"$INSTDIR\CleanupService.exe" install'
    IfFileExists "$INSTDIR\CleanupService.exe" 0 +2
    ExecWait 'net start TPLinkShutdownCleanup'
SectionEnd

Section "Uninstall"
    MessageBox MB_OKCANCEL "Uninstall Broadband Dial Tool?" IDCANCEL cancel
    nsExec::ExecToLog 'net stop TPLinkShutdownCleanup'
    Sleep 2000
    IfFileExists "$INSTDIR\CleanupService.exe" 0 +2
    ExecWait '"$INSTDIR\CleanupService.exe" remove'
    nsExec::ExecToLog 'taskkill /F /IM TP-Link_Dialer.exe'
    nsExec::ExecToLog 'taskkill /F /IM CleanupService.exe'
    Sleep 1000
    Delete "$INSTDIR\uninstall.exe"
    RMDir /r "$INSTDIR"
    Delete "$DESKTOP\Broadband Dial Tool.lnk"
    RMDir /r "$SMPROGRAMS\Broadband Dial Tool"
    DeleteRegKey HKLM "Software\TPLinkDialer"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TPLinkDialer"
    MessageBox MB_OK "Uninstall complete!"
    cancel:
    Abort
SectionEnd

LangString DESC_SecMain ${LANG_English} "Main program"
LangString DESC_SecService ${LANG_English} "Cleanup service"
LangString DESC_SecBrowser ${LANG_English} "Browser (required)"
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecMain} $(DESC_SecMain)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecService} $(DESC_SecService)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecBrowser} $(DESC_SecBrowser)
!insertmacro MUI_FUNCTION_DESCRIPTION_END
