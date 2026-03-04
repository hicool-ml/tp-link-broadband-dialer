; TP-Link Broadband Dialer Tool - Installer Script
; Compiled with NSIS (Nullsoft Scriptable Install System)
; Encoding: ANSI

; Get environment variables
!define LOCALAPPDATA $%LOCALAPPDATA%

; Application Information
!define APP_NAME "TP-Link宽带拨号"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "Kilo Code"
!define APP_EXE "TP-Link_Dialer.exe"
!define APP_DIR "TP-Link_Dialer"
!define APP_ICON "app.ico"

; Installer Configuration
Name "${APP_NAME}"
OutFile "发布包\TP-Link_Dialer_Setup.exe"
InstallDir "$PROGRAMFILES64\${APP_DIR}"
InstallDirRegKey HKLM "Software\${APP_DIR}" "InstallPath"
RequestExecutionLevel admin
SetCompressor /SOLID lzma
ShowInstDetails show
ShowUninstDetails show

; Interface Settings
!include "MUI2.nsh"

!define MUI_ABORTWARNING
!define MUI_COMPONENTSPAGE_NODESC

; License Data
LicenseData "license.txt"

; Welcome Page
!insertmacro MUI_PAGE_WELCOME
; License Page
!insertmacro MUI_PAGE_LICENSE "license.txt"
; Directory Page
!insertmacro MUI_PAGE_DIRECTORY
; Installation Page
!insertmacro MUI_PAGE_INSTFILES
; Finish Page
!insertmacro MUI_PAGE_FINISH

; Language Settings (Must be after all pages)
!insertmacro MUI_LANGUAGE "SimpChinese"

; Installation Section
Section "Main Program" SecMain
  SectionIn RO
  
  SetOutPath $INSTDIR
  
  DetailPrint "Copying program files..."
  
  ; Copy main executable
  File "dist\${APP_EXE}"
  
  ; Copy icon files
  File "app.ico"
  File "connecting.ico"
  File "error.ico"
  File "offline.ico"
  File "online.ico"
  
  ; Copy documentation
  File "license.txt"
  
  ; Copy Playwright browser drivers
  DetailPrint "Copying Playwright browser drivers..."
  SetOutPath $INSTDIR\playwright-drivers
  File /r "${LOCALAPPDATA}\ms-playwright\chromium-1208\*.*"
  
  ; Set environment variable for Playwright browsers path
  DetailPrint "Configuring Playwright browser path..."
  WriteRegStr HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "PLAYWRIGHT_BROWSERS_PATH" "$INSTDIR\playwright-drivers"
  
  SetOutPath $INSTDIR
  
  ; Create desktop shortcut
  DetailPrint "Creating desktop shortcut..."
  CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\${APP_ICON}" 0
  
  ; Create start menu shortcuts
  DetailPrint "Creating start menu shortcuts..."
  CreateDirectory "$SMPROGRAMS\${APP_NAME}"
  CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\${APP_ICON}" 0
  CreateShortCut "$SMPROGRAMS\${APP_NAME}\Uninstall.lnk" "$INSTDIR\uninstall.exe"
  
  ; Write registry entries
  DetailPrint "Writing registry entries..."
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
  
  DetailPrint "Installation completed!"
SectionEnd

; Uninstallation Section
Section "Uninstall"
  ; Delete files
  DetailPrint "Deleting program files..."
  Delete "$INSTDIR\${APP_EXE}"
  Delete "$INSTDIR\${APP_ICON}"
  Delete "$INSTDIR\connecting.ico"
  Delete "$INSTDIR\error.ico"
  Delete "$INSTDIR\offline.ico"
  Delete "$INSTDIR\online.ico"
  Delete "$INSTDIR\license.txt"
  Delete "$INSTDIR\uninstall.exe"
  
  ; Delete Playwright browser drivers
  DetailPrint "Deleting Playwright browser drivers..."
  RMDir /r "$INSTDIR\playwright-drivers"
  
  ; Remove environment variable
  DetailPrint "Removing Playwright browser path environment variable..."
  DeleteRegValue HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "PLAYWRIGHT_BROWSERS_PATH"
  
  ; Delete shortcuts
  DetailPrint "Deleting shortcuts..."
  Delete "$DESKTOP\${APP_NAME}.lnk"
  RMDir /r "$SMPROGRAMS\${APP_NAME}"
  
  ; Delete registry entries
  DetailPrint "Cleaning registry..."
  DeleteRegKey HKLM "Software\${APP_DIR}"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
  
  ; Delete installation directory
  DetailPrint "Deleting installation directory..."
  RMDir "$INSTDIR"
  
  DetailPrint "Uninstallation completed!"
SectionEnd
