; 宽带拨号助手 - HTTP API版本
; NSIS安装脚本

!include "MUI2.nsh"
!include "x64.nsh"

; ============================================
; 安装程序配置
; ============================================
Name "宽带拨号助手"
OutFile "宽带拨号助手_Setup.exe"
InstallDir "$PROGRAMFILES\宽带拨号助手"
RequestExecutionLevel admin ; 需要管理员权限

; 版本信息
VIProductVersion "1.0.0.0"
VIAddVersionKey "ProductName" "宽带拨号助手"
VIAddVersionKey "CompanyName" "Your Company"
VIAddVersionKey "FileDescription" "宽带拨号助手安装程序"
VIAddVersionKey "FileVersion" "1.0.0.0"
VIAddVersionKey "ProductVersion" "1.0.0.0"
VIAddVersionKey "LegalCopyright" "2025"

; 压缩设置
SetCompressor /SOLID lzma
SetCompressorDictSize 32

; ============================================
; 页面设置
; ============================================
; 欢迎页面
!insertmacro MUI_PAGE_WELCOME

; 许可协议页面（可选）
Page custom CheckAdminRights ShowAdminError

; 组件页面
!insertmacro MUI_PAGE_COMPONENTS

; 目录选择页面
!insertmacro MUI_PAGE_DIRECTORY

; 安装过程页面
!insertmacro MUI_PAGE_INSTFILES

; 完成页面
!define MUI_FINISHPAGE_TITLE "安装完成"
!define MUI_FINISHPAGE_TEXT "宽带拨号助手已成功安装！$\n$\n点击【完成】按钮退出安装向导。"
!define MUI_FINISHPAGE_RUN "$INSTDIR\宽带拨号助手.exe"
!define MUI_FINISHPAGE_RUN_TEXT "启动宽带拨号助手"
!define MUI_FINISHPAGE_SHOWREADME_NOTCHECKED
!define MUI_FINISHPAGE_SHOWREADME_TEXT "查看服务状态"
!define MUI_FINISHPAGE_SHOWREADME_FUNCTION ShowServiceStatus
!insertmacro MUI_PAGE_FINISH

; 卸载页面
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; 语言
!insertmacro MUI_LANGUAGE "SimpChinese"

; ============================================
; 自定义页面函数
; ============================================

Var AdminRightsDialog
Var AdminRightsLabel

Function CheckAdminRights
  ; 检查管理员权限
  ClearErrors
  UserInfo::GetName
  Pop $0
  UserInfo::GetAccountType
  Pop $1

  ${If} $1 != "admin" ; 非管理员
    ; 创建警告对话框
    nsDialogs::Create 1018 ${NSIS_DEFAULTPARENTWINDOW} $AdminRightsDialog \
      $PLUGINSDIR\modern-wizard.bmp "" \
      30 110u

    Pop $0

    ; 背景颜色
    SetCtlColors $AdminRightsDialog "" "0xFFFF99"

    ; 标题
    ${NSD_CreateLabel} $AdminRightsLabel $AdminRightsDialog \
      "" 20u 30u 100% 30u \
      "⚠️ 警告：检测到未使用管理员权限运行安装程序"

    Pop $0

    ; 说明文字
    ${NSD_CreateLabel} $0 $AdminRightsDialog \
      "" 20u 70u 100% 50u \
      "本安装程序需要管理员权限才能正常工作。$\n$\n原因：$\n  • 安装Windows服务需要管理员权限$\n  • 修改系统注册表需要管理员权限$\n$\n请：$\n  1. 右键点击安装程序$\n  2. 选择【以管理员身份运行】$\n  3. 重新运行安装程序"

    Pop $0

    ; 退出按钮
    ${NSD_CreateButton} $0 $AdminRightsDialog \
      "" 140u 145u 100u 30u \
      /SD_IDCANCEL \
      "退出安装程序"

    Pop $0
    ${NSD_OnClick} $0 /SD_IDCANCEL nsDialogs::OnBack $AdminRightsDialog

    ; 显示对话框
    EnableWindow $HWNDPARENT 0
    nsDialogs::Show $AdminRightsDialog $HWNDPARENT
    EnableWindow $HWNDPARENT 1

    nsDialogs::Release $AdminRightsDialog

    ; 退出安装程序
    Quit
  ${EndIf}

  Abort
FunctionEnd

Function ShowAdminError
  ; 占位函数，实际处理在CheckAdminRights中
FunctionEnd

Function ShowServiceStatus
  ; 显示服务状态
  ExecShell "sc" "query TPLinkShutdownCleanup" SW_SHOW
FunctionEnd

; ============================================
; 安装部分
; ============================================

Section "主程序" SecMain
  SectionIn RO

  SetOutPath $INSTDIR

  ; 复制主程序文件
  File "/oname=宽带拨号助手.exe" "dist\宽带拨号助手.exe"

  ; 复制托盘图标文件
  File "app.ico"
  File "online.ico"
  File "offline.ico"
  File "connecting.ico"
  File "error.ico"

  ; 创建桌面快捷方式
  CreateShortcut "$DESKTOP\宽带拨号助手.lnk" "$INSTDIR\宽带拨号助手.exe"

  ; 创建开始菜单
  CreateDirectory "$SMPROGRAMS\宽带拨号助手"
  CreateShortcut "$SMPROGRAMS\宽带拨号助手\宽带拨号助手.lnk" "$INSTDIR\宽带拨号助手.exe"
  CreateShortcut "$SMPROGRAMS\宽带拨号助手\服务状态.lnk" "sc.exe" 'query TPLinkShutdownCleanup' "" SW_SHOWMINIMIZE
  CreateShortcut "$SMPROGRAMS\宽带拨号助手\卸载.lnk" "$INSTDIR\uninstall.exe"

  ; 写入注册表
  WriteRegStr HKLM "Software\宽带拨号助手" "Install_Dir" $INSTDIR
  WriteRegStr HKLM "Software\宽带拨号助手" "Version" "1.0.0"

  ; 写入卸载信息
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\宽带拨号助手" "DisplayName" "宽带拨号助手"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\宽带拨号助手" "DisplayVersion" "1.0.0"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\宽带拨号助手" "Publisher" "Your Company"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\宽带拨号助手" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\宽带拨号助手" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\宽带拨号助手" "NoRepair" 1

SectionEnd

Section "系统服务" SecService
  SectionIn RO

  SetOutPath $INSTDIR

  ; 复制服务程序
  File "/oname=TPLinkCleanupService.exe" "dist\TPLinkCleanupService.exe"

  ; 安装Windows服务
  DetailPrint "=========================================="
  DetailPrint "正在安装关机清理服务..."
  DetailPrint "=========================================="

  ; 执行服务安装命令
  nsExec::ExecToLog '"$INSTDIR\TPLinkCleanupService.exe" install'
  Pop $0

  ; 启动服务
  DetailPrint "正在启动服务..."
  nsExec::ExecToLog 'net start TPLinkShutdownCleanup'
  Pop $1

  DetailPrint "=========================================="
  DetailPrint "服务安装完成！"
  DetailPrint "=========================================="

  ; 验证服务状态
  nsExec::ExecToLog 'sc query TPLinkShutdownCleanup'

SectionEnd

; ============================================
; 后安装部分
; ============================================

Section -Post
  ; 写入卸载程序
  WriteUninstaller "$INSTDIR\uninstall.exe"

  ; 显示完成信息
  DetailPrint "=========================================="
  DetailPrint "安装完成！"
  DetailPrint "=========================================="
  DetailPrint "主程序: $INSTDIR\宽带拨号助手.exe"
  DetailPrint "服务: TPLinkShutdownCleanup"
  DetailPrint ""
  DetailPrint "功能说明:"
  DetailPrint "  • 主程序: 宽带拨号连接"
  DetailPrint "  • 服务: 关机时自动清理路由器账号"
  DetailPrint ""
  DetailPrint "日志位置: %TEMP%\tplink_cleanup\"
  DetailPrint "=========================================="
SectionEnd

; ============================================
; 卸载部分
; ============================================

Section "Uninstall"
  ; 设置详情视图
  SetDetailsView show

  ; ============================================
  ; 步骤1: 停止并卸载服务
  ; ============================================
  DetailPrint "=========================================="
  DetailPrint "步骤 1/5: 停止并卸载服务..."
  DetailPrint "=========================================="

  ; 停止服务
  nsExec::ExecToLog 'net stop TPLinkShutdownCleanup'
  Pop $0
  Sleep 1000

  ; 卸载服务
  DetailPrint "正在卸载服务..."
  nsExec::ExecToLog '"$INSTDIR\TPLinkCleanupService.exe" remove'
  Pop $0
  Sleep 1000

  ; ============================================
  ; 步骤2: 停止运行进程
  ; ============================================
  DetailPrint ""
  DetailPrint "步骤 2/5: 停止运行进程..."

  nsExec::ExecToLog 'taskkill /F /IM 宽带拨号助手.exe'
  nsExec::ExecToLog 'taskkill /F /IM TPLinkCleanupService.exe'
  Sleep 1000

  ; ============================================
  ; 步骤3: 删除文件
  ; ============================================
  DetailPrint ""
  DetailPrint "步骤 3/5: 删除程序文件..."

  Delete /REBOOTOK "$INSTDIR\宽带拨号助手.exe"
  Delete /REBOOTOK "$INSTDIR\TPLinkCleanupService.exe"
  Delete /REBOOTOK "$INSTDIR\app.ico"
  Delete /REBOOTOK "$INSTDIR\online.ico"
  Delete /REBOOTOK "$INSTDIR\offline.ico"
  Delete /REBOOTOK "$INSTDIR\connecting.ico"
  Delete /REBOOTOK "$INSTDIR\error.ico"
  Delete /REBOOTOK "$INSTDIR\uninstall.exe"

  RMDir /REBOOTOK "$INSTDIR"

  ; ============================================
  ; 步骤4: 删除快捷方式
  ; ============================================
  DetailPrint ""
  DetailPrint "步骤 4/5: 删除快捷方式..."

  Delete "$DESKTOP\宽带拨号助手.lnk"
  RMDir /r "$SMPROGRAMS\宽带拨号助手"

  ; ============================================
  ; 步骤5: 清理注册表
  ; ============================================
  DetailPrint ""
  DetailPrint "步骤 5/5: 清理注册表..."

  DeleteRegKey HKLM "Software\宽带拨号助手"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\宽带拨号助手"

  ; ============================================
  ; 完成信息
  ; ============================================
  DetailPrint ""
  DetailPrint "=========================================="
  DetailPrint "卸载完成！"
  DetailPrint "=========================================="

  MessageBox MB_OK "宽带拨号助手已成功卸载。$\n$\n已移除：$\n  • 主程序和服务$\n  • 桌面和开始菜单快捷方式$\n  • 系统注册表项$\n$\n保留：$\n  • 配置文件: %USERPROFILE%\.tplink_dialer\config.json$\n  • 服务日志: %TEMP%\tplink_cleanup\"

SectionEnd

; ============================================
; 组件描述
; ============================================

LangString DESC_SecMain ${LANG_SIMPCHINESE} "主程序：提供图形界面的宽带拨号连接工具"
LangString DESC_SecService ${LANG_SIMPCHINESE} "系统服务：在Windows关机时自动清理路由器账号密码（强烈推荐，防止账号因频繁重启被锁定）"

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SecMain} $(DESC_SecMain)
  !insertmacro MUI_DESCRIPTION_TEXT ${SecService} $(DESC_SecService)
!insertmacro MUI_FUNCTION_DESCRIPTION_END
