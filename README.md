<div align="center">

# ⚡ YouTube Downloader

<p align="center">
  <strong>High-performance, asynchronous YouTube media downloader with genuine audio transcoding, real-time WebSocket HUD tracking, and defensive storage management.</strong>
</p>

[![CI & Release Pipeline](https://github.com/chinmaykrishnroy/YouTubeDownloader/actions/workflows/ci.yml/badge.svg)](https://github.com/chinmaykrishnroy/YouTubeDownloader/actions/workflows/ci.yml)
[![Latest Release](https://img.shields.io/github/v/release/chinmaykrishnroy/YouTubeDownloader?color=blue&logo=github)](https://github.com/chinmaykrishnroy/YouTubeDownloader/releases)
[![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![yt-dlp](https://img.shields.io/badge/yt--dlp-Active-FF0000?logo=youtube&logoColor=white)](https://github.com/yt-dlp/yt-dlp)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/Tests-52%20Passed-brightgreen?logo=pytest&logoColor=white)](https://github.com/chinmaykrishnroy/YouTubeDownloader/tree/main/tests)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 🌟 Key Features

* ⚡ **Asynchronous Non-Blocking Engine**: Built with FastAPI and background worker thread pools (`asyncio.to_thread`), preventing I/O stalls during concurrent downloads.
* 🎵 **True Audio Transcoding**: Real FFmpeg audio extraction to genuine MP3 with user-selectable bitrates (`320kbps`, `256kbps`, `192kbps`, `128kbps`) and automated `mutagen` ID3 metadata tagging (title, artist, album art).
* 🖥️ **Draggable Floating HUD**: Interactive bottom-right floating playback and download HUD that can be freely dragged across the viewport with state persistence.
* 📡 **Real-Time WebSocket Streaming**: Bi-directional real-time updates for progress percentage, transfer rate, ETA, and job state transitions with automatic HTTP polling fallback.
* 🛡️ **Pre-Flight Verification Gate**: Built-in verification script (`scripts/preflight_check.py`) that audits dependencies, write permissions, live YouTube connectivity, and FFmpeg before startup.
* 🧹 **Automated Lifecycle & Storage Guard**: Multi-tier auto-cleanup that purges expired downloads when browser sessions close, evicts oldest cache files when disk quotas are reached, and cleans stale partial files.
* 🔒 **Crash-Proof Directory Management**: Defensive directory handling ensures the application never crashes if the `downloads/` folder is deleted or emptied at runtime.
* 🐳 **Production Docker Container**: Debian 12 Bookworm base with native FFmpeg, non-root user isolation, and automatic healthcheck monitoring.

---

## 🚀 Quick Start

### Option 1: Automated Start Scripts (Recommended)

The automated launchers create a virtual environment (`.venv`), install dependencies, verify pre-flight components, launch the application, and open your browser automatically.

#### 🪟 Windows
Double-click `start.bat` or run:
```cmd
start.bat
```

#### 🐧 Linux & 🍎 macOS
Make executable and run:
```bash
chmod +x start.sh scripts/run.sh
./start.sh
```

---

### Option 2: Docker & Docker Compose

Deploy the application in a sandboxed, production container with pre-configured FFmpeg and health checks:

```bash
# Build and run container in detached mode
docker compose up -d --build

# View real-time container logs
docker compose logs -f

# Stop container
docker compose down
```

Access the interface at `http://localhost:8000`.

---

### Option 3: Manual Setup

```bash
# 1. Clone repository
git clone https://github.com/chinmaykrishnroy/YouTubeDownloader.git
cd YouTubeDownloader

# 2. Create and activate virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy configuration
cp .env.example .env

# 5. Run pre-flight check & start server
python scripts/preflight_check.py
python main.py
```

---

## ⚙️ Configuration

Copy `.env.example` to `.env` to customize runtime parameters:

```bash
cp .env.example .env
```

| Variable | Default | Description |
| :--- | :--- | :--- |
| `HOST` | `0.0.0.0` | Binding network interface IP address |
| `PORT` | `8000` | Application HTTP & WebSocket listening port |
| `DOWNLOADS_DIR` | `downloads` | Local directory for temporary storage of downloads |
| `MAX_CONCURRENT_DOWNLOADS` | `3` | Maximum simultaneous active download tasks |
| `MAX_DOWNLOADS_CACHE_MB` | `5000` | Disk quota in megabytes before oldest files are purged |
| `DOWNLOAD_TTL_SECONDS` | `1800` | Time-to-live in seconds before completed files expire |
| `SESSION_CLEANUP_DELAY_SECONDS`| `30` | Grace period after all client tabs close before auto-cleaning |
| `AUTO_OPEN_BROWSER` | `true` | Automatically open default browser on local startup |
| `YTDL_COOKIES_PATH` | *(none)* | Path to optional Netscape cookies file for YouTube authentication |

---

## 🛡️ Pre-Flight Verification Gate

Before the server accepts traffic, [`scripts/preflight_check.py`](scripts/preflight_check.py) verifies critical components:

```
=================================================================
   YouTube Downloader - Pre-Flight Component Verification
=================================================================
  [1/4] Checking Python dependencies... OK
  [2/4] Verifying downloads directory permissions... OK
  [3/4] Performing yt-dlp functional test & YouTube connectivity... OK
  [4/4] Checking FFmpeg audio/video encoder... OK (Available)
-----------------------------------------------------------------
 [OK] All mandatory components passed verification. Starting server...
=================================================================
```

If a mandatory component is missing, startup halts immediately with an actionable troubleshooting guide.

---

## 🧹 Storage Lifecycle & Deletion Safety

> **What happens if I delete or empty the `downloads/` folder?**
>
> **The application will NEVER crash.**
> The server uses defensive directory handling (`DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)`). It verifies folder existence at boot, recreates it immediately before any write operation, and safely guards cleanup passes against missing directories.

### Auto-Cleanup Policies:
1. **Session Disconnect**: When all connected browser tabs disconnect, a background cleaner runs after a 30-second grace window to purge completed downloads.
2. **TTL Expiration**: Completed downloads older than `DOWNLOAD_TTL_SECONDS` (default: 30 minutes) are automatically unlinked.
3. **Storage Quota Manager**: If total cache size exceeds `MAX_DOWNLOADS_CACHE_MB`, the oldest files are evicted until disk usage is within bounds.
4. **Stale Partial Cleanup**: Interrupted `.part` files are removed during startup and routine sweeps.

---

## 🧪 Testing & CI Pipeline

The project includes a comprehensive suite of **52 automated unit, integration, and end-to-end tests**:

```bash
# Run full test suite
python tests/run_tests.py
```

### GitHub Actions CI Workflow:
* **Matrix Testing**: Validates every pull request and push against Python `3.11` and `3.12` on both `ubuntu-latest` and `windows-latest`.
* **Branch Protection**: Builds fail immediately if any unit or integration test fails.
* **Docker Verification**: Verifies container build and runs live container health checks.
* **Tagged Release Automation**: Pushing a tag (`v*.*.*`) triggers the release pipeline, generating release notes and attaching standalone release packages.

```bash
# Create and push a new release tag
git tag -a v4.0.0 -m "Release v4.0.0"
git push origin v4.0.0
```

---

## 📡 API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/system-status` | System health, active jobs count, and FFmpeg status |
| `POST` | `/search` | Query YouTube videos (`{"query": "...", "limit": 10}`) |
| `GET` | `/formats/{video_id}`| Retrieve available video resolutions and audio streams |
| `POST` | `/download` | Queue a download job (`url`, `format`, `quality`, `title`) |
| `GET` | `/jobs` | List all active and completed download jobs |
| `GET` | `/jobs/{job_id}` | Poll current status, progress percentage, speed, and ETA |
| `DELETE` | `/jobs/{job_id}` | Cancel active download or immediately delete completed file |
| `GET` | `/files/{job_id}` | Stream and download the completed media file to client |
| `WS` | `/ws` | Real-time WebSocket connection for progress broadcasts |

---

## 📄 License

Distributed under the [MIT License](LICENSE). Copyright (c) 2023–2026 Chinmay Krishn Roy.
