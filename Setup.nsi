; TPLink Dialer - Optimized Setup Script
; Shared Browser Architecture

!include "MUI2.nsh"

; Installer Configuration
Name "Broadband Dial Tool v2.1.1"
OutFile "Release\Setup.exe"
InstallDir "$PROGRAMFILES64\TPLinkDialer"
InstallDirRegKey HKLM "Software\TPLinkDialer" "InstallPath"
RequestExecutionLevel admin

; Set compressor
SetCompressor /SOLID lzma
SetCompressorDictSize 32

; Version Info
VIProductVersion "2.1.1.0"
VIAddVersionKey "ProductName" "Broadband Dial Tool"
VIAddVersionKey "CompanyName" "Kilo Code"
VIAddVersionKey "FileDescription" "TP-Link Broadband Dial Tool Installer"
VIAddVersionKey "FileVersion" "2.1.1.0"
VIAddVersionKey "ProductVersion" "2.1.1.0"
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
!define MUI_FINISHPAGE_SHOWREADME
!define MUI_FINISHPAGE_SHOWREADME_TEXT "View Service Status"
!define MUI_FINISHPAGE_SHOWREADME_FUNCTION ShowServiceStatus
!insertmacro MUI_PAGE_FINISH

; Uninstall Pages
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Language
!insertmacro MUI_LANGUAGE "English"

; Function to show service status after installation
Function ShowServiceStatus
  ExecShell "sc" "query TPLinkShutdownCleanup" SW_SHOW
FunctionEnd

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

SectionEnd

Section "Cleanup Service" SecService
    SetOutPath $INSTDIR

    ; Install cleanup service scripts
    File "CleanupService.py"
    File "config_manager.py"
    File "browser_manager.py"

    ; Install cleanup worker executable
    File "dist\cleanup_worker.exe"

    ; Install portable Python runtime
    File /r "python"

    ; Write service registry
    WriteRegStr HKLM "Software\TPLinkDialer" "CleanupService" "$INSTDIR\CleanupService.py"

SectionEnd

Section "Playwright Browser (Required)" SecBrowser
    SectionIn RO

    SetOutPath $INSTDIR

    ; Install shared browser
    File /r "chrome-win64"

    ; Write browser install flag
    WriteRegStr HKLM "Software\TPLinkDialer" "BrowserInstalled" "1"

    ; Write uninstaller (must be in last section)
    WriteUninstaller "$INSTDIR\uninstall.exe"

SectionEnd

; Post-install
Section "-PostInstall"
    ; Install and start service if selected
    IfFileExists "$INSTDIR\CleanupService.py" 0 no_service
        DetailPrint "=========================================="
        DetailPrint "Installing cleanup service..."
        DetailPrint "=========================================="

        ; Install service using portable Python
        ExecWait '"$INSTDIR\python\python.exe" "$INSTDIR\CleanupService.py" install' $0
        DetailPrint "Service install result: $0"

        ; Start service
        DetailPrint "Starting cleanup service..."
        ExecWait 'net start TPLinkShutdownCleanup' $1
        DetailPrint "Service start result: $1"

        ; Verify service status
        nsExec::ExecToLog 'sc query TPLinkShutdownCleanup'
        Pop $2

        DetailPrint "=========================================="
        DetailPrint "Service installation completed!"
        DetailPrint "The service will automatically clear your router"
        DetailPrint "account when Windows shuts down."
        DetailPrint "=========================================="

        MessageBox MB_OK "Cleanup service has been installed and started.$\n$\nThis service will automatically clear your router account on Windows shutdown, preventing ISP account locking due to frequent reboots.$\n$\nYou can check the service status in Windows Services (TPLinkShutdownCleanup)."

        Goto done
    no_service:
        DetailPrint "Cleanup service not selected (skipped)"
    done:
SectionEnd

; Uninstaller Section
Section "Uninstall"
    ; Show uninstall confirmation
    MessageBox MB_OKCANCEL "Are you sure you want to uninstall Broadband Dial Tool?$\n$\nThis will:$\n  - Stop and remove the cleanup service$\n  - Delete all program files$\n  - Remove shortcuts and registry entries$\n$\nNote: Your router configuration will be kept." IDCANCEL cancel_uninstall

    ; Set details view
    SetDetailsView show

    ; ============================================
    ; Step 1: Stop and remove Windows service
    ; ============================================
    DetailPrint "=========================================="
    DetailPrint "Step 1: Stopping cleanup service..."
    DetailPrint "=========================================="

    ; Try to stop the service
    nsExec::ExecToLog 'net stop TPLinkShutdownCleanup'
    Pop $0
    DetailPrint "Service stop result: $0"
    Sleep 3000

    ; Remove the service
    DetailPrint "Removing cleanup service..."
    IfFileExists "$INSTDIR\CleanupService.py" 0 service_removed
    ExecWait '"$INSTDIR\python\python.exe" "$INSTDIR\CleanupService.py" remove' $0
    DetailPrint "Service remove result: $0"
    Sleep 2000

    service_removed:

    ; ============================================
    ; Step 2: Kill running processes
    ; ============================================
    DetailPrint ""
    DetailPrint "=========================================="
    DetailPrint "Step 2: Stopping running processes..."
    DetailPrint "=========================================="

    nsExec::ExecToLog 'taskkill /F /IM TP-Link_Dialer.exe'
    nsExec::ExecToLog 'taskkill /F /IM CleanupService.exe'
    Sleep 2000

    ; ============================================
    ; Step 3: Delete files and directories
    ; ============================================
    DetailPrint ""
    DetailPrint "=========================================="
    DetailPrint "Step 3: Removing program files..."
    DetailPrint "=========================================="

    ; Delete uninstaller first
    Delete "$INSTDIR\uninstall.exe"

    ; Delete all files and directories
    RMDir /r "$INSTDIR"

    ; Verify deletion
    IfFileExists "$INSTDIR" 0 +3
    DetailPrint "Warning: Some files could not be deleted"
    DetailPrint "Program files removed successfully"

    ; ============================================
    ; Step 4: Delete shortcuts
    ; ============================================
    DetailPrint ""
    DetailPrint "=========================================="
    DetailPrint "Step 4: Removing shortcuts..."
    DetailPrint "=========================================="

    Delete "$DESKTOP\Broadband Dial Tool.lnk"
    RMDir /r "$SMPROGRAMS\Broadband Dial Tool"

    DetailPrint "Shortcuts removed"

    ; ============================================
    ; Step 5: Clean registry
    ; ============================================
    DetailPrint ""
    DetailPrint "=========================================="
    DetailPrint "Step 5: Cleaning registry..."
    DetailPrint "=========================================="

    DeleteRegKey HKLM "Software\TPLinkDialer"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TPLinkDialer"

    DetailPrint "Registry cleaned"

    ; ============================================
    ; Step 6: Show completion message
    ; ============================================
    DetailPrint ""
    DetailPrint "=========================================="
    DetailPrint "Uninstallation completed!"
    DetailPrint "=========================================="

    MessageBox MB_OK "Broadband Dial Tool has been uninstalled successfully.$\n$\nRemoved:$\n  - Program files and cleanup service$\n  - Desktop and start menu shortcuts$\n  - Registry entries$\n$\nKept:$\n  - Configuration file: $%USERPROFILE%\.tplink_dialer\config.json$\n  - Service logs: $%TEMP%\tplink_cleanup\"

    cancel_uninstall:
    Abort
SectionEnd

; Component Descriptions
LangString DESC_SecMain ${LANG_English} "Main dial program with GUI interface"
LangString DESC_SecService ${LANG_English} "Shutdown cleanup service (Recommended: Automatically clears router account on Windows shutdown to prevent account locking)"
LangString DESC_SecBrowser ${LANG_English} "Embedded browser (Required for router communication)"

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecMain} $(DESC_SecMain)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecService} $(DESC_SecService)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecBrowser} $(DESC_SecBrowser)
!insertmacro MUI_FUNCTION_DESCRIPTION_END
