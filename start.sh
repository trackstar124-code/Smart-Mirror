#!/bin/bash

# Define paths
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SMART_MIRROR_DIR="$PROJECT_ROOT/smart-mirror"
VENV_DIR="$PROJECT_ROOT/.venv"

# Use Python 3.11
PYTHON=python3.11

# Check that Python 3.11 is installed
if ! command -v "$PYTHON" &> /dev/null; then
    echo "Error: Python 3.11 is not installed."
    echo "Install it with:"
    echo "sudo apt install python3.11 python3.11-venv"
    read -p "Press Enter to exit..."
    exit 1
fi

# Recreate the virtual environment if it was built with another Python version
if [ -d "$VENV_DIR" ]; then
    VENV_PY="$VENV_DIR/bin/python"
    if [ -x "$VENV_PY" ]; then
        VERSION=$("$VENV_PY" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        if [ "$VERSION" != "3.11" ]; then
            echo "Existing virtual environment uses Python $VERSION."
            echo "Recreating it with Python 3.11..."
            rm -rf "$VENV_DIR"
        fi
    fi
fi

# Create virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment with Python 3.11..."
    "$PYTHON" -m venv "$VENV_DIR"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Use the venv's Python from this point on
PYTHON="$VENV_DIR/bin/python"
PIP="$VENV_DIR/bin/pip"

# Upgrade pip
echo "Upgrading pip..."
"$PIP" install --upgrade pip

# Install requirements
echo "Installing requirements..."

if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
    "$PIP" install -r "$PROJECT_ROOT/requirements.txt"
fi

if [ -f "$SMART_MIRROR_DIR/requirements.txt" ]; then
    "$PIP" install -r "$SMART_MIRROR_DIR/requirements.txt"
fi

# Start main.py only
echo "Starting main.py..."
"$PYTHON" -u "$SMART_MIRROR_DIR/app/main.py" &
MAIN_PID=$!

echo "=========================================================="
echo "Smart Mirror is running!"
echo "Using: $("$PYTHON" --version)"
echo "Dashboard available at: http://localhost:8000"
echo "Press Ctrl+C to stop."
echo "=========================================================="

cleanup() {
    echo
    echo "Stopping Smart Mirror..."
    kill "$MAIN_PID" 2>/dev/null
}

trap "cleanup; exit" INT TERM

# Wait for main.py to exit
wait "$MAIN_PID"
EXIT_CODE=$?

echo
echo "=========================================================="
echo "main.py has exited."
echo "Exit code: $EXIT_CODE"
echo "=========================================================="

cleanup

echo
echo "The program has paused so you can read any Python errors above."
read -p "Press Enter to close..."