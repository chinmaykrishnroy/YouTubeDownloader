@echo off
setlocal enabledelayedexpansion
title YouTube Downloader - Production Runner

:: Navigate to project root directory
cd /d "%~dp0\.."
set "PROJECT_DIR=%CD%"

echo ==========================================================
echo       YouTube Downloader - Production Setup & Runner
echo ==========================================================
echo Project Directory: %PROJECT_DIR%
echo.

:: Check or auto-create .env from .env.example for first-time run
if not exist ".env" (
    if exist ".env.example" (
        echo [INFO] First-time setup: Creating .env from .env.example...
        copy ".env.example" ".env" >nul
        echo [OK] Created .env configuration file.
    )
)

:: 1. Check Python installation
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    where py >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Python is not installed or not in PATH!
        echo Please install Python 3.10+ from https://www.python.org/downloads/
        pause
        exit /b 1
    )
    set "PY_CMD=py"
) else (
    set "PY_CMD=python"
)

for /f "tokens=*" %%i in ('%PY_CMD% --version 2^>^&1') do set "PY_VER=%%i"
echo [OK] Detected %PY_VER%

:: 2. Check or create virtual environment (.venv)
if not exist ".venv\Scripts\activate.bat" (
    echo [INFO] Creating virtual environment (.venv)...
    %PY_CMD% -m venv .venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created successfully.
) else (
    echo [OK] Found existing virtual environment (.venv).
)

:: 3. Activate virtual environment
call .venv\Scripts\activate.bat

:: 4. Install / Update dependencies
echo [INFO] Checking and installing dependencies from requirements.txt...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Dependency installation finished with warnings or errors. Retrying...
    pip install -r requirements.txt
)
echo [OK] Dependencies are up to date.

:: 5. Check FFmpeg availability
where ffmpeg >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ----------------------------------------------------------
    echo [NOTICE] FFmpeg is not detected in your PATH.
    echo 1080p video merging and MP3 conversion require FFmpeg.
    echo To install on Windows, run in PowerShell:
    echo     winget install Gyan.FFmpeg
    echo (The app will still run and download 720p/360p video).
    echo ----------------------------------------------------------
    echo.
) else (
    echo [OK] FFmpeg is available on PATH.
)

:: 6. Run Pre-Flight Component Check (Dependencies, yt-dlp, Storage)
echo.
echo [INFO] Running pre-flight component checks (yt-dlp, dependencies, storage)...
python scripts\preflight_check.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ==========================================================
    echo [FATAL ERROR] Pre-flight verification failed!
    echo The application cannot start safely because a mandatory component failed.
    echo Please resolve the error above and rerun this script.
    echo ==========================================================
    pause
    exit /b 1
)

:: 7. Detect custom PORT from .env if present
set "SERVER_PORT=8000"
if exist ".env" (
    for /f "usebackq tokens=1,2 delims==" %%A in (".env") do (
        set "KEY=%%A"
        set "KEY=!KEY: =!"
        if /i "!KEY!"=="PORT" (
            set "VAL=%%B"
            set "VAL=!VAL: =!"
            set "VAL=!VAL:"=!"
            set "VAL=!VAL:'=!"
            if not "!VAL!"=="" set "SERVER_PORT=!VAL!"
        )
    )
)

:: 8. Launch browser after a brief delay in background
start "" /B cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:!SERVER_PORT!"

:: 9. Start production server
echo.
echo ==========================================================
echo [INFO] Starting FastAPI server on http://localhost:!SERVER_PORT! ...
echo [INFO] Opening default browser at http://localhost:!SERVER_PORT! ...
echo [INFO] Press Ctrl+C in this window to stop the server.
echo ==========================================================
echo.
python main.py
pause
