# SolarFlow ERP - Container Startup Script
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "          Starting SolarFlow ERP Container Stack           " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Docker is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Please start Docker Desktop on your Windows machine." -ForegroundColor Yellow
    exit 1
}

Write-Host "[INFO] Starting PostgreSQL and Odoo services..." -ForegroundColor Cyan
docker-compose up -d

Write-Host "[INFO] Checking container status..." -ForegroundColor Cyan
docker-compose ps

Write-Host "`n[SUCCESS] Services launched!" -ForegroundColor Green
Write-Host "Access SolarFlow at: http://localhost:8069" -ForegroundColor Yellow
