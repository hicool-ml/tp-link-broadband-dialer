; TP-Link Broadband Dialer - Setup Script (RunOnce机制)
; 企业级稳定方案 - 微软官方推荐
; UTF-8 with BOM encoding

Unicode true
RequestExecutionLevel admin

!define PRODUCT_NAME "TP-Link Broadband Dialer"
!define PRODUCT_VERSION "3.0.0"
!define PRODUCT_PUBLISHER "Hicool & CMCC (scerp@outlook.com)"

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "Broadband_Dialer_Setup_v3.0.0.exe"
InstallDir "$PROGRAMFILES\Broadband_Dialer"
InstallDirRegKey HKLM "Software\Broadband_Dialer" ""

!include "MUI2.nsh"

; ============================================
; 安装程序界面配置
; ============================================

; 定义安装程序信息
!define MUI_ABORTWARNING
!define MUI_WELCOMEPAGE_TITLE "欢迎使用 TP-Link 宽带拨号助手 v3.0.0"
!define MUI_WELCOMEPAGE_TEXT "本程序将安装 TP-Link 宽带拨号助手到您的计算机。$\r$\n$\r$\n本软件采用 RunOnce 机制，可在关机、重启、注销后自动清理路由器账号密码。$\r$\n$\r$\n$_CLICK"

; 完成页面配置
!define MUI_FINISHPAGE_TITLE "安装完成"
!define MUI_FINISHPAGE_TEXT "TP-Link 宽带拨号助手 v3.0.0 已成功安装到您的计算机。$\r$\n$\r$\n✅ RunOnce 清理机制已激活$\r$\n✅ 下次启动时将自动执行路由器清理$\r$\n$\r$\n点击[完成]按钮退出安装程序。"
!define MUI_FINISHPAGE_LINK "访问 GitHub 项目主页"
!define MUI_FINISHPAGE_LINK_LOCATION "https://github.com/kilocode"

; 安装页面配置
!define MUI_DIRECTORYPAGE_TEXT_TOP "选择安装文件夹。本程序将安装到以下文件夹："
!define MUI_DIRECTORYPAGE_TEXT_DESTINATION "目标文件夹"

; 安装进度页面
!define MUI_INSTFILESPAGE_FINISHHEADER_TEXT "完成"
!define MUI_INSTFILESPAGE_FINISHHEADER_SUBTEXT "安装已完成"
!define MUI_INSTFILESPAGE_ABORTHEADER_TEXT "安装中止"
!define MUI_INSTFILESPAGE_ABORTHEADER_SUBTEXT "安装未能成功完成"

; ============================================
; 插入语言（必须在页面定义之后）
; ============================================
!insertmacro MUI_LANGUAGE "SimpChinese"

; ============================================
; 安装页面顺序
; ============================================
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "license.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; ============================================
; 卸载页面顺序
; ============================================
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

Section "Main Section" SEC01

SetOutPath "$INSTDIR"

; ============================================
; 复制程序文件
; ============================================
DetailPrint "正在复制程序文件..."
File "/oname=broadband_dialer.exe" "dist\broadband_dialer.exe"
DetailPrint "  ✓ broadband_dialer.exe"

File "/oname=cleanup_http.exe" "dist\cleanup_http.exe"
DetailPrint "  ✓ cleanup_http.exe"

File "/oname=cleanup.ps1" "cleanup.ps1"
DetailPrint "  ✓ cleanup.ps1"

; ============================================
; 创建快捷方式
; ============================================
DetailPrint "正在创建快捷方式..."
CreateShortCut "$DESKTOP\宽带连接.lnk" "$INSTDIR\broadband_dialer.exe"
DetailPrint "  ✓ 桌面快捷方式：宽带连接"

CreateDirectory "$SMPROGRAMS\Broadband_Dialer"
CreateShortCut "$SMPROGRAMS\Broadband_Dialer\宽带拨号助手.lnk" "$INSTDIR\broadband_dialer.exe"
CreateShortCut "$SMPROGRAMS\Broadband_Dialer\卸载.lnk" "$INSTDIR\uninstall.exe"
DetailPrint "  ✓ 开始菜单快捷方式"

; ============================================
; 创建日志目录
; ============================================
DetailPrint "正在创建日志目录..."
CreateDirectory "$WINDIR\..\ProgramData\BroadbandDialer"
DetailPrint "  ✓ 日志目录：C:\ProgramData\BroadbandDialer"

; ============================================
; 写入卸载信息
; ============================================
DetailPrint "正在注册卸载信息..."
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Broadband_Dialer" "DisplayName" "${PRODUCT_NAME}"
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Broadband_Dialer" "DisplayVersion" "${PRODUCT_VERSION}"
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Broadband_Dialer" "Publisher" "${PRODUCT_PUBLISHER}"
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Broadband_Dialer" "UninstallString" "$INSTDIR\uninstall.exe"
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Broadband_Dialer" "DisplayIcon" "$INSTDIR\broadband_dialer.exe"
WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Broadband_Dialer" "NoModify" 1
WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Broadband_Dialer" "NoRepair" 1
WriteUninstaller "$INSTDIR\uninstall.exe"
DetailPrint "  ✓ 卸载信息已注册"

; ============================================
; 注册 RunOnce 清理机制（核心功能）
; ============================================
DetailPrint ""
DetailPrint "========================================"
DetailPrint "  注册 RunOnce 清理机制"
DetailPrint "========================================"
DetailPrint "正在注册 RunOnce 清理任务..."
DetailPrint "  • 机制：下次启动自动执行路由器清理"
DetailPrint "  • 触发：关机/重启/注销前自动注册"
DetailPrint "  • 执行：下次开机时自动运行"

ExecWait 'powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File "$INSTDIR\cleanup.ps1"'

DetailPrint ""
DetailPrint "✓ RunOnce 清理机制已激活！"
DetailPrint "✓ 下次启动时将自动清理路由器"
DetailPrint ""
DetailPrint "========================================"
DetailPrint ""

SectionEnd

Section "Uninstall"

; ============================================
; 显示卸载信息
; ============================================
DetailPrint ""
DetailPrint "========================================"
DetailPrint "  开始卸载 TP-Link 宽带拨号助手"
DetailPrint "========================================"
DetailPrint ""

; ============================================
; 删除 RunOnce 注册表项
; ============================================
DetailPrint "正在删除 RunOnce 注册表项..."
DeleteRegValue HKLM "Software\Microsoft\Windows\CurrentVersion\RunOnce" "TPLinkCleanup"
DetailPrint "  ✓ RunOnce 注册表项已删除"

; ============================================
; 删除快捷方式
; ============================================
DetailPrint "正在删除快捷方式..."
Delete "$DESKTOP\宽带连接.lnk"
DetailPrint "  ✓ 桌面快捷方式已删除"

Delete "$SMPROGRAMS\Broadband_Dialer\宽带拨号助手.lnk"
Delete "$SMPROGRAMS\Broadband_Dialer\卸载.lnk"
RMDir "$SMPROGRAMS\Broadband_Dialer"
DetailPrint "  ✓ 开始菜单快捷方式已删除"

; ============================================
; 删除程序文件
; ============================================
DetailPrint "正在删除程序文件..."
Delete "$INSTDIR\broadband_dialer.exe"
DetailPrint "  ✓ broadband_dialer.exe 已删除"

Delete "$INSTDIR\cleanup_http.exe"
DetailPrint "  ✓ cleanup_http.exe 已删除"

Delete "$INSTDIR\cleanup.ps1"
DetailPrint "  ✓ cleanup.ps1 已删除"

Delete "$INSTDIR\uninstall.exe"
DetailPrint "  ✓ uninstall.exe 已删除"

; ============================================
; 删除配置文件（可选）
; ============================================
DetailPrint "正在删除配置文件..."
Delete "$INSTDIR\config.json"
DetailPrint "  ✓ config.json 已删除"

; ============================================
; 删除卸载信息
; ============================================
DetailPrint "正在删除卸载信息..."
DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Broadband_Dialer"
DeleteRegKey HKLM "Software\Broadband_Dialer"
DetailPrint "  ✓ 注册表项已删除"

; ============================================
; 删除安装目录
; ============================================
DetailPrint "正在删除安装目录..."
RMDir "$INSTDIR"
DetailPrint "  ✓ 安装目录已删除"

; ============================================
; 询问是否删除日志文件
; ============================================
DetailPrint ""
DetailPrint "========================================"
MessageBox MB_YESNO "是否同时删除日志文件？$\r$\n$\r$\n日志位置：C:\ProgramData\BroadbandDialer" IDNO SkipLogDelete

DetailPrint "正在删除日志目录..."
RMDir /r "$WINDIR\..\ProgramData\BroadbandDialer"
DetailPrint "  ✓ 日志目录已删除"

SkipLogDelete:
DetailPrint ""
DetailPrint "========================================"
DetailPrint "  卸载完成！"
DetailPrint "========================================"
DetailPrint ""

SectionEnd
