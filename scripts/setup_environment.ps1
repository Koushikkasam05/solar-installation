# SolarFlow ERP - Environment Setup & Diagnostic Script
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "       SolarFlow ERP - Environment Diagnostic & Setup     " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Check Python
Write-Host "`n[1/5] Checking Python Installation..." -ForegroundColor White
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pyVer = python --version
    Write-Host "  -> Python is available: $pyVer" -ForegroundColor Green
} else {
    Write-Host "  -> [WARNING] Python is not found in PATH." -ForegroundColor Red
}

# 2. Check WSL2
Write-Host "`n[2/5] Checking WSL2 Status..." -ForegroundColor White
$wslStatus = wsl --status 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  -> WSL is installed and active." -ForegroundColor Green
} else {
    Write-Host "  -> [NOTICE] WSL is not installed. To install WSL2, run in Admin PowerShell:" -ForegroundColor Yellow
    Write-Host "     wsl --install" -ForegroundColor Cyan
}

# 3. Check Docker Desktop
Write-Host "`n[3/5] Checking Docker & Docker Compose..." -ForegroundColor White
if (Get-Command docker -ErrorAction SilentlyContinue) {
    $dockerVer = docker --version
    Write-Host "  -> Docker is installed: $dockerVer" -ForegroundColor Green
} else {
    Write-Host "  -> [ACTION REQUIRED] Docker Desktop is not detected in PATH." -ForegroundColor Yellow
    Write-Host "     Please download and install Docker Desktop for Windows from:" -ForegroundColor White
    Write-Host "     https://www.docker.com/products/docker-desktop" -ForegroundColor Cyan
}

# 4. Check Development Ports (8069, 5432, 8072)
Write-Host "`n[4/5] Checking Port Conflicts..." -ForegroundColor White
$ports = @(8069, 5432, 8072)
foreach ($p in $ports) {
    $conn = Get-NetTCPConnection -LocalPort $p -ErrorAction SilentlyContinue
    if ($conn) {
        Write-Host "  -> [WARNING] Port $p is already in use by PID $($conn.OwningProcess)!" -ForegroundColor Red
    } else {
        Write-Host "  -> Port $p is FREE and ready for SolarFlow." -ForegroundColor Green
    }
}

# 5. Environment File (.env)
Write-Host "`n[5/5] Checking .env configuration..." -ForegroundColor White
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "  -> Created .env from .env.example." -ForegroundColor Green
} else {
    Write-Host "  -> .env file is present." -ForegroundColor Green
}

Write-Host "`nDiagnostic check complete!" -ForegroundColor Cyan
