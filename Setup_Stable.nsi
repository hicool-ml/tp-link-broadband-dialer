; TPLink Dialer - Stable Setup Script
; Fixed installer integrity check issue

!include "MUI2.nsh"
!include "x64.nsh"

; Installer Configuration
Name "Broadband Dial Tool v2.1"
OutFile "Release\Setup.exe"
InstallDir "$PROGRAMFILES64\TPLinkDialer"
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
!define MUI_FINISHPAGE_RUN_TEXT "启动宽带拨号"
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

    ; Install icon files
    File "app.ico"
    File "online.ico"
    File "offline.ico"
    File "connecting.ico"
    File "error.ico"

    ; Create desktop shortcut
    CreateShortCut "$DESKTOP\宽带拨号.lnk" "$INSTDIR\TP-Link_Dialer.exe" "" "$INSTDIR\app.ico" 0

    ; Create start menu shortcuts
    CreateDirectory "$SMPROGRAMS\宽带拨号"
    CreateShortCut "$SMPROGRAMS\宽带拨号\宽带拨号.lnk" "$INSTDIR\TP-Link_Dialer.exe" "" "$INSTDIR\app.ico" 0
    CreateShortCut "$SMPROGRAMS\宽带拨号\卸载.lnk" "$INSTDIR\uninstall.exe"

    ; Write registry
    WriteRegStr HKLM "Software\TPLinkDialer" "InstallPath" $INSTDIR
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TPLinkDialer" "DisplayName" "宽带拨号"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TPLinkDialer" "UninstallString" "$INSTDIR\uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TPLinkDialer" "Publisher" "Kilo Code"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TPLinkDialer" "DisplayVersion" "2.1.0.0"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TPLinkDialer" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TPLinkDialer" "NoRepair" 1

SectionEnd

Section "Cleanup Service" SecService
    SectionIn RO

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
    DetailPrint ""
    DetailPrint "=========================================="
    DetailPrint "Step 6: Installing cleanup service..."
    DetailPrint "=========================================="

    ; Install cleanup service
    IfFileExists "$INSTDIR\CleanupService.exe" 0 service_installed
    DetailPrint "Installing cleanup service..."
    ExecWait '"$INSTDIR\CleanupService.exe" install'
    Pop $0
    DetailPrint "Service install result: $0"

    service_installed:

    ; Start service
    DetailPrint ""
    DetailPrint "=========================================="
    DetailPrint "Step 7: Starting cleanup service..."
    DetailPrint "=========================================="

    DetailPrint "Starting TPLinkShutdownCleanup service..."
    nsExec::ExecToLog 'net start TPLinkShutdownCleanup'
    Pop $0

    ; Wait a bit for service to start
    Sleep 3000

    ; Verify service is running
    nsExec::ExecToLog 'sc query TPLinkShutdownCleanup'
    Pop $0

    DetailPrint ""
    DetailPrint "=========================================="
    DetailPrint "Installation Complete!"
    DetailPrint "=========================================="
SectionEnd

; Uninstaller Section
Section "Uninstall"
    ; Show uninstall confirmation
    MessageBox MB_OKCANCEL "确定要卸载宽带拨号吗？$\n$\n这将：$\n  - 停止并移除清理服务$\n  - 删除所有程序文件$\n  - 移除快捷方式和注册表项$\n$\n注意：您的路由器配置将被保留。" IDCANCEL cancel_uninstall

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

    Delete "$DESKTOP\宽带拨号.lnk"
    RMDir /r "$SMPROGRAMS\宽带拨号"

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
