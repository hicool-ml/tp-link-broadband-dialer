; 宽带拨号助手 - NSIS安装脚本

!include "MUI2.nsh"

; 安装程序配置
Name "宽带拨号助手"
OutFile "宽带拨号助手_Setup.exe"
InstallDir "$PROGRAMFILES\宽带拨号助手"
RequestExecutionLevel admin

; 版本信息
VIProductVersion "1.0.0.0"
VIAddVersionKey "ProductName" "宽带拨号助手"
VIAddVersionKey "CompanyName" "Your Company"
VIAddVersionKey "FileDescription" "宽带拨号助手安装程序"
VIAddVersionKey "FileVersion" "1.0.0.0"
VIProductVersion "1.0.0.0"
VIAddVersionKey "LegalCopyright "2025"

; 压缩设置
SetCompressor /SOLID lzma

; 页面
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; 语言
!insertmacro MUI_LANGUAGE "SimpChinese"

; 安装部分
Section "主程序" SecMain
  SectionIn RO
  
  SetOutPath \$INSTDIR
  
  ; 复制主程序
  File /oname=宽带拨号助手.exe "dist\宽带拨号助手.exe"
  
  ; 复制图标
  File "app.ico"
  File "online.ico"
  File "offline.ico"
  File "connecting.ico"
  File "error.ico"
  
  ; 创建快捷方式
  CreateShortcut "\$DESKTOP\宽带拨号助手.lnk" "\$INSTDIR\宽带拨号助手.exe"
  
  ; 开始菜单
  CreateDirectory "\$SMPROGRAMS\宽带拨号助手"
  CreateShortcut "\$SMPROGRAMS\宽带拨号助手\宽带拨号助手.lnk" "\$INSTDIR\宽带拨号助手.exe"
  
  ; 写入注册表
  WriteRegStr HKLM "Software\宽带拨号助手" "Install_Dir" "\$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\宽带拨号助手" "DisplayName" "宽带拨号助手"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\宽带拨号助手" "UninstallString" "\$INSTDIR\uninstall.exe"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\宽带拨号助手" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\宽带拨号助手" "NoRepair" 1
  
  ; 写入卸载程序
  WriteUninstaller "\$INSTDIR\uninstall.exe"
SectionEnd

Section "系统服务" SecService
  SectionIn RO
  
  SetOutPath \$INSTDIR
  
  ; 复制服务程序
  File /oname=TPLinkCleanupService.exe "dist\TPLinkCleanupService.exe"
  
  ; 安装服务
  DetailPrint "正在安装关机清理服务..."
  nsExec::ExecToLog '"\$INSTDIR\TPLinkCleanupService.exe" install'
  
  ; 启动服务
  DetailPrint "正在启动服务..."
  nsExec::ExecToLog 'net start TPLinkShutdownCleanup'
  
SectionEnd

Section -Post
SectionEnd

; 卸载部分
Section "Uninstall"
  ; 停止并卸载服务
  nsExec::ExecToLog 'net stop TPLinkShutdownCleanup'
  Sleep 1000
  nsExec::ExecToLog '"\$INSTDIR\TPLinkCleanupService.exe" remove'
  Sleep 1000
  
  ; 删除文件
  Delete /REBOOTOK "\$INSTDIR\宽带拨号助手.exe"
  Delete /REBOOTOK "\$INSTDIR\TPLinkCleanupService.exe"
  Delete /REBOOTOK "\$INSTDIR\app.ico"
  Delete /REBOOTOK "\$INSTDIR\online.ico"
  Delete /REBOOTOK "\$INSTDIR\offline.ico"
  Delete /REBOOTOK "\$INSTDIR\connecting.ico"
  Delete /REBOOTOK "\$INSTDIR\error.ico"
  Delete /REBOOTOK "\$INSTDIR\uninstall.exe"
  
  ; 删除快捷方式
  Delete "\$DESKTOP\宽带拨号助手.lnk"
  RMDir /r "\$SMPROGRAMS\宽带拨号助手"
  
  ; 删除目录
  RMDir /REBOOTOK "\$INSTDIR"
  
  ; 删除注册表
  DeleteRegKey HKLM "Software\宽带拨号助手"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\宽带拨号助手"
SectionEnd

; 组件描述
LangString DESC_SecMain \${LANG_SIMPCHINESE} "主程序：提供图形界面的宽带拨号连接工具"
LangString DESC_SecService \${LANG_SIMPCHINESE} "系统服务：在Windows关机时自动清理路由器账号密码（强烈推荐）"

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT \${SecMain} \$(DESC_SecMain)
  !insertmacro MUI_DESCRIPTION_TEXT \${SecService} \$(DESC_SecService)
!insertmacro MUI_FUNCTION_DESCRIPTION_END
