@echo off
REM Strategy Pipeline - Backend Startup Script
REM Starts the Flask backend server with JSON API

echo.
echo ============================================================
echo Strategy Pipeline - Starting Backend Server
echo ============================================================
echo.

cd /d "%~dp0"

REM Check if virtual environment exists
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo Warning: No virtual environment found at .venv
    echo Using global Python installation
)

REM Check if flask-cors is installed
python -c "import flask_cors" 2>nul
if errorlevel 1 (
    echo.
    echo Installing flask-cors...
    pip install flask-cors==4.0.0
)

REM Start the server
echo.
echo Starting Flask backend...
echo Server will be available at: http://localhost:5000
echo API endpoints at: http://localhost:5000/api/*
echo.
echo Press Ctrl+C to stop the server
echo.

python interfaces/web_app.py

pause

