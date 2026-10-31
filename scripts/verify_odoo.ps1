# SolarFlow ERP - Odoo Health & Connectivity Verification
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "            Verifying SolarFlow Odoo Connectivity          " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

$url = "http://localhost:8069/web/login"
Write-Host "[INFO] Testing HTTP connectivity to $url..." -ForegroundColor Cyan

try {
    $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "[SUCCESS] Odoo Web Interface is responding (HTTP 200 OK)!" -ForegroundColor Green
        Write-Host "You can now log in or create your database at http://localhost:8069" -ForegroundColor Yellow
    } else {
        Write-Host "[WARNING] Received HTTP status code: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[NOTICE] Odoo web interface is not responding yet on port 8069." -ForegroundColor Yellow
    Write-Host "If Docker Desktop is running, check container logs with: docker-compose logs web" -ForegroundColor White
}
