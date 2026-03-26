@echo off
echo ========================================
echo BitoGuard Demo - Fixed Version
echo ========================================
echo.
echo Starting Streamlit server...
echo Demo will open at: http://localhost:8502
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

streamlit run app.py --server.port 8502
