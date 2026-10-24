<div align="center">

  <img src="static/icon.svg" width="80" height="56" alt="YouTube Downloader Logo" />

  <h1>YouTube Downloader</h1>

  <p>
    <strong>A modern Python web application designed for fast, high-quality media downloads from YouTube. Supports true MP3 audio extraction with embedded ID3 metadata and album artwork, alongside full high-definition video downloads (1080p, 2K, 4K) via FFmpeg muxing. Features a sleek single-page interface with an interactive search player, a draggable floating HUD, real-time WebSocket progress tracking, and automated cache management.</strong>
  </p>

  <p>
    <a href="https://github.com/chinmaykrishnroy/YouTubeDownloader/actions/workflows/ci.yml"><img src="https://github.com/chinmaykrishnroy/YouTubeDownloader/actions/workflows/ci.yml/badge.svg?branch=main" alt="CI Pipeline Status" /></a>
    <a href="https://github.com/chinmaykrishnroy/YouTubeDownloader/releases"><img src="https://img.shields.io/github/v/release/chinmaykrishnroy/YouTubeDownloader?color=blue&logo=github" alt="Latest Release" /></a>
    <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.11%20%7C%203.12-3776AB?logo=python&logoColor=white" alt="Python 3.11 | 3.12" /></a>
    <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white" alt="FastAPI" /></a>
    <a href="https://github.com/yt-dlp/yt-dlp"><img src="https://img.shields.io/badge/yt--dlp-Active-FF0000?logo=youtube&logoColor=white" alt="yt-dlp" /></a>
    <a href="https://www.docker.com/"><img src="https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white" alt="Docker" /></a>
    <a href="https://github.com/chinmaykrishnroy/YouTubeDownloader/tree/main/tests"><img src="https://img.shields.io/badge/Tests-52%20Passed-brightgreen?logo=pytest&logoColor=white" alt="Tests" /></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT" /></a>
  </p>

</div>

---

## Features

* **Asynchronous Non-Blocking Engine**: Built with FastAPI and background worker thread pools (`asyncio.to_thread`), preventing I/O stalls during concurrent downloads.
* **True Audio Transcoding**: Real FFmpeg audio extraction to genuine MP3 with user-selectable bitrates (`320kbps`, `256kbps`, `192kbps`, `128kbps`) and automated `mutagen` ID3 metadata tagging (title, artist, album art).
* **Draggable Floating HUD**: Interactive bottom-right floating playback and download HUD that can be freely dragged across the viewport with state persistence.
* **Real-Time WebSocket Streaming**: Bi-directional real-time updates for progress percentage, transfer rate, ETA, and job state transitions with automatic HTTP polling fallback.
* **Pre-Flight Verification Gate**: Built-in verification script (`scripts/preflight_check.py`) that audits dependencies, write permissions, live YouTube connectivity, and FFmpeg before startup.
* **Automated Lifecycle and Storage Guard**: Multi-tier auto-cleanup that purges expired downloads when browser sessions close, evicts oldest cache files when disk quotas are reached, and cleans stale partial files.
* **Crash-Proof Directory Management**: Defensive directory handling ensures the application never crashes if the `downloads/` folder is deleted or emptied at runtime.
* **Production Docker Container**: Debian 12 Bookworm base with native FFmpeg, non-root user isolation, and automatic healthcheck monitoring.

---

## Quick Start

### Automated Start Scripts (Recommended)

The automated launchers create a virtual environment (`.venv`), install dependencies, verify pre-flight components, launch the application, and open your browser automatically.

#### Windows
Double-click `start.bat` or run:
```cmd
start.bat
```

#### Linux and macOS
Make executable and run:
```bash
chmod +x start.sh scripts/run.sh
./start.sh
```

---

### Docker and Docker Compose

Deploy the application in a sandboxed container with pre-configured FFmpeg and health checks:

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

### Manual Setup

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

# 5. Run pre-flight check and start server
python scripts/preflight_check.py
python main.py
```

---

## Configuration

Copy `.env.example` to `.env` to customize runtime parameters:

```bash
cp .env.example .env
```

| Variable | Default | Description |
| :--- | :--- | :--- |
| `HOST` | `0.0.0.0` | Binding network interface IP address |
| `PORT` | `8000` | Application HTTP and WebSocket listening port |
| `DOWNLOADS_DIR_PATH` | OS temporary directory | Optional override for private temporary media storage |
| `MAX_CONCURRENT_DOWNLOADS` | `3` | Maximum simultaneous active download tasks |
| `MAX_DOWNLOADS_CACHE_MB` | `5000` | Disk quota in megabytes before oldest files are purged |
| `DOWNLOAD_TTL_SECONDS` | `1800` | Time-to-live in seconds before completed files expire |
| Session disconnect grace | 15 seconds | Allows refresh/reconnection before deleting that browser session |
| `AUTO_OPEN_BROWSER` | `true` | Automatically open default browser on local startup |
| `YTDLP_COOKIES_PATH` | *(none)* | Path to optional Netscape cookies file for YouTube authentication |
| `YTDLP_COOKIES_FROM_BROWSER` | *(none)* | Optional browser name to extract cookies from (e.g. `chrome`, `firefox`) |

---

## Pre-Flight Verification Gate

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

## Storage Lifecycle and Safety

> **What happens if I delete or empty the `downloads/` folder?**
>
> **The application will not crash.**
> The server uses defensive directory handling (`DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)`). It verifies folder existence at boot, recreates it immediately before any write operation, and safely guards cleanup passes against missing directories.

### Auto-Cleanup Policies:
1. **Private Sessions**: An opaque HttpOnly, SameSite cookie identifies each browser session. Queue listings, job operations, file delivery, and WebSocket events enforce ownership. Tabs in one browser share their queue; other browsers/devices cannot see it.
2. **Session Disconnect**: After the last socket for a browser disconnects, its jobs and temporary files are removed after a 15-second reconnect grace period. Silent connections time out after 60 seconds; sessions without sockets expire after 90 seconds. Running yt-dlp workers stop at the next progress callback and remove any late output when they exit.
3. **File Delivery**: Media remains available privately until the user chooses Save. Once the full response finishes, its job and temporary files are deleted. This confirms transfer to the browser, not whether the user retained the file. Interrupted transfers are also discarded; restart the download to retry. Partial/range downloads are unsupported.

4. **TTL Expiration**: Completed downloads older than `CLEANUP_TTL_SECONDS` (default: 30 minutes) are automatically unlinked.
5. **Storage Quota Manager**: If total cache size exceeds `MAX_DISK_STORAGE_BYTES`, the oldest files are evicted until disk usage is within bounds.
6. **Stale Partial Cleanup**: Interrupted `.part` files are removed during startup and routine sweeps.

The default cache is a process-specific OS temporary directory, and Docker no longer mounts the shared host downloads folder. Existing files in an old host downloads folder are not exposed or deleted by the new app. Run one application worker/replica: sessions and queues are in memory. A multi-replica deployment needs a shared ownership store and routed workers before scaling out.

---

## Testing and CI Pipeline

The project includes a suite of **63 automated unit, integration, and end-to-end tests**:

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
git tag -a v4.0.1 -m "Release v4.0.1"
git push origin v4.0.1
```

---

## API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/system-status` | System health, active jobs count, and FFmpeg status |
| `POST` | `/search` | Query YouTube videos (`{"query": "...", "limit": 10}`) |
| `GET` | `/formats/{video_id}`| Retrieve available video resolutions and audio streams |
| `POST` | `/download` | Queue a download job (`url`, `format`, `quality`, `title`) |
| `GET` | `/jobs` | List this browser session’s active and completed jobs |
| `GET` | `/jobs/{job_id}` | Poll current status, progress percentage, speed, and ETA |
| `DELETE` | `/jobs/{job_id}` | Cancel active download or immediately delete completed file |
| `GET` | `/files/{job_id}` | Stream and download the completed media file to client |
| `WS` | `/ws` | Real-time WebSocket connection for progress broadcasts |

---

## License

Distributed under the [MIT License](LICENSE). Copyright (c) 2023-2026 Chinmay Krishn Roy.
