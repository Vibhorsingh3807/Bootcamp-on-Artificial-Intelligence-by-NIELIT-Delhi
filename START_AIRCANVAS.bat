@echo off
title AirCanvas AI Launcher
color 0B
cd /d "%~dp0"

echo ====================================================================
echo      🎨 AIRCANVAS AI — TOUCHLESS GESTURE WHITEBOARD & SMART CANVAS
echo ====================================================================
echo.
echo  [*] Launching AirCanvas from root directory...
cd AirCanvas
python run.py

if errorlevel 1 (
    echo.
    echo [NOTICE] If port was busy or an issue occurred, please retry.
    pause
)
