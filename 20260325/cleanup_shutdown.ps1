# TP-Link路由器关机清理脚本
# 使用任务计划程序在关机时自动触发

param(
    [string]$ConfigPath = "$env:LOCALAPPDATA\Broadband_Dialer\config.json"
)

# 设置编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 日志函数
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $logDir = Join-Path $env:TEMP "tplink_cleanup"
    if (-not (Test-Path $logDir)) {
        New-Item -Path $logDir -ItemType Directory -Force | Out-Null
    }
    $logFile = Join-Path $logDir "cleanup.log"
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $Level - $Message" | Out-File -FilePath $logFile -Append -Encoding UTF8
}

Write-Log "=== 关机清理脚本启动 ==="

try {
    # 读取配置
    if (-not (Test-Path $ConfigPath)) {
        Write-Log "配置文件不存在: $ConfigPath" "ERROR"
        exit 1
    }

    $configJson = Get-Content $ConfigPath -Raw -Encoding UTF8
    $config = $configJson | ConvertFrom-Json

    $routerIp = $config.router_ip
    $encryptedPassword = $config.router_password

    if (-not $routerIp -or -not $encryptedPassword) {
        Write-Log "配置不完整，跳过清理" "WARN"
        exit 0
    }

    Write-Log "路由器IP: $routerIp"

    # 解密密码
    try {
        # 使用Python解密（因为加密是用Python做的）
        $decryptScript = @"
import sys
import base64
from pathlib import Path

key = b'TPLinkRouterCleanup2025'

def decrypt_password(encrypted):
    try:
        decoded = base64.b64decode(encrypted)
        iv = decoded[:16]
        ciphertext = decoded[16:]
        from Crypto.Cipher import AES
        from Crypto.Util.Padding import unpad
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(ciphertext), 16).decode('utf-8')
    except:
        return encrypted

if __name__ == '__main__':
    encrypted = sys.argv[1] if len(sys.argv) > 1 else ''
    print(decrypt_password(encrypted))
"@

        $tempScript = Join-Path $env:TEMP "decrypt_pwd.py"
        $decryptScript | Out-File -FilePath $tempScript -Encoding UTF8

        $password = python $tempScript $encryptedPassword 2>&1
        Remove-Item $tempScript -Force -ErrorAction SilentlyContinue

        if ($LASTEXITCODE -ne 0) {
            Write-Log "密码解密失败，使用原文" "WARN"
            $password = $encryptedPassword
        }
    } catch {
        Write-Log "密码解密异常: $_" "WARN"
        $password = $encryptedPassword
    }

    # 执行清理（直接调用HTTP API）
    Write-Log "开始清理路由器账号..."

    $loginUrl = "http://${routerIp}/"
    $logoutUrl = "http://${routerIp}/logout"

    # 使用requests库（通过Python）
    $cleanupScript = @"
import sys
import requests

router_ip = "$routerIp"
password = "$password"

try:
    session = requests.Session()
    session.verify = False
    session.headers.update({'User-Agent': 'Mozilla/5.0'})

    # 登录
    login_data = {'password': password}
    resp = session.post(f'http://{router_ip}/', data=login_data, timeout=5)
    print(f'Login: {resp.status_code}')

    # 退出登录（清除账号）
    resp = session.get(f'http://{router_ip}/logout', timeout=5)
    print(f'Logout: {resp.status_code}')

    print('SUCCESS')
except Exception as e:
    print(f'ERROR: {e}')
"@

    $tempCleanup = Join-Path $env:TEMP "cleanup_http.py"
    $cleanupScript | Out-File -FilePath $tempCleanup -Encoding UTF8

    $result = python $tempCleanup 2>&1
    Remove-Item $tempCleanup -Force -ErrorAction SilentlyContinue

    if ($result -match "SUCCESS") {
        Write-Log "清理成功"
    } else {
        Write-Log "清理失败: $result" "ERROR"
    }

} catch {
    Write-Log "脚本异常: $_" "ERROR"
}

Write-Log "=== 关机清理脚本结束 ==="
