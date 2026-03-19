; TPLink Dialer - Stable Setup Script
; Fixed installer integrity check issue

!include "MUI2.nsh"

; Installer Configuration
Name "Broadband Dial Tool v2.1"
OutFile "Release\Setup.exe"
InstallDir "$PROGRAMFILES\TPLinkDialer"
InstallDirRegKey HKLM "Software\TPLinkDialer" "InstallPath"
RequestExecutionLevel admin

; Set compressor (use more conservative settings)
SetCompressor lzma
SetCompressorDictSize 32
SetDatablockOptimize on

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

; Finish Page
!define MUI_FINISHPAGE_RUN "$INSTDIR\TP-Link_Dialer.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Launch Broadband Dial Tool"
!insertmacro MUI_PAGE_FINISH

; Uninstall Pages
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Language
!insertmacro MUI_LANGUAGE "English"

; Installer Sections
Section "Main Program" SecMain
    SectionIn RO

    SetOutPath $INSTDIR

    ; Install main program
    File /r "dist\TP-Link_Dialer\*"

    ; Create desktop shortcut
    CreateShortCut "$DESKTOP\Broadband Dial Tool.lnk" "$INSTDIR\TP-Link_Dialer.exe" "" "$INSTDIR\app.ico" 0

    ; Create start menu shortcuts
    CreateDirectory "$SMPROGRAMS\Broadband Dial Tool"
    CreateShortCut "$SMPROGRAMS\Broadband Dial Tool\Broadband Dial Tool.lnk" "$INSTDIR\TP-Link_Dialer.exe" "" "$INSTDIR\app.ico" 0
    CreateShortCut "$SMPROGRAMS\Broadband Dial Tool\Uninstall.lnk" "$INSTDIR\uninstall.exe"

    ; Write registry
    WriteRegStr HKLM "Software\TPLinkDialer" "InstallPath" $INSTDIR
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TPLinkDialer" "DisplayName" "Broadband Dial Tool"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TPLinkDialer" "UninstallString" "$INSTDIR\uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TPLinkDialer" "Publisher" "Kilo Code"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TPLinkDialer" "DisplayVersion" "2.1.0.0"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TPLinkDialer" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TPLinkDialer" "NoRepair" 1

SectionEnd

Section "Cleanup Service" SecService
    SetOutPath $INSTDIR

    ; Install cleanup service
    File /r "dist\CleanupService\*"

    ; Install service installer
    File "dist\ServiceInstaller.exe"

    ; Write service registry
    WriteRegStr HKLM "Software\TPLinkDialer" "CleanupService" "$INSTDIR\CleanupService.exe"

SectionEnd

Section "Playwright Browser (Required)" SecBrowser
    SectionIn RO

    SetOutPath $INSTDIR

    ; Install shared browser (use solid file compression)
    File /r /x "*.pdb" /x "*.debug" "chrome-win64\*"

    ; Write browser install flag
    WriteRegStr HKLM "Software\TPLinkDialer" "BrowserInstalled" "1"

    ; Write uninstaller (must be in last section)
    WriteUninstaller "$INSTDIR\uninstall.exe"

SectionEnd

; Post-install
Section "-PostInstall"
    ; Install service if selected
    IfFileExists "$INSTDIR\CleanupService.exe" 0 +2
    ExecWait '"$INSTDIR\CleanupService.exe" install'

    ; Start service
    IfFileExists "$INSTDIR\CleanupService.exe" 0 +2
    ExecWait 'net start TPLinkShutdownCleanup'
SectionEnd

; Uninstaller Section
Section "Uninstall"
    ; Show uninstall confirmation
    MessageBox MB_OKCANCEL "Are you sure you want to uninstall Broadband Dial Tool?$\n$\nThis will:$\n  - Stop and remove the cleanup service$\n  - Delete all program files$\n  - Remove shortcuts and registry entries$\n$\nNote: Your router configuration will be kept." IDCANCEL cancel_uninstall

    ; Set details view
    SetDetailsView show

    ; Stop and remove service
    DetailPrint "=========================================="
    DetailPrint "Step 1: Stopping cleanup service..."
    DetailPrint "=========================================="

    nsExec::ExecToLog 'net stop TPLinkShutdownCleanup'
    Pop $0
    Sleep 3000

    DetailPrint "Removing cleanup service..."
    IfFileExists "$INSTDIR\CleanupService.exe" 0 service_removed
    ExecWait '"$INSTDIR\CleanupService.exe" remove'
    Sleep 2000

    service_removed:

    ; Kill running processes
    DetailPrint ""
    DetailPrint "=========================================="
    DetailPrint "Step 2: Stopping running processes..."
    DetailPrint "=========================================="

    nsExec::ExecToLog 'taskkill /F /IM TP-Link_Dialer.exe'
    nsExec::ExecToLog 'taskkill /F /IM CleanupService.exe'
    Sleep 2000

    ; Delete uninstaller first (while it's still running)
    DetailPrint ""
    DetailPrint "=========================================="
    DetailPrint "Step 3: Removing uninstaller..."
    DetailPrint "=========================================="

    Delete "$INSTDIR\uninstall.exe"

    ; Delete files and directories
    DetailPrint ""
    DetailPrint "=========================================="
    DetailPrint "Step 4: Removing program files..."
    DetailPrint "=========================================="

    RMDir /r "$INSTDIR"

    ; Wait a bit for file system to update
    Sleep 1000

    ; Check if directory was removed
    IfFileExists "$INSTDIR" dir_not_removed
    DetailPrint "Program files removed successfully"
    Goto shortcuts_removed

    dir_not_removed:
    DetailPrint "Warning: Some files may still exist. This is usually safe."
    Goto shortcuts_removed

    shortcuts_removed:

    ; Delete shortcuts
    DetailPrint ""
    DetailPrint "=========================================="
    DetailPrint "Step 5: Removing shortcuts..."
    DetailPrint "=========================================="

    Delete "$DESKTOP\Broadband Dial Tool.lnk"
    RMDir /r "$SMPROGRAMS\Broadband Dial Tool"

    DetailPrint "Shortcuts removed"

    ; Delete registry keys
    DetailPrint ""
    DetailPrint "=========================================="
    DetailPrint "Step 6: Cleaning registry..."
    DetailPrint "=========================================="

    DeleteRegKey HKLM "Software\TPLinkDialer"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TPLinkDialer"

    DetailPrint "Registry cleaned"

    ; Show success message
    DetailPrint ""
    DetailPrint "=========================================="
    DetailPrint "Uninstallation completed!"
    DetailPrint "=========================================="

    MessageBox MB_OK "Broadband Dial Tool has been uninstalled successfully!$\n$\nRemoved:$\n  - Program files and cleanup service$\n  - Desktop and start menu shortcuts$\n  - Registry entries$\n$\nKept:$\n  - Configuration file: $%USERPROFILE%\.tplink_dialer\config.json$\n  - Service logs: $%TEMP%\tplink_cleanup\"

    cancel_uninstall:
    Abort
SectionEnd

; Component Descriptions
LangString DESC_SecMain ${LANG_English} "Broadband dial main program"
LangString DESC_SecService ${LANG_English} "Background cleanup service (auto clear router account on shutdown)"
LangString DESC_SecBrowser ${LANG_English} "Playwright browser component (required)"

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecMain} $(DESC_SecMain)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecService} $(DESC_SecService)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecBrowser} $(DESC_SecBrowser)
!insertmacro MUI_FUNCTION_DESCRIPTION_END
