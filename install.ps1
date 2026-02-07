# E1 Assistant - Windows PowerShell Installer
# One-liner: irm https://raw.githubusercontent.com/m3tokenized-hue/m3trad/main/install.ps1 | iex

$ErrorActionPreference = "Stop"
$repoUrl = "https://github.com/m3tokenized-hue/m3trad.git"

Write-Host ""
Write-Host "  ========================================" -ForegroundColor Cyan
Write-Host "   E1 Assistant - Local Installation" -ForegroundColor Cyan
Write-Host "  ========================================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "[CHECK] Verifying prerequisites..." -ForegroundColor Yellow

try { python --version | Out-Null } catch {
    Write-Host "[ERROR] Python not found. Install from https://python.org" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Python found" -ForegroundColor Green

try { node --version | Out-Null } catch {
    Write-Host "[ERROR] Node.js not found. Install from https://nodejs.org" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Node.js found" -ForegroundColor Green

try { git --version | Out-Null } catch {
    Write-Host "[ERROR] Git not found. Install from https://git-scm.com" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Git found" -ForegroundColor Green

Write-Host ""

# Installation directory
$installDir = "$env:USERPROFILE\e1-assistant"

if (Test-Path $installDir) {
    Write-Host "[INFO] Updating existing installation..." -ForegroundColor Yellow
    Set-Location $installDir
    git pull
} else {
    Write-Host "[INFO] Installing E1 Assistant to $installDir" -ForegroundColor Yellow
    git clone $repoUrl $installDir
    Set-Location $installDir
}

Write-Host ""
Write-Host "[INFO] Installing backend dependencies..." -ForegroundColor Yellow
Set-Location backend
pip install -r requirements.txt -q
Set-Location ..

Write-Host "[INFO] Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location frontend
npm install --silent 2>$null
Set-Location ..

# Setup environment
Write-Host ""
Write-Host "[SETUP] Configuration" -ForegroundColor Cyan

$backendEnv = "backend\.env"
if (-not (Test-Path $backendEnv)) {
    $mongoUrl = Read-Host "MongoDB URL (Enter for local mongodb://localhost:27017)"
    if ([string]::IsNullOrWhiteSpace($mongoUrl)) { $mongoUrl = "mongodb://localhost:27017" }
    
    $emergentKey = Read-Host "Emergent LLM Key (get from Emergent Profile -> Universal Key)"
    
    @"
MONGO_URL="$mongoUrl"
DB_NAME="e1_assistant"
CORS_ORIGINS="*"
EMERGENT_LLM_KEY=$emergentKey
"@ | Out-File -FilePath $backendEnv -Encoding UTF8
    
    Write-Host "[OK] Backend .env created" -ForegroundColor Green
}

$frontendEnv = "frontend\.env"
if (-not (Test-Path $frontendEnv)) {
    "REACT_APP_BACKEND_URL=http://localhost:8001" | Out-File -FilePath $frontendEnv -Encoding UTF8
    Write-Host "[OK] Frontend .env created" -ForegroundColor Green
}

Write-Host ""
Write-Host "  ========================================" -ForegroundColor Green
Write-Host "   Installation Complete!" -ForegroundColor Green
Write-Host "  ========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  To start E1 Assistant:" -ForegroundColor White
Write-Host "    cd $installDir" -ForegroundColor Yellow
Write-Host "    .\start.bat" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Or run manually:" -ForegroundColor White
Write-Host "    Terminal 1: cd backend; python -m uvicorn server:app --reload --port 8001" -ForegroundColor Gray
Write-Host "    Terminal 2: cd frontend; npm start" -ForegroundColor Gray
Write-Host ""
Write-Host "  Then open: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""

# Ask to start now
$startNow = Read-Host "Start E1 Assistant now? (Y/n)"
if ($startNow -ne "n" -and $startNow -ne "N") {
    & ".\start.bat"
}
