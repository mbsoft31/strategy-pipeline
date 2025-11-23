@echo off
REM Strategy Pipeline - Frontend Startup Script
REM Starts the React development server

echo.
echo ============================================================
echo Strategy Pipeline - Starting Frontend Server
echo ============================================================
echo.

cd /d "%~dp0\frontend\strategy-pipeline-ui"

REM Check if node_modules exists
if not exist "node_modules\" (
    echo Installing dependencies...
    call npm install
)

REM Start the development server
echo.
echo Starting React dev server...
echo Frontend will be available at: http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.

call npm run dev

pause

