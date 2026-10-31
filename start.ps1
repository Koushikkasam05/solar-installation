Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Starting Solar Installation ERP (Odoo 17) Stack " -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Cyan

# Check if Docker is installed
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Docker is not found in your PATH." -ForegroundColor Red
    Write-Host "Please install Docker Desktop for Windows from: https://www.docker.com/products/docker-desktop" -ForegroundColor White
    Write-Host "Alternatively, you can test all calculations and models using the Standalone Simulator:" -ForegroundColor Green
    Write-Host "  python test_solar_suite.py" -ForegroundColor Green
    exit 1
}

Write-Host "[INFO] Starting PostgreSQL and Odoo services..." -ForegroundColor Cyan
docker-compose up -d

Write-Host "[SUCCESS] Services launched!" -ForegroundColor Green
Write-Host "Access Odoo Web Interface at: http://localhost:8069" -ForegroundColor Yellow
Write-Host "Master Password: solar_admin_master_2026" -ForegroundColor White
Write-Host "Database User: odoo | Pass: odoo_secure_pass_2026" -ForegroundColor White
