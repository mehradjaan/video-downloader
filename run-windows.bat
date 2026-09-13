@echo off
chcp 65001 >nul
title Video Downloader
echo ============================================
echo   Video Downloader - Windows Launcher
echo ============================================
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Install it from https://www.python.org/downloads/
    echo Tick "Add python.exe to PATH" during install.
    pause
    exit /b
)
echo Installing requirements...
pip install -r requirements.txt
echo.
echo Starting app... open http://localhost:5000 in your browser
echo.
python app.py
pause
