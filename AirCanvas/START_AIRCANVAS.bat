@echo off
title AirCanvas AI — Touchless Gesture Whiteboard
color 0B
cd /d "%~dp0"

echo ====================================================================
echo      🎨 AIRCANVAS AI — TOUCHLESS GESTURE WHITEBOARD & SMART CANVAS
echo ====================================================================
echo.
echo  [*] Checking Python Environment...

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    pause
    exit /b 1
)

echo  [*] Initializing AirCanvas AI Engine...
echo  [*] Starting FastAPI Server on Localhost...
echo  [*] Browser will open automatically at http://127.0.0.1:8050
echo.
python run.py

if errorlevel 1 (
    echo.
    echo [NOTICE] If port was busy or an issue occurred, please retry.
    pause
)
