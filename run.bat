@echo off
echo ========================================
echo   CodeMaster AI - Learning Assistant
echo ========================================
echo.

:: Check if Python virtual environment exists
if not exist ".venv" (
    echo Creating Python virtual environment...
    python -m venv .venv
)

:: Activate virtual environment and install backend dependencies
echo Installing backend dependencies...
call .venv\Scripts\activate
cd backend
pip install -r requirements.txt
cd ..

:: Install frontend dependencies if node_modules doesn't exist
if not exist "frontend\node_modules" (
    echo Installing frontend dependencies...
    cd frontend
    npm install
    cd ..
)

echo.
echo ========================================
echo   Starting Application...
echo ========================================
echo.

:: Start backend in a new window
echo Starting Backend Server on http://localhost:5000
start "Backend Server" cmd /k "cd /d %~dp0backend && ..\\.venv\Scripts\python.exe -m app.main"

:: Wait for backend to start
timeout /t 3 /nobreak >nul

:: Start frontend in a new window
echo Starting Frontend on http://localhost:3000
start "Frontend Server" cmd /k "cd /d %~dp0frontend && npm start"

echo.
echo ========================================
echo   Application Started!
echo ========================================
echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Close the terminal windows to stop the servers.
echo.
pause
