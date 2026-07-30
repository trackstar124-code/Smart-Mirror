#!/bin/bash

# Define paths
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SMART_MIRROR_DIR="$PROJECT_ROOT/smart-mirror"
VENV_DIR="$PROJECT_ROOT/.venv"

# Force Python 3.12
PYTHON=python3.12

# Check that Python 3.12 is installed
if ! command -v $PYTHON &> /dev/null; then
    echo "Error: Python 3.12 is not installed."
    echo "Please install Python 3.12 before running this script."
    read -p "Press Enter to exit..."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment with Python 3.12..."
    $PYTHON -m venv "$VENV_DIR"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Use the venv's Python from this point on
PYTHON="$VENV_DIR/bin/python"
PIP="$VENV_DIR/bin/pip"

# Upgrade pip
echo "Upgrading pip..."
$PIP install --upgrade pip

# Install requirements
echo "Checking and installing requirements..."

if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
    $PIP install -r "$PROJECT_ROOT/requirements.txt"
fi

if [ -f "$SMART_MIRROR_DIR/requirements.txt" ]; then
    $PIP install -r "$SMART_MIRROR_DIR/requirements.txt"
fi

# Start gestures.py in the background
echo "Starting gestures.py..."
$PYTHON -u "$SMART_MIRROR_DIR/app/modules/gestures.py" &
GESTURES_PID=$!

# Start main.py in the background
echo "Starting main.py..."
$PYTHON -u "$SMART_MIRROR_DIR/app/main.py" &
MAIN_PID=$!

echo "=========================================================="
echo "Smart Mirror is running!"
echo "Using: $($PYTHON --version)"
echo "Dashboard available at: http://localhost:8000"
echo "Press Ctrl+C to stop both the web server and gesture recognition."
echo "=========================================================="

cleanup() {
    echo
    echo "Stopping Smart Mirror..."
    kill $GESTURES_PID $MAIN_PID 2>/dev/null
}

trap "cleanup; exit" INT TERM

# Wait until one process exits
wait -n
EXIT_CODE=$?

echo
echo "=========================================================="
echo "A process has exited!"
echo "Exit code: $EXIT_CODE"
echo "=========================================================="

# Check which process exited
if ! kill -0 $GESTURES_PID 2>/dev/null; then
    echo "gestures.py has stopped or crashed."
fi

if ! kill -0 $MAIN_PID 2>/dev/null; then
    echo "main.py has stopped or crashed."
fi

cleanup

echo
echo "The program has paused so you can read any Python errors above."
read -p "Press Enter to close..."