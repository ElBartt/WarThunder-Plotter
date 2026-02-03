@echo off
title WarThunder Plotter - Watch Mode
color 0A
echo ======================================
echo   WarThunder Plotter - Watch Mode
echo ======================================
echo.
echo Activating virtual environment...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Error: Failed to activate virtual environment
    echo Please check if .venv exists and is properly set up
    pause
    exit /b 1
)
echo Virtual environment activated successfully.
echo.
echo Starting plotter in watch mode...
echo Press Ctrl+C to stop the server
echo.
python app.py watch
pause