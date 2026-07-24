#!/bin/bash

# Define paths
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SMART_MIRROR_DIR="$PROJECT_ROOT/smart-mirror"
VENV_DIR="$PROJECT_ROOT/.venv"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip just in case
pip install --upgrade pip

# Install requirements
echo "Checking and installing requirements..."
if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
    pip install -r "$PROJECT_ROOT/requirements.txt"
fi

if [ -f "$SMART_MIRROR_DIR/requirements.txt" ]; then
    pip install -r "$SMART_MIRROR_DIR/requirements.txt"
fi

# Start gestures.py in the background
echo "Starting gestures.py..."
python "$SMART_MIRROR_DIR/app/modules/gestures.py" &
GESTURES_PID=$!

# Start main.py in the background
echo "Starting main.py..."
python "$SMART_MIRROR_DIR/app/main.py" &
MAIN_PID=$!

echo "=========================================================="
echo "Smart Mirror is running!"
echo "Dashboard available at: http://localhost:8000"
echo "Press Ctrl+C to stop both the web server and gesture recognition."
echo "=========================================================="

# Trap SIGINT (Ctrl+C) and kill both background processes
trap "echo -e '\nStopping Smart Mirror...'; kill $GESTURES_PID $MAIN_PID 2>/dev/null; exit" INT TERM

# Wait for processes so the script doesn't exit immediately
wait $MAIN_PID
wait $GESTURES_PID
