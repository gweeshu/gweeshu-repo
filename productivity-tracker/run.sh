#!/bin/bash
set -e

cd "$(dirname "$0")/backend"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate and install deps
source venv/bin/activate
pip install -q -r requirements.txt

# Copy .env.example if no .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "No .env file found. Creating from .env.example..."
    echo "Add your ANTHROPIC_API_KEY to backend/.env for AI insights."
    cp .env.example .env
fi

echo ""
echo "Starting Productivity Tracker on http://localhost:8000"
echo ""

python main.py
