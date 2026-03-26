#!/bin/bash

echo "========================================"
echo "BitoGuard Live Demo Launcher"
echo "========================================"
echo ""

echo "Checking Python installation..."
python3 --version
if [ $? -ne 0 ]; then
    echo "ERROR: Python is not installed or not in PATH"
    exit 1
fi

echo ""
echo "Installing dependencies..."
pip3 install -r requirements.txt

echo ""
echo "Starting BitoGuard Demo..."
echo ""
echo "Demo will open in your browser at http://localhost:8501"
echo "Press Ctrl+C to stop the demo"
echo ""

streamlit run app.py
