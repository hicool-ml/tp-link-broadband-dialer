# TP-Link路由器关机清理 - PowerShell包装脚本
# 支持区分关机和重启

param(
    [switch]$ShutdownOnly  # 只在关机时清除
)

$exe = "D:\13jiao\20260325\cleanup_http.exe"

# 检查是否是关机（不是重启）
function Test-IsShutdown {
    try {
        # 获取最近的关机事件
        $events = Get-WinEvent -FilterHashtable @{LogName='System'; ID=1074} -MaxEvents 5 -ErrorAction SilentlyContinue

        if ($events) {
            $lastEvent = $events[0]

            # 检查事件消息
            $message = $lastEvent.Message

            # 关机关键字
            if ($message -match "power off|shutdown|关机") {
                return $true
            }

            # 重启关键字
            if ($message -match "restart|reboot|重启") {
                return $false
            }

            # 检查进程名（shutdown.exe通常是关机）
            if ($message -match "process.*shutdown\.exe") {
                return $true
            }

            # 默认情况下，如果无法确定，执行清除（更安全）
            return $true
        }

        # 无法获取事件，默认执行清除
        return $true
    } catch {
        # 出错时默认执行清除
        return $true
    }
}

# 如果指定了 -ShutdownOnly 参数，检查是否是关机
if ($ShutdownOnly) {
    $isShutdown = Test-IsShutdown

    if (-not $isShutdown) {
        # 是重启，不执行清除
        $logDir = "C:\ProgramData\BroadbandDialer"
        if (-not (Test-Path $logDir)) {
            New-Item -Path $logDir -ItemType Directory -Force | Out-Null
        }
        $logFile = Join-Path $logDir "cleanup.log"
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        "$timestamp - INFO - 检测到重启，跳过账号清除" | Out-File -FilePath $logFile -Append -Encoding UTF8
        exit 0
    }
}

# 执行清除（关机或无法判断时）
if (Test-Path $exe) {
    Start-Process $exe -WindowStyle Hidden -Wait
} else {
    $logDir = "C:\ProgramData\BroadbandDialer"
    if (-not (Test-Path $logDir)) {
        New-Item -Path $logDir -ItemType Directory -Force | Out-Null
    }
    $logFile = Join-Path $logDir "cleanup.log"
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - ERROR - 找不到文件: $exe" | Out-File -FilePath $logFile -Append -Encoding UTF8
}
