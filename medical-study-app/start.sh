#!/bin/bash

# Medical Study App Launcher
# This script starts both the backend server and Electron app

echo "🏥 Starting Medical Study App..."
echo ""

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run setup first:"
    echo "  cd backend"
    echo "  python -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Check if node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "❌ Node modules not found!"
    echo "Please run: cd frontend && npm install"
    exit 1
fi

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  Warning: backend/.env not found!"
    echo "Please create it from backend/.env.example and add your ANTHROPIC_API_KEY"
    exit 1
fi

# Start backend in background
echo "🚀 Starting backend server..."
cd backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to be ready
echo "⏳ Waiting for backend to start..."
sleep 3

# Start Electron app
echo "🖥️  Launching desktop app..."
cd frontend
npm start

# Cleanup: kill backend when Electron exits
echo ""
echo "🛑 Shutting down backend server..."
kill $BACKEND_PID
echo "✅ App closed"
