@echo off
REM Medical Study App Launcher for Windows
REM This script starts both the backend server and Electron app

echo 🏥 Starting Medical Study App...
echo.

REM Check if virtual environment exists
if not exist "backend\venv" (
    echo ❌ Virtual environment not found!
    echo Please run setup first:
    echo   cd backend
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    exit /b 1
)

REM Check if node_modules exists
if not exist "frontend\node_modules" (
    echo ❌ Node modules not found!
    echo Please run: cd frontend ^&^& npm install
    exit /b 1
)

REM Check if .env exists
if not exist "backend\.env" (
    echo ⚠️  Warning: backend\.env not found!
    echo Please create it from backend\.env.example and add your ANTHROPIC_API_KEY
    exit /b 1
)

REM Start backend in background
echo 🚀 Starting backend server...
cd backend
start /B cmd /c "call venv\Scripts\activate && python main.py"
cd ..

REM Wait for backend to be ready
echo ⏳ Waiting for backend to start...
timeout /t 3 /nobreak > nul

REM Start Electron app
echo 🖥️  Launching desktop app...
cd frontend
call npm start

echo.
echo ✅ App closed
