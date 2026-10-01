@echo off
cd /d "%~dp0"
title Gemini Flash TTS
cls
echo ======================================================
echo    Gemini Flash TTS Web App
echo ======================================================
echo.
echo [INFO] Starting web server...
echo [INFO] Please open http://localhost:8501 in your browser.
echo [INFO] Press Ctrl+C or close this window to exit.
echo.

.\.venv\Scripts\streamlit.exe run app.py
pause
