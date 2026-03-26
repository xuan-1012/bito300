#!/bin/bash
# Setup script for AWS Model Risk Scoring development environment

echo "Setting up AWS Model Risk Scoring development environment..."

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install package in editable mode
echo "Installing package in editable mode..."
pip install -e .

echo "Setup complete! Activate the environment with: source venv/bin/activate"
