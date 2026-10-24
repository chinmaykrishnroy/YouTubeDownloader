#!/usr/bin/env bash
set -e

# Resolve project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"

echo "=========================================================="
echo "      YouTube Downloader - Production Setup & Runner      "
echo "=========================================================="
echo "Project Directory: $PROJECT_DIR"
echo ""

# Check or auto-create .env from .env.example for first-time run
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    echo "[INFO] First-time setup: Creating .env from .env.example..."
    cp .env.example .env
    echo "[OK] Created .env configuration file."
fi

# 1. Check Python installation
if command -v python3 >/dev/null 2>&1; then
    PY_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PY_CMD="python"
else
    echo "[ERROR] Python 3 is not installed or not in PATH!"
    echo "Please install Python 3.11+ (e.g. sudo apt install python3 python3-venv)"
    exit 1
fi

PY_VER=$($PY_CMD --version)
echo "[OK] Detected $PY_VER"

# 2. Check or create virtual environment (.venv)
if [ ! -f ".venv/bin/activate" ]; then
    echo "[INFO] Creating virtual environment (.venv)..."
    $PY_CMD -m venv .venv
    echo "[OK] Virtual environment created successfully."
else
    echo "[OK] Found existing virtual environment (.venv)."
fi

# 3. Activate virtual environment
source .venv/bin/activate

# 4. Install / Update dependencies
echo "[INFO] Checking and installing dependencies from requirements.txt..."
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo "[OK] Dependencies are up to date."

# 5. Check FFmpeg availability
if ! command -v ffmpeg >/dev/null 2>&1; then
    echo ""
    echo "----------------------------------------------------------"
    echo "[NOTICE] FFmpeg is not detected in your PATH."
    echo "To install on Linux/macOS:"
    echo "  - Debian/Ubuntu: sudo apt update && sudo apt install -y ffmpeg"
    echo "  - macOS (Homebrew): brew install ffmpeg"
    echo "  - Fedora: sudo dnf install -y ffmpeg"
    echo "----------------------------------------------------------"
    echo ""
else
    echo "[OK] FFmpeg is available on PATH."
fi

# 6. Run Pre-Flight Component Check (Dependencies, yt-dlp, Storage)
echo ""
echo "[INFO] Running pre-flight component checks (yt-dlp, dependencies, storage)..."
if ! python scripts/preflight_check.py; then
    echo ""
    echo "=========================================================="
    echo "[FATAL ERROR] Pre-flight verification failed!"
    echo "The application cannot start safely because a mandatory component failed."
    echo "Please resolve the error above and rerun this script."
    echo "=========================================================="
    exit 1
fi

# 7. Detect custom PORT from .env if present
SERVER_PORT="8000"
if [ -f ".env" ]; then
    ENV_PORT=$(grep -E '^[[:space:]]*PORT[[:space:]]*=' .env | head -n 1 | cut -d '=' -f 2 | tr -d ' "\x27[:space:]')
    if [ -n "$ENV_PORT" ]; then
        SERVER_PORT="$ENV_PORT"
    fi
fi

# 8. Launch browser in background after 2 seconds
(
    sleep 2
    if command -v xdg-open >/dev/null 2>&1; then
        xdg-open "http://localhost:${SERVER_PORT}" >/dev/null 2>&1 || true
    elif command -v open >/dev/null 2>&1; then
        open "http://localhost:${SERVER_PORT}" >/dev/null 2>&1 || true
    fi
) &

# 9. Start production server
echo ""
echo "=========================================================="
echo "[INFO] Starting FastAPI server on http://localhost:${SERVER_PORT} ..."
echo "[INFO] Opening default browser at http://localhost:${SERVER_PORT} ..."
echo "[INFO] Press Ctrl+C to stop the server."
echo "=========================================================="
echo ""
python main.py
