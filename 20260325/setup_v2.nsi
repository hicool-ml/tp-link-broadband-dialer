; TP-Link宽带拨号助手 - 安装程序（含关机清理任务）
; UTF-8 with BOM 编码

!define PRODUCT_NAME "TP-Link宽带拨号助手"
!define PRODUCT_VERSION "2.2.0"
!define PRODUCT_PUBLISHER "Kilo Code"
!define PRODUCT_WEB_SITE "https://github.com/kilocode"
!define PRODUCT_DIR_REGKEY "Software\Broadband_Dialer"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"

; 安装配置
Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "Broadband_Dialer_Setup_${PRODUCT_VERSION}.exe"
InstallDir "$PROGRAMFILES\Broadband_Dialer"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

; 现代UI界面
!include "MUI2.nsh"

; 页面定义
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "license.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; 语言设置
!insertmacro MUI_LANGUAGE "SimpChinese"

; 安装区段
Section "MainSection" SEC01
  SetOutPath "$INSTDIR"

  ; 主程序
  File "dist\broadband_dialer.exe"

  ; 清理程序
  File "dist\cleanup_http.exe"
  File "cleanup.ps1"

  ; 创建快捷方式
  CreateDirectory "$SMPROGRAMS\Broadband_Dialer"
  CreateShortCut "$SMPROGRAMS\Broadband_Dialer\宽带拨号助手.lnk" "$INSTDIR\broadband_dialer.exe"
  CreateShortCut "$DESKTOP\宽带拨号助手.lnk" "$INSTDIR\broadband_dialer.exe"

  ; 注册表
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\broadband_dialer.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "Version" "${PRODUCT_VERSION}"

  ; 卸载信息
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayName" "${PRODUCT_NAME}"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegDWORD HKLM "${PRODUCT_UNINST_KEY}" "NoModify" 1
  WriteRegDWORD HKLM "${PRODUCT_UNINST_KEY}" "NoRepair" 1

  ; 写入卸载程序
  WriteUninstaller "$INSTDIR\uninstall.exe"

  ; 创建日志目录
  CreateDirectory "$WINDIR\..\ProgramData\BroadbandDialer"

  ; 创建关机清理任务（重要！）
  DetailPrint "正在创建关机清理任务..."
  ExecWait 'schtasks /Delete /TN "TPLinkCleanup" /F'
  ExecWait 'schtasks /Create /TN "TPLinkCleanup" /TR "powershell.exe -ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File \"$INSTDIR\cleanup.ps1\"" /SC ONEVENT /EC System /MO "*[System[(EventID=1074 or EventID=6006)]]" /RU SYSTEM /RL HIGHEST /F'
  DetailPrint "关机清理任务创建完成！"

SectionEnd

; 卸载区段
Section Uninstall
  ; 删除任务计划
  DetailPrint "正在删除关机清理任务..."
  ExecWait 'schtasks /Delete /TN "TPLinkCleanup" /F'

  ; 删除文件
  Delete "$INSTDIR\broadband_dialer.exe"
  Delete "$INSTDIR\cleanup_http.exe"
  Delete "$INSTDIR\cleanup.ps1"
  Delete "$INSTDIR\config.json"
  Delete "$INSTDIR\uninstall.exe"

  ; 删除快捷方式
  Delete "$DESKTOP\宽带拨号助手.lnk"
  Delete "$SMPROGRAMS\Broadband_Dialer\宽带拨号助手.lnk"
  RMDir "$SMPROGRAMS\Broadband_Dialer"

  ; 删除注册表
  DeleteRegKey HKLM "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"

  ; 删除安装目录
  RMDir "$INSTDIR"
SectionEnd
