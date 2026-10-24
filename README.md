# YouTube Downloader (Production Grade)

A high-performance YouTube downloader and inline player web application built with **FastAPI**, **yt-dlp**, Tailwind CSS, and real-time WebSockets.

---

## First-Time Run (Step-by-Step)

To configure and launch the application for the first time:

### Step 1: Create your `.env` configuration file
Copy the provided `.env.example` template:

- **Windows (Command Prompt)**:
  ```cmd
  copy .env.example .env
  ```
- **Windows (PowerShell)**:
  ```powershell
  Copy-Item .env.example .env
  ```
- **Linux & macOS**:
  ```bash
  cp .env.example .env
  ```
*(You can edit `.env` in any text editor to customize `PORT`, `HOST`, `MAX_CONCURRENT_DOWNLOADS`, etc. Default port is `8000`.)*

### Step 2: Run the Start Script
Execute the launcher for your operating system:

- **Windows**: Double-click `start.bat` or run:
  ```cmd
  start.bat
  ```
- **Linux & macOS**: Make executable and run:
  ```bash
  chmod +x start.sh scripts/run.sh
  ./start.sh
  ```

> **Note**: Even if you skip Step 1, `start.bat` and `./start.sh` will automatically detect the missing `.env` file and generate it from `.env.example` for you. The script automatically sets up `.venv`, installs dependencies, launches the server, and opens your default browser directly to `http://localhost:<PORT>`.

---

## What Happens If I Delete the `downloads/` Folder?

**The application will NEVER crash.**

The server uses defensive directory handling (`DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)`):
- On startup, the server automatically checks for the downloads directory and creates it if missing.
- Whenever a download begins, the server verifies the folder exists and creates it on the fly.
- Periodic cleanup routines safely check folder existence before scanning files.

You can safely delete or empty the `downloads/` folder at any time without worrying about crashes.

---

## Manual Setup (Without Start Scripts)

```bash
# 1. Create and activate virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start server
python main.py
```

Access the application in your browser at `http://localhost:8000`.

---

## Production Hardening & Auto-Clean Features

1. **Intelligent Auto-Clean Logic**:
   - **Post-Download Cleanup**: Once a user completes saving a file to their device via `/files/{job_id}`, the server unlinks the physical file after 90 seconds.
   - **Session Closure Cleanup**: When all active browser WebSocket sessions disconnect, an auto-clean runs after a 45-second grace period to purge completed downloads and free storage.
   - **Periodic Garbage Collection**: A background loop scans every 2 minutes, removing files older than 30 minutes (`CLEANUP_TTL_SECONDS`) and cleaning orphaned `.part`/`.ytdl` files.
   - **Disk Quota Protection**: Enforces a configurable 3GB ceiling (`MAX_DISK_STORAGE_BYTES`); oldest downloads are purged first if the threshold is exceeded.
   - **Manual Cleanup**: The "Clear finished" and job remove buttons immediately unlink the files from disk.

2. **Security & Reliability**:
   - **Path Traversal Shield**: `/files/{job_id}` strictly verifies path resolution within the downloads folder, blocking any directory traversal.
   - **Concurrency Semaphore**: Limits simultaneous yt-dlp tasks to 4 concurrent downloads (`MAX_CONCURRENT_DOWNLOADS`) to prevent memory and CPU exhaustion.
   - **GZip Compression**: All JSON and HTML payloads are compressed on the wire.
   - **Graceful Lifecycle**: Interrupted temp files are cleaned up on startup and shutdown.

3. **FFmpeg Integration**:
   - Supports 1080p video merging and high-bitrate MP3 conversion.
   - If FFmpeg is missing, a persistent dismissible banner provides OS-specific install commands (`winget install Gyan.FFmpeg` for Windows, `apt install ffmpeg` for Linux, `brew install ffmpeg` for macOS).

---

## Environment Variables (.env)

All settings can be customized in `.env` (refer to `.env.example`):

| Variable | Default | Description |
|---|---|---|
| `HOST` | `0.0.0.0` | IP address to bind HTTP server (`0.0.0.0` for all LAN or `127.0.0.1` for local only) |
| `PORT` | `8000` | Port number for web server & WebSockets |
| `RELOAD` | `false` | Enable auto-reload on code change (`true` for development) |
| `ALLOWED_ORIGINS` | `*` | Comma-separated list of permitted CORS origins |
| `MAX_CONCURRENT_DOWNLOADS` | `4` | Max parallel yt-dlp worker threads (subsequent tasks queue cleanly) |
| `DOWNLOADS_DIR_PATH` | `./downloads` | Custom disk path for downloaded media files |
| `CLEANUP_TTL_SECONDS` | `1800` | Retention period for completed files (30 minutes) |
| `FILE_POST_DOWNLOAD_CLEANUP_SECONDS` | `90` | Time to keep file after user clicks save |
| `MAX_DISK_STORAGE_BYTES` | `3221225472` | 3GB storage limit before auto-purging oldest files |
| `YTDLP_COOKIES_PATH` | `""` | Path to cookies.txt (useful for cloud VPS hosting to bypass YouTube bot blocks) |
| `YTDLP_PROXY` | `""` | Optional proxy URL (e.g. `http://user:pass@host:port`) |
| `LOG_LEVEL` | `INFO` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

---

## Docker Deployment (Production)

To deploy using Docker and Docker Compose:

```bash
# 1. Build and run in detached mode
docker-compose up -d --build

# 2. Check logs
docker-compose logs -f

# 3. Stop container
docker-compose down
```
The Docker setup includes FFmpeg, non-root Python runtime, persistent download volumes, and automated health checks.

---

## Pre-Flight Verification Gate

Before the server starts, `scripts/preflight_check.py` automatically validates all mandatory components:
1. **Python Dependencies**: Verifies imports of `fastapi`, `uvicorn`, `yt_dlp`, `aiofiles`, `mutagen`, `pydantic`.
2. **Storage Permissions**: Confirms `downloads/` directory exists and is writable.
3. **yt-dlp Live Functional Test**: Performs a live query to verify yt-dlp extractor health and YouTube connectivity (checks for IP blocks/429 walls).
4. **FFmpeg Availability**: Audits encoder tools.

If any mandatory check fails, the pre-flight gate **halts immediately**, raises a fatal exception, and prevents the server or browser from launching in a broken state.

---

## Automated Test Suite

A comprehensive test suite covering 52 test cases (unit helpers, pre-flight verification, storage lifecycle, quota eviction, REST/WebSocket endpoints, path-traversal security, and live NCS Fade audio end-to-end download) is included:

```bash
# Run all 52 tests using the unified test runner
python tests/run_tests.py

# Alternatively, run using pytest
pytest tests/

# Run the pre-flight verification gate independently
python scripts/preflight_check.py

# Generate test coverage report
python -m coverage run --source=main -m unittest discover tests
python -m coverage report -m
```
