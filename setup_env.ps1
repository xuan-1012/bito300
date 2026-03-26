# PowerShell setup script for AWS Model Risk Scoring development environment

Write-Host "Setting up AWS Model Risk Scoring development environment..." -ForegroundColor Green

# Create virtual environment
Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Install package in editable mode
Write-Host "Installing package in editable mode..." -ForegroundColor Yellow
pip install -e .

Write-Host "Setup complete! Activate the environment with: .\venv\Scripts\Activate.ps1" -ForegroundColor Green
