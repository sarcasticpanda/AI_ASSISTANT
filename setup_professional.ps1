# Quick Setup Script for Jarvis Voice Assistant
# Run this in PowerShell with venv activated

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  JARVIS SETUP - Professional Version" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if venv is activated
if ($env:VIRTUAL_ENV) {
    Write-Host "✅ Virtual environment activated: $env:VIRTUAL_ENV" -ForegroundColor Green
} else {
    Write-Host "⚠️  Virtual environment NOT activated!" -ForegroundColor Yellow
    Write-Host "   Please run: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press ENTER to exit"
    exit
}

Write-Host ""
Write-Host "Installing professional audio libraries..." -ForegroundColor Cyan

# Install WebRTC VAD
Write-Host "  📦 Installing webrtcvad (Voice Activity Detection)..." -ForegroundColor White
pip install webrtcvad --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "     ✅ webrtcvad installed" -ForegroundColor Green
} else {
    Write-Host "     ❌ webrtcvad failed - you might need Visual C++ Build Tools" -ForegroundColor Red
}

# Install noisereduce
Write-Host "  📦 Installing noisereduce (Noise Suppression)..." -ForegroundColor White
pip install noisereduce --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "     ✅ noisereduce installed" -ForegroundColor Green
} else {
    Write-Host "     ❌ noisereduce failed" -ForegroundColor Red
}

# Install pydub
Write-Host "  📦 Installing pydub (Audio Normalization)..." -ForegroundColor White
pip install pydub --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "     ✅ pydub installed" -ForegroundColor Green
} else {
    Write-Host "     ❌ pydub failed" -ForegroundColor Red
}

# Install numpy
Write-Host "  📦 Installing numpy (Array Processing)..." -ForegroundColor White
pip install numpy --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "     ✅ numpy installed" -ForegroundColor Green
} else {
    Write-Host "     ❌ numpy failed" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VERIFICATION" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Verify installations
Write-Host ""
Write-Host "Testing imports..." -ForegroundColor White

$testScript = @"
import webrtcvad
import noisereduce
import pydub
import numpy
print('✅ All professional audio libraries installed successfully!')
"@

python -c $testScript

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ✅ SETUP COMPLETE!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now run:" -ForegroundColor White
    Write-Host "  python tests\phase1_professional.py" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  ❌ SETUP INCOMPLETE" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Some packages failed to install." -ForegroundColor Yellow
    Write-Host "Please check the errors above." -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Package List:" -ForegroundColor White
pip list | Select-String -Pattern "webrtcvad|noisereduce|pydub|numpy|pyaudio"

Write-Host ""
Read-Host "Press ENTER to exit"
