# TP-Link 路由器清理触发器（RunOnce 机制）

$ErrorActionPreference = "SilentlyContinue"

$baseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$exe = Join-Path $baseDir "cleanup_http.exe"

$logDir = "C:\ProgramData\BroadbandDialer"
if (-not (Test-Path $logDir)) {
    New-Item -Path $logDir -ItemType Directory -Force | Out-Null
}
$logFile = Join-Path $logDir "cleanup.log"

function Log($msg) {
    $time = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$time - $msg" | Out-File $logFile -Append -Encoding utf8
}

Log "Registering RunOnce cleanup task..."
Log "Exe path: $exe"

if (Test-Path $exe) {
    reg add "HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce" `
        /v "TPLinkCleanup" `
        /t REG_SZ `
        /d "`"$exe`"" /f | Out-Null

    Log "RunOnce registered successfully"
} else {
    Log "ERROR: cleanup_http.exe not found!"
}
