; 宽带拨号工具 - 优化安装脚本
; 共享浏览器架构，减小安装包体积

!include "MUI2.nsh"

; 安装程序配置
Name "宽带拨号工具 v2.1"
OutFile "Release\Setup.exe"
InstallDir "$PROGRAMFILES\TPLinkDialer"
InstallDirRegKey HKLM "Software\TPLinkDialer" "InstallPath"
RequestExecutionLevel admin

; 设置压缩算法
SetCompressor /SOLID lzma
SetCompressorDictSize 32

; 版本信息
VIProductVersion "2.1.0.0"
VIAddVersionKey "ProductName" "宽带拨号工具"
VIAddVersionKey "CompanyName" "Kilo Code"
VIAddVersionKey "FileDescription" "TP-Link宽带拨号工具安装程序"
VIAddVersionKey "FileVersion" "2.1.0.0"
VIAddVersionKey "ProductVersion" "2.1.0.0"
VIAddVersionKey "LegalCopyright" "© 2026"

; 页面配置
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "license.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES

; 完成页面配置
!define MUI_FINISHPAGE_RUN "$INSTDIR\TP-Link_Dialer.exe"
!define MUI_FINISHPAGE_RUN_TEXT "启动宽带拨号工具"
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; 语言设置
!insertmacro MUI_LANGUAGE "SimpChinese"

; 安装组件
Section "主程序" SecMain
    SectionIn RO

    SetOutPath $INSTDIR

    ; 安装主程序
    File /r "dist\TP-Link_Dialer\*"

    ; 创建桌面快捷方式
    CreateShortCut "$DESKTOP\宽带拨号工具.lnk" "$INSTDIR\TP-Link_Dialer.exe" "" "$INSTDIR\app.ico" 0

    ; 创建开始菜单快捷方式
    CreateDirectory "$SMPROGRAMS\宽带拨号工具"
    CreateShortCut "$SMPROGRAMS\宽带拨号工具\宽带拨号工具.lnk" "$INSTDIR\TP-Link_Dialer.exe" "" "$INSTDIR\app.ico" 0
    CreateShortCut "$SMPROGRAMS\宽带拨号工具\卸载.lnk" "$INSTDIR\uninstall.exe"

    ; 写入注册表
    WriteRegStr HKLM "Software\TPLinkDialer" "InstallPath" $INSTDIR
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TPLinkDialer" "DisplayName" "宽带拨号工具"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TPLinkDialer" "UninstallString" "$INSTDIR\uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TPLinkDialer" "Publisher" "Kilo Code"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TPLinkDialer" "DisplayVersion" "2.1.0.0"

SectionEnd

Section "后台清理服务" SecService
    SetOutPath $INSTDIR

    ; 安装清理服务
    File /r "dist\CleanupService\*"

    ; 安装服务安装器
    File "dist\ServiceInstaller.exe"

    ; 写入卸载命令
    WriteRegStr HKLM "Software\TPLinkDialer" "CleanupService" "$INSTDIR\CleanupService.exe"

SectionEnd

Section "Playwright 浏览器 (必需)" SecBrowser
    SectionIn RO

    SetOutPath $INSTDIR

    ; 安装共享浏览器（这是最大的组件，约500MB）
    ; 注意：这里假设浏览器已经准备好在 chrome-win64 目录
    ; 可以使用 playwright install chromium 命令下载

    File /r "chrome-win64"

    ; 写入浏览器安装标记
    WriteRegStr HKLM "Software\TPLinkDialer" "BrowserInstalled" "1"

SectionEnd

; 安装后运行
Section "-PostInstall"
    ; 安装服务（如果选择了）
    IfFileExists "$INSTDIR\CleanupService.exe" 0 +2
    ExecWait '"$INSTDIR\CleanupService.exe" install'

    ; 启动服务
    IfFileExists "$INSTDIR\CleanupService.exe" 0 +2
    ExecWait 'net start TPLinkShutdownCleanup'
SectionEnd

; 卸载部分
Section "Uninstall"
    ; 停止并卸载服务
    IfFileExists "$INSTDIR\CleanupService.exe" 0 +3
    ExecWait 'net stop TPLinkShutdownCleanup'
    IfFileExists "$INSTDIR\CleanupService.exe" 0 +3
    ExecWait '"$INSTDIR\CleanupService.exe" remove'

    ; 删除文件和目录
    RMDir /r "$INSTDIR"

    ; 删除快捷方式
    Delete "$DESKTOP\宽带拨号工具.lnk"
    RMDir /r "$SMPROGRAMS\宽带拨号工具"

    ; 删除注册表项
    DeleteRegKey HKLM "Software\TPLinkDialer"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\TPLinkDialer"

SectionEnd

; 组件描述
LangString DESC_SecMain ${LANG_SimpChinese} "宽带拨号主程序"
LangString DESC_SecService ${LANG_SimpChinese} "后台清理服务（关机时自动清理路由器账号）"
LangString DESC_SecBrowser ${LANG_SimpChinese} "Playwright 浏览器组件（程序运行必需）"

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecMain} $(DESC_SecMain)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecService} $(DESC_SecService)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecBrowser} $(DESC_SecBrowser)
!insertmacro MUI_FUNCTION_DESCRIPTION_END
