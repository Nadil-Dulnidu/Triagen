# ==============================================================================
# PullSense — 1-Click Local Development Setup Script (Windows PowerShell)
# ==============================================================================

Write-Host "🚀 Starting PullSense local development setup..." -ForegroundColor Cyan

# 1. Check prerequisites
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "❌ 'uv' is required. Install via: winget install astral-sh.uv or irm https://astral.sh/uv/install.ps1 | iex" -ForegroundColor Red
    exit 1
}

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Node.js is required. Please install Node.js >= 18" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Prerequisites verified: uv, node, npm." -ForegroundColor Green

# 2. Server setup
if (-not (Test-Path "server/.env")) {
    Write-Host "📋 Copying server/.env.example -> server/.env" -ForegroundColor Yellow
    Copy-Item "server/.env.example" "server/.env"
}

Write-Host "📦 Installing backend dependencies with uv..." -ForegroundColor Cyan
Set-Location server
uv sync
Write-Host "✅ Backend dependencies installed." -ForegroundColor Green

# 3. Client setup
Set-Location ../client
if (-not (Test-Path ".env")) {
    Write-Host "📋 Copying client/.env.example -> client/.env" -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
}

Write-Host "📦 Installing frontend dependencies with npm..." -ForegroundColor Cyan
npm install
Write-Host "✅ Frontend dependencies installed." -ForegroundColor Green

Set-Location ..
Write-Host "🎉 PullSense setup complete! Run 'make dev' to start all services." -ForegroundColor Magenta
