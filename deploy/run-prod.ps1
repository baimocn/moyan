# 墨衍 · 生产启动脚本（Windows / PowerShell）
#
# 顺序：
#   1) 加载 .env  2) 启动后端（无 reload） 3) 启 Caddy 反代
#
# 用法：
#   powershell -ExecutionPolicy Bypass -File deploy/run-prod.ps1

$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

if (-not (Test-Path .env)) {
    Write-Host "❌ .env 不存在。先 Copy-Item .env.production.example .env" -ForegroundColor Red
    exit 1
}

# 1) 加载 .env 到当前 session
Get-Content .env | ForEach-Object {
    if ($_ -match '^\s*#' -or $_ -match '^\s*$') { return }
    $name, $value = $_ -split '=', 2
    Set-Item -Path "Env:$name" -Value $value
}

# 2) 检查关键配置
if (-not $env:MOYAN_JWT_SECRET) { throw "MOYAN_JWT_SECRET 未配置（生产必填）" }
if (-not $env:MOYAN_WX_APPID)   { throw "MOYAN_WX_APPID 未配置" }
if (-not $env:MOYAN_WX_APPSECRET) { throw "MOYAN_WX_APPSECRET 未配置" }

# 3) 启 FastAPI
Write-Host "→ 启动墨衍后端（uvicorn）" -ForegroundColor Green
& uvicorn backend.main:app `
    --host ($env:MOYAN_HOST ?? "127.0.0.1") `
    --port ($env:MOYAN_PORT ?? "5001") `
    --workers ($env:MOYAN_WORKERS ?? "2") `
    --proxy-headers `
    --forwarded-allow-ips="*" `
    --log-level info
