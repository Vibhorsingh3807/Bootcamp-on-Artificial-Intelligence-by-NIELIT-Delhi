@echo off
title EchoSign AI - Assistive Communication Bridge
cls

echo ====================================================================
echo   EchoSign AI 2.0 -- Assistive Communication Bridge
echo ====================================================================

cd /d "%~dp0"

if exist "EchoSign\run.py" (
    set SCRIPT_PATH=EchoSign\run.py
) else if exist "run.py" (
    set SCRIPT_PATH=run.py
) else (
    echo [ERROR] Could not find run.py! Make sure you run this from the project folder.
    pause
    exit /b 1
)

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python was not found in your system PATH!
    pause
    exit /b 1
)

echo   [1/2] Checking GPU RTX 4060 and PyTorch CUDA status...
python -c "import torch; print('         Hardware Status:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU mode')"

echo   [2/2] Starting EchoSign server and opening your web browser...
echo ====================================================================
echo.

python "%SCRIPT_PATH%"

if %errorlevel% neq 0 (
    echo.
    echo Server stopped or encountered an error.
    pause
)
