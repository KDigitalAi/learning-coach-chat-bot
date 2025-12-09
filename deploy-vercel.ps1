# Vercel Deployment Script for Windows PowerShell
# This script helps deploy to Vercel with different configurations

Write-Host "🚀 Vercel Deployment Helper" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan
Write-Host ""

# Check if Vercel CLI is installed
try {
    $vercelVersion = vercel --version 2>&1
    Write-Host "✅ Vercel CLI found: $vercelVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Vercel CLI not found. Installing..." -ForegroundColor Red
    npm install -g vercel
}

Write-Host ""

# Check current configuration
Write-Host "📋 Current Configuration:" -ForegroundColor Yellow
if (Test-Path "vercel.json") {
    Write-Host "  - vercel.json: ✅" -ForegroundColor Green
} else {
    Write-Host "  - vercel.json: ❌" -ForegroundColor Red
}

if (Test-Path "api/index.py") {
    Write-Host "  - api/index.py: ✅" -ForegroundColor Green
} else {
    Write-Host "  - api/index.py: ❌" -ForegroundColor Red
}

if (Test-Path "api/requirements.txt") {
    Write-Host "  - api/requirements.txt: ✅" -ForegroundColor Green
} else {
    Write-Host "  - api/requirements.txt: ❌" -ForegroundColor Red
}

Write-Host ""

# Ask which configuration to use
Write-Host "Select deployment method:"
Write-Host "1) Current vercel.json (functions format)"
Write-Host "2) Alternative 1 (builds + routes)"
Write-Host "3) Alternative 2 (minimal)"
Write-Host "4) Test locally first (vercel dev)"
Write-Host "5) Deploy to production"
$choice = Read-Host "Enter choice [1-5]"

switch ($choice) {
    "1" {
        Write-Host "Using current vercel.json..." -ForegroundColor Yellow
    }
    "2" {
        Write-Host "Switching to builds + routes format..." -ForegroundColor Yellow
        Copy-Item "vercel-alternative-1.json" "vercel.json" -Force
    }
    "3" {
        Write-Host "Switching to minimal configuration..." -ForegroundColor Yellow
        Copy-Item "vercel-alternative-2.json" "vercel.json" -Force
    }
    "4" {
        Write-Host "Starting local development server..." -ForegroundColor Yellow
        vercel dev
        exit
    }
    "5" {
        Write-Host "Deploying to production..." -ForegroundColor Yellow
        vercel --prod
        exit
    }
    default {
        Write-Host "Invalid choice" -ForegroundColor Red
        exit 1
    }
}

# Deploy
Write-Host ""
Write-Host "🚀 Deploying..." -ForegroundColor Cyan
vercel

Write-Host ""
Write-Host "✅ Deployment initiated!" -ForegroundColor Green
Write-Host "Check Vercel dashboard for status." -ForegroundColor Yellow

