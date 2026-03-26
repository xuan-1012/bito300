@echo off
echo ========================================
echo BitoGuard Demo - XGBoost Predictions
echo ========================================
echo.
echo Starting demo...
echo Demo will open at: http://localhost:8503
echo.
echo Press Ctrl+C to stop
echo ========================================
echo.

streamlit run app_demo.py --server.port 8503
