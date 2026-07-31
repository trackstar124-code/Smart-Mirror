#!/bin/bash

# Define paths
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SMART_MIRROR_DIR="$PROJECT_ROOT/smart-mirror"
VENV_DIR="$PROJECT_ROOT/.venv"

# ── Python version detection ───────────────────────────────────────────────────
# Prefer the highest available Python (3.14 → 3.13 → 3.12 → 3.11).
# Adjust the list below if you need a specific version.
PYTHON=""
for candidate in python3.14 python3.13 python3.12 python3.11 python3; do
    if command -v "$candidate" &> /dev/null; then
        PYTHON="$candidate"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "Error: No compatible Python 3 installation found."
    echo "Install Python 3.11 or later and try again."
    read -p "Press Enter to exit..."
    exit 1
fi

echo "Using Python: $("$PYTHON" --version)"

# Recreate the virtual environment if it was built with a different Python version
if [ -d "$VENV_DIR" ]; then
    VENV_PY="$VENV_DIR/bin/python"
    if [ -x "$VENV_PY" ]; then
        VENV_VER=$("$VENV_PY" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        SYS_VER=$("$PYTHON" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        if [ "$VENV_VER" != "$SYS_VER" ]; then
            echo "Existing venv uses Python $VENV_VER, but system Python is $SYS_VER."
            echo "Recreating virtual environment..."
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

# Pre-download ONNX hand-tracking models (skipped if already cached)
echo "Checking ONNX gesture models..."
"$PYTHON" "$SMART_MIRROR_DIR/app/modules/download_models.py"

# Start main.py (gesture loop runs as a daemon thread inside it)
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