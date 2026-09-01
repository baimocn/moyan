# Moyan - reset local PostgreSQL password & create moyan user/db (ASCII only)
# Run as Administrator:
#   powershell -ExecutionPolicy Bypass -File "D:\Desktop\墨衍-项目\tools\reset_pg_local.ps1"
$ErrorActionPreference = "Stop"
$pg = "C:\Program Files\PostgreSQL\18"
$hba = "$pg\data\pg_hba.conf"
$bin = "$pg\bin"
$pw = "moyan_dev_2026"
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)

if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole("Administrators")) {
    Write-Host "NOT ADMIN - please run elevated."
    exit 1
}
if (-not (Test-Path $hba)) { Write-Host "hba not found: $hba"; exit 1 }

# 1) backup + switch localhost to trust
Copy-Item $hba "$hba.bak" -Force
$lines = @(Get-Content $hba)
$out = @()
foreach ($ln in $lines) {
    $t = $ln -replace '^host\s+all\s+all\s+127\.0\.0\.1/32\s+.*$', 'host    all    all    127.0.0.1/32    trust'
    $t = $t -replace '^host\s+all\s+all\s+::1/128\s+.*$', 'host    all    all    ::1/128    trust'
    $out += $t
}
[System.IO.File]::WriteAllLines($hba, $out, $utf8NoBom)
Write-Host "[1] hba -> trust"

# 2) restart service
Write-Host "[2] restart service..."
Restart-Service -Name "postgresql-x64-18" -Force
Start-Sleep -Seconds 3

# 3) trust ops (separate psql calls, tolerate already-exists errors)
Write-Host "[3] reset passwords, create moyan user/db..."
& "$bin\psql.exe" -U postgres -h localhost -c "ALTER USER postgres WITH PASSWORD '$pw';"
& "$bin\psql.exe" -U postgres -h localhost -c "CREATE USER moyan WITH PASSWORD '$pw';"
& "$bin\psql.exe" -U postgres -h localhost -c "CREATE DATABASE moyan OWNER moyan;"

# 4) restore scram
$lines = @(Get-Content $hba)
$out = @()
foreach ($ln in $lines) {
    $t = $ln -replace '^host\s+all\s+all\s+127\.0\.0\.1/32\s+trust\s*$', 'host    all    all    127.0.0.1/32    scram-sha-256'
    $t = $t -replace '^host\s+all\s+all\s+::1/128\s+trust\s*$', 'host    all    all    ::1/128    scram-sha-256'
    $out += $t
}
[System.IO.File]::WriteAllLines($hba, $out, $utf8NoBom)
& "$bin\psql.exe" -U postgres -h localhost -c "SELECT pg_reload_conf();" | Out-Null
Write-Host "[4] hba -> scram restored"

# 5) verify moyan
$env:PGPASSWORD = $pw
$test = & "$bin\psql.exe" -U moyan -h localhost -d moyan -c "SELECT 1 AS ok;" 2>&1
$env:PGPASSWORD = ""
if ($LASTEXITCODE -eq 0) {
    Write-Host "[5] VERIFY OK: moyan / $pw @ 127.0.0.1:5432/moyan"
    Write-Host "DONE"
} else {
    Write-Host "[5] VERIFY FAIL: $test"
    exit 1
}