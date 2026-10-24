import asyncio
import logging
import os
import re
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import aiofiles
import yt_dlp
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

BASE_DIR = Path(__file__).parent

# ---------------------------------------------------------------------------
# Load .env configuration automatically if present
# ---------------------------------------------------------------------------
def _load_dotenv(dotenv_path: Path):
    if not dotenv_path.exists():
        return
    try:
        with open(dotenv_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                if k and k not in os.environ:
                    os.environ[k] = v
    except Exception as e:
        print(f"Notice: Could not read .env file: {e}")

_load_dotenv(BASE_DIR / ".env")

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("yt_downloader")

# ---------------------------------------------------------------------------
# App setup & Environment PATH fix for WinGet tools (ffmpeg)
# ---------------------------------------------------------------------------
_local_appdata = os.environ.get("LOCALAPPDATA", "")
_winget_links = Path(_local_appdata) / "Microsoft" / "WinGet" / "Links"
if _winget_links.exists() and str(_winget_links) not in os.environ.get("PATH", ""):
    os.environ["PATH"] = f"{_winget_links};" + os.environ.get("PATH", "")

STATIC_DIR = BASE_DIR / "static"
_downloads_custom = os.environ.get("DOWNLOADS_DIR_PATH")
DOWNLOADS_DIR = Path(_downloads_custom).resolve() if _downloads_custom else (BASE_DIR / "downloads")
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Production Constants & Concurrency Controls
# ---------------------------------------------------------------------------
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8000"))
RELOAD = os.environ.get("RELOAD", "false").lower() in ("true", "1", "yes")
MAX_CONCURRENT_DOWNLOADS = int(os.environ.get("MAX_CONCURRENT_DOWNLOADS", 4))
DOWNLOAD_SEMAPHORE: Optional[asyncio.Semaphore] = None
CLEANUP_TTL_SECONDS = int(os.environ.get("CLEANUP_TTL_SECONDS", 1800))  # 30 mins file retention
FILE_POST_DOWNLOAD_CLEANUP_SECONDS = int(os.environ.get("FILE_POST_DOWNLOAD_CLEANUP_SECONDS", 90))  # Auto-clean 90s after user starts saving file
MAX_DISK_STORAGE_BYTES = int(os.environ.get("MAX_DISK_STORAGE_BYTES", 3 * 1024 * 1024 * 1024))  # 3GB max disk cache
YTDLP_COOKIES_PATH = os.environ.get("YTDLP_COOKIES_PATH", "")
YTDLP_PROXY = os.environ.get("YTDLP_PROXY", "")

# In-memory job store & WebSocket connections
jobs: dict[str, dict] = {}
active_connections: set[WebSocket] = set()
cleanup_task: Optional[asyncio.Task] = None
session_cleanup_timer: Optional[asyncio.TimerHandle] = None


# ---------------------------------------------------------------------------
# Auto-Clean & Storage Management Logic
# ---------------------------------------------------------------------------
def get_downloads_dir_size() -> int:
    """Return total bytes occupied by files in DOWNLOADS_DIR."""
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    if not DOWNLOADS_DIR.exists():
        return 0
    for p in DOWNLOADS_DIR.iterdir():
        if p.is_file():
            try:
                total += p.stat().st_size
            except Exception:
                pass
    return total


def clean_stale_files(max_age_seconds: int = CLEANUP_TTL_SECONDS) -> int:
    """Clean completed downloads older than max_age_seconds, stale partials, and enforce quota."""
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    if not DOWNLOADS_DIR.exists():
        return 0
    now = datetime.now(timezone.utc).timestamp()
    removed_count = 0

    # 1. Clean orphaned partial/interrupted files (*.part, *.ytdl, *.tmp) older than 10 mins
    for pattern in ("*.part", "*.ytdl", "*.tmp", "*.temp"):
        for fp in DOWNLOADS_DIR.glob(pattern):
            try:
                if (now - fp.stat().st_mtime) > 600:
                    fp.unlink(missing_ok=True)
                    removed_count += 1
                    logger.info(f"[Auto-Clean] Removed stale partial file: {fp.name}")
            except Exception:
                pass

    # 2. Clean completed or error jobs older than max_age_seconds
    for job_id, job in list(jobs.items()):
        if job.get("status") in ("complete", "error"):
            try:
                created_ts = datetime.fromisoformat(job["created_at"]).timestamp()
            except Exception:
                created_ts = now

            if (now - created_ts) > max_age_seconds:
                fn = job.get("filename")
                if fn:
                    fp = DOWNLOADS_DIR / fn
                    if fp.exists():
                        try:
                            fp.unlink(missing_ok=True)
                            removed_count += 1
                            logger.info(f"[Auto-Clean] TTL expired for job {job_id}: {fn}")
                        except Exception:
                            pass
                jobs.pop(job_id, None)

    # 3. Clean files in DOWNLOADS_DIR not tracked by active jobs older than max_age_seconds
    active_filenames = {j.get("filename") for j in jobs.values() if j.get("filename")}
    for fp in DOWNLOADS_DIR.iterdir():
        if fp.is_file() and fp.name not in active_filenames:
            try:
                if (now - fp.stat().st_mtime) > max_age_seconds:
                    fp.unlink(missing_ok=True)
                    removed_count += 1
            except Exception:
                pass

    # 4. Enforce max storage quota (if disk exceeds MAX_DISK_STORAGE_BYTES, purge oldest files)
    current_size = get_downloads_dir_size()
    if current_size > MAX_DISK_STORAGE_BYTES:
        logger.warning(f"[Storage Quota] Cache {current_size / (1024*1024):.1f}MB exceeds limit. Purging oldest files...")
        file_list = []
        for fp in DOWNLOADS_DIR.iterdir():
            if fp.is_file():
                try:
                    file_list.append((fp.stat().st_mtime, fp))
                except Exception:
                    pass
        file_list.sort(key=lambda x: x[0])  # oldest first
        for _, fp in file_list:
            if current_size <= MAX_DISK_STORAGE_BYTES:
                break
            try:
                sz = fp.stat().st_size
                fp.unlink(missing_ok=True)
                current_size -= sz
                removed_count += 1
                logger.info(f"[Storage Quota] Purged: {fp.name}")
            except Exception:
                pass

    return removed_count


async def schedule_file_cleanup(job_id: str, delay_seconds: int = FILE_POST_DOWNLOAD_CLEANUP_SECONDS):
    """Wait for client to complete browser download, then securely unlink file from server disk."""
    await asyncio.sleep(delay_seconds)
    if job_id in jobs:
        job = jobs[job_id]
        fn = job.get("filename")
        if fn:
            fp = DOWNLOADS_DIR / fn
            if fp.exists():
                try:
                    fp.unlink(missing_ok=True)
                    logger.info(f"[Post-Download Clean] Removed served file for job {job_id}: {fn}")
                except Exception as e:
                    logger.warning(f"Failed cleaning file {fn}: {e}")


async def periodic_cleanup_loop():
    """Background garbage collection loop running every 2 minutes."""
    while True:
        try:
            await asyncio.sleep(120)
            clean_stale_files(max_age_seconds=CLEANUP_TTL_SECONDS)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.warning(f"Error in periodic cleanup loop: {e}")


@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    global cleanup_task, DOWNLOAD_SEMAPHORE
    DOWNLOAD_SEMAPHORE = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)
    # Initial cleanup of any interrupted downloads from past crashes
    clean_stale_files(max_age_seconds=600)
    # Start periodic background garbage collection
    cleanup_task = asyncio.create_task(periodic_cleanup_loop())
    logger.info("YouTube Downloader initialized. Background auto-clean loop active.")
    yield
    if cleanup_task and not cleanup_task.done():
        cleanup_task.cancel()
    # Clean partial/interrupted files on shutdown
    for pattern in ("*.part", "*.ytdl", "*.tmp", "*.temp"):
        for fp in DOWNLOADS_DIR.glob(pattern):
            try:
                fp.unlink(missing_ok=True)
            except Exception:
                pass
    logger.info("YouTube Downloader shutdown complete.")


# ---------------------------------------------------------------------------
# FastAPI Instance & Middleware Setup
# ---------------------------------------------------------------------------
app = FastAPI(title="YouTube Downloader - Production", lifespan=lifespan)

app.add_middleware(GZipMiddleware, minimum_size=1000)

_origins_raw = os.environ.get("ALLOWED_ORIGINS", "*")
ALLOWED_ORIGINS = [orig.strip() for orig in _origins_raw.split(",") if orig.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------
class SearchRequest(BaseModel):
    query: str
    limit: int = 10


class RelatedRequest(BaseModel):
    video_id: str
    title: str = ""
    limit: int = 8


class DownloadRequest(BaseModel):
    url: str
    format: str = "video"   # "video" | "audio"
    quality: str = "720p"
    title: str = ""
    thumbnail: str = ""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def sanitize_filename(name: str) -> str:
    """Remove characters that are unsafe in filenames."""
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = name.strip().strip(".")
    return name or "download"


def format_view_count(n: Optional[int]) -> str:
    if n is None:
        return "N/A views"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M views"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K views"
    return f"{n} views"


def format_duration(secs: Optional[int]) -> str:
    if secs is None:
        return ""
    secs = int(secs)
    h, rem = divmod(secs, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


# ---------------------------------------------------------------------------
# WebSocket broadcasting
# ---------------------------------------------------------------------------
async def broadcast(message: dict):
    dead: set[WebSocket] = set()
    for ws in list(active_connections):
        try:
            await ws.send_json(message)
        except Exception:
            dead.add(ws)
    active_connections.difference_update(dead)


# ---------------------------------------------------------------------------
# yt-dlp helpers & Anti-Blocking Config
# ---------------------------------------------------------------------------
def _get_cookies_opts() -> dict:
    """Try to grab browser cookies or custom cookiefile to bypass YouTube 403 blocks.
    Returns extra yt-dlp opts dict; empty dict if nothing available."""
    if YTDLP_COOKIES_PATH and Path(YTDLP_COOKIES_PATH).exists():
        return {"cookiefile": str(Path(YTDLP_COOKIES_PATH).resolve())}
    import shutil
    # Prefer Chrome, then Firefox, then Edge — whichever is installed
    for browser in ("chrome", "firefox", "edge", "brave", "chromium", "opera"):
        try:
            if shutil.which(browser) or shutil.which(browser.capitalize()):
                return {"cookiesfrombrowser": (browser, None, None, None)}
        except Exception:
            pass
    return {}


def _get_base_ydl_opts() -> dict:
    """Base options for yt-dlp with anti-blocking headers, cookies, and proxy."""
    opts: dict = {
        "quiet": True,
        "no_warnings": True,
        "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    }
    opts.update(_get_cookies_opts())
    if YTDLP_PROXY:
        opts["proxy"] = YTDLP_PROXY
    return opts


def search_youtube(query: str, limit: int = 10) -> list[dict]:
    ydl_opts = _get_base_ydl_opts()
    ydl_opts["extract_flat"] = True
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
            entries = result.get("entries", []) if result else []
            videos = []
            for e in entries:
                if not e:
                    continue
                vid_id = e.get("id", "")
                videos.append(
                    {
                        "id": vid_id,
                        "title": e.get("title", "Unknown"),
                        "thumbnail": e.get("thumbnail")
                        or (
                            f"https://i.ytimg.com/vi/{vid_id}/hqdefault.jpg"
                            if vid_id
                            else ""
                        ),
                        "duration": format_duration(e.get("duration")),
                        "channel": e.get("uploader") or e.get("channel") or "Unknown",
                        "view_count": format_view_count(e.get("view_count")),
                        "url": e.get("url") or f"https://www.youtube.com/watch?v={vid_id}",
                    }
                )
            return videos
    except Exception as exc:
        logger.warning(f"Search failed for '{query}': {exc}")
        return []


def get_ydl_format(fmt: str, quality: str, has_ffmpeg: bool) -> dict:
    """Return yt-dlp options dict for the requested format/quality."""
    if fmt == "audio":
        quality_map = {"320kbps": "320", "192kbps": "192", "128kbps": "128"}
        bitrate = quality_map.get(quality, "192")
        opts: dict = {"format": "bestaudio/best"}
        if has_ffmpeg:
            opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": bitrate,
                }
            ]
        return opts
    else:
        height_map = {"1080p": 1080, "720p": 720, "480p": 480, "360p": 360}
        h = height_map.get(quality, 720)
        if has_ffmpeg:
            fmt_str = f"bestvideo[height<={h}]+bestaudio/best[height<={h}]"
        else:
            fmt_str = f"best[height<={h}]/best"
        return {"format": fmt_str}


def check_ffmpeg() -> bool:
    import shutil
    return shutil.which("ffmpeg") is not None


def embed_metadata(filepath: Path, info: dict, thumbnail_url: str = ""):
    """Embed title, artist, album, and thumbnail cover art into audio/video files."""
    try:
        import urllib.request
        from mutagen.mp4 import MP4, MP4Cover
        from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, APIC, ID3NoHeaderError

        ext = filepath.suffix.lower()
        title = info.get("title") or filepath.stem
        artist = info.get("artist") or info.get("uploader") or info.get("channel") or "YouTube"
        album = info.get("album") or title
        year = str(info.get("upload_date") or "")[:4]

        # Download thumbnail if needed for cover art
        cover_data = None
        cover_mime = "image/jpeg"
        thumb_url = thumbnail_url or info.get("thumbnail")
        if thumb_url:
            try:
                req = urllib.request.Request(thumb_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=8) as resp:
                    cover_data = resp.read()
                    if thumb_url.lower().endswith(".png"):
                        cover_mime = "image/png"
            except Exception:
                cover_data = None

        if ext == ".mp3":
            try:
                audio = ID3(str(filepath))
            except ID3NoHeaderError:
                audio = ID3()
            if title:
                audio["TIT2"] = TIT2(encoding=3, text=title)
            if artist:
                audio["TPE1"] = TPE1(encoding=3, text=artist)
            if album:
                audio["TALB"] = TALB(encoding=3, text=album)
            if year:
                audio["TDRC"] = TDRC(encoding=3, text=year)
            if cover_data:
                audio["APIC"] = APIC(
                    encoding=3,
                    mime=cover_mime,
                    type=3,  # Cover front
                    desc="Cover",
                    data=cover_data,
                )
            audio.save(str(filepath))

        elif ext in (".mp4", ".m4a"):
            try:
                video = MP4(str(filepath))
                if title:
                    video["\xa9nam"] = [title]
                if artist:
                    video["\xa9ART"] = [artist]
                    video["aART"] = [artist]
                if album:
                    video["\xa9alb"] = [album]
                if year:
                    video["\xa9day"] = [year]
                if cover_data:
                    fmt = MP4Cover.FORMAT_PNG if cover_mime == "image/png" else MP4Cover.FORMAT_JPEG
                    video["covr"] = [MP4Cover(cover_data, image_format=fmt)]
                video.save()
            except Exception:
                pass
    except Exception as e:
        print(f"Metadata embed notice: {e}")


def run_download(job_id: str, url: str, fmt: str, quality: str, title: str, loop: asyncio.AbstractEventLoop):
    """Blocking download – runs in a thread pool."""
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    has_ffmpeg = check_ffmpeg()
    safe_title = sanitize_filename(title) if title else "%(title)s"
    # Use job_id ONLY for on-disk uniqueness; the clean title is used when serving to browser
    outtmpl = str(DOWNLOADS_DIR / f"{job_id}.%(ext)s")

    ydl_extra = get_ydl_format(fmt, quality, has_ffmpeg)

    def progress_hook(d: dict):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes", 0)
            pct = (downloaded / total * 100) if total else 0
            speed = d.get("_speed_str", "").strip() or "—"
            eta = d.get("_eta_str", "").strip() or "—"

            jobs[job_id].update(
                {"status": "downloading", "progress": round(pct, 1), "speed": speed, "eta": eta}
            )
            asyncio.run_coroutine_threadsafe(
                broadcast(
                    {
                        "type": "progress",
                        "job_id": job_id,
                        "progress": round(pct, 1),
                        "status": "downloading",
                        "speed": speed,
                        "eta": eta,
                    }
                ),
                loop,
            )
        elif d["status"] == "finished":
            jobs[job_id].update({"progress": 99, "status": "processing"})
            asyncio.run_coroutine_threadsafe(
                broadcast({"type": "progress", "job_id": job_id, "progress": 99, "status": "processing", "speed": "", "eta": ""}),
                loop,
            )

    ydl_opts = _get_base_ydl_opts()
    ydl_opts.update({
        "outtmpl": outtmpl,
        "progress_hooks": [progress_hook],
        "noplaylist": True,
        "retries": 5,
        "fragment_retries": 5,
        "sleep_interval": 1,
        **ydl_extra,
    })

    # ── Embed metadata (title, artist, album art) when ffmpeg is available ──
    if has_ffmpeg:
        meta_pp: list[dict] = [{"key": "FFmpegMetadata", "add_metadata": True}]
        if fmt == "audio":
            # Embed album art thumbnail into the MP3
            meta_pp.append({"key": "EmbedThumbnail"})
        # Prepend metadata postprocessors (format-specific ones were already added via ydl_extra)
        existing_pp = ydl_opts.get("postprocessors", [])
        ydl_opts["postprocessors"] = meta_pp + existing_pp
        ydl_opts["writethumbnail"] = fmt == "audio"   # download thumb only for audio embed

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # Find the actual output file — after post-processing the extension may differ
            filename = None
            if info:
                prepared = ydl.prepare_filename(info)
                stem = Path(prepared).stem   # e.g. "3f70..." (the job_id)
                for f in DOWNLOADS_DIR.iterdir():
                    if f.is_file() and f.stem == stem:
                        filename = f.name
                        break
            if not filename:
                # Fallback: newest file matching job_id prefix
                candidates = sorted(
                    DOWNLOADS_DIR.glob(f"{job_id}.*"),
                    key=lambda p: p.stat().st_mtime,
                    reverse=True,
                )
                # Exclude thumbnail files (.jpg/.webp written by writethumbnail)
                candidates = [p for p in candidates if p.suffix.lower() not in (".jpg", ".jpeg", ".webp", ".png")]
                filename = candidates[0].name if candidates else None

            file_size = None
            if filename:
                fp = DOWNLOADS_DIR / filename
                if fp.exists():
                    embed_metadata(fp, info or {}, thumbnail_url=jobs[job_id].get("thumbnail") or "")
                    size_bytes = fp.stat().st_size
                    if size_bytes >= 1_000_000:
                        file_size = f"{size_bytes / 1_000_000:.1f} MB"
                    else:
                        file_size = f"{size_bytes / 1_000:.1f} KB"

            # Clean up standalone thumbnail image files
            for stray in DOWNLOADS_DIR.glob(f"{job_id}.*"):
                if stray.suffix.lower() in (".jpg", ".jpeg", ".webp", ".png"):
                    try:
                        stray.unlink(missing_ok=True)
                    except Exception:
                        pass

            jobs[job_id].update(
                {
                    "status": "complete",
                    "progress": 100,
                    "filename": filename,
                    "file_size": file_size,
                    "speed": "",
                    "eta": "",
                }
            )
            asyncio.run_coroutine_threadsafe(
                broadcast({"type": "complete", "job_id": job_id, "filename": filename, "file_size": file_size}),
                loop,
            )
    except Exception as exc:
        error_msg = str(exc)
        jobs[job_id].update({"status": "error", "error": error_msg})
        asyncio.run_coroutine_threadsafe(
            broadcast({"type": "error", "job_id": job_id, "error": error_msg}),
            loop,
        )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    path = STATIC_DIR / "index.html"
    async with aiofiles.open(path, "r", encoding="utf-8") as f:
        return await f.read()


FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 70">
  <rect width="100" height="70" rx="15" fill="#ff0000"/>
  <polygon points="38,18 38,52 68,35" fill="white"/>
</svg>"""


@app.get("/system-status")
async def system_status():
    """Check system environment (ffmpeg availability, platform install guide)."""
    import platform
    has_ff = check_ffmpeg()
    os_name = platform.system().lower()
    if "windows" in os_name:
        cmd = "winget install Gyan.FFmpeg"
        guide = "Windows: Run 'winget install Gyan.FFmpeg' in PowerShell or Command Prompt, then restart the app."
    elif "darwin" in os_name:
        cmd = "brew install ffmpeg"
        guide = "macOS: Run 'brew install ffmpeg' in Terminal, then restart the app."
    else:
        cmd = "sudo apt update && sudo apt install -y ffmpeg"
        guide = "Linux: Run 'sudo apt update && sudo apt install -y ffmpeg' in Terminal, then restart the app."

    return {
        "has_ffmpeg": has_ff,
        "platform": os_name,
        "install_cmd": cmd,
        "guide": guide,
        "active_jobs": len(jobs),
    }


@app.post("/related")
async def related_endpoint(req: RelatedRequest):
    """Fetch suggested / related videos based on title or video ID."""
    loop = asyncio.get_event_loop()
    query = req.title.strip() if req.title else f"related to {req.video_id}"
    try:
        results = await loop.run_in_executor(None, search_youtube, query, req.limit + 4)
        filtered = [v for v in results if v.get("id") != req.video_id][:req.limit]
        return {"results": filtered}
    except Exception as e:
        return {"results": [], "error": str(e)}


@app.get("/favicon.ico")
async def favicon():
    from fastapi.responses import Response
    return Response(content=FAVICON_SVG, media_type="image/svg+xml")


@app.get("/downloads-page", response_class=HTMLResponse)
async def serve_downloads():
    path = STATIC_DIR / "index.html"
    async with aiofiles.open(path, "r", encoding="utf-8") as f:
        return await f.read()


@app.post("/search")
async def search_endpoint(req: SearchRequest):
    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(None, search_youtube, req.query, req.limit)
    return {"results": results}


@app.post("/download")
async def start_download(req: DownloadRequest):
    job_id = str(uuid.uuid4())
    job = {
        "id": job_id,
        "url": req.url,
        "title": req.title or req.url,
        "thumbnail": req.thumbnail,
        "format": req.format,
        "quality": req.quality,
        "status": "queued",
        "progress": 0.0,
        "speed": "",
        "eta": "",
        "filename": None,
        "error": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "file_size": None,
    }
    jobs[job_id] = job

    # Broadcast new job immediately to all active WebSocket connections
    await broadcast({"type": "new_job", "job": job})

    loop = asyncio.get_event_loop()

    async def _managed_worker():
        global DOWNLOAD_SEMAPHORE
        if DOWNLOAD_SEMAPHORE is None:
            DOWNLOAD_SEMAPHORE = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)
        async with DOWNLOAD_SEMAPHORE:
            await loop.run_in_executor(
                None,
                run_download,
                job_id,
                req.url,
                req.format,
                req.quality,
                req.title,
                loop,
            )

    loop.create_task(_managed_worker())

    return {"job_id": job_id, "job": job}


@app.get("/jobs")
async def list_jobs():
    return {"jobs": list(jobs.values())}


@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]


@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    job = jobs.pop(job_id)
    # Immediately delete the physical file if it exists
    if job.get("filename"):
        fp = DOWNLOADS_DIR / job["filename"]
        if fp.exists():
            try:
                fp.unlink(missing_ok=True)
                logger.info(f"[Manual Delete] Removed file: {fp.name}")
            except Exception:
                pass
    return {"ok": True}


@app.get("/files/{job_id}")
async def serve_file(job_id: str, background_tasks: BackgroundTasks):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    job = jobs[job_id]
    if job["status"] != "complete" or not job.get("filename"):
        raise HTTPException(status_code=400, detail="File not ready")

    # Production Path-Traversal Security Check
    fn = job["filename"]
    if not fn or ".." in fn or "/" in fn or "\\" in fn:
        raise HTTPException(status_code=400, detail="Invalid filename format")

    fp = (DOWNLOADS_DIR / fn).resolve()
    if not str(fp).startswith(str(DOWNLOADS_DIR.resolve())):
        raise HTTPException(status_code=403, detail="Access denied")
    if not fp.exists():
        raise HTTPException(status_code=404, detail="File has already been cleaned or removed")

    # Track download metrics & schedule auto-cleanup after file is saved by user
    job["download_count"] = job.get("download_count", 0) + 1
    job["last_downloaded_at"] = datetime.now(timezone.utc).isoformat()
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(schedule_file_cleanup(job_id, delay_seconds=FILE_POST_DOWNLOAD_CLEANUP_SECONDS))
    except RuntimeError:
        background_tasks.add_task(schedule_file_cleanup, job_id, delay_seconds=FILE_POST_DOWNLOAD_CLEANUP_SECONDS)

    # Build a clean, human-readable download filename (no UUID)
    ext = Path(job["filename"]).suffix          # e.g. ".mp3" or ".mp4"
    clean_title = sanitize_filename(job.get("title", "download"))[:180]  # cap length
    download_name = f"{clean_title}{ext}"

    # RFC 5987 encoding for non-ASCII filenames (covers Unicode titles)
    import urllib.parse
    encoded_name = urllib.parse.quote(download_name, safe="")

    return FileResponse(
        path=str(fp),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": (
                f"attachment; filename=\"{download_name}\"; "
                f"filename*=UTF-8''{encoded_name}"
            )
        },
    )


@app.get("/formats/{video_id}")
async def get_formats(video_id: str):
    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = _get_base_ydl_opts()
    loop = asyncio.get_event_loop()

    def _fetch():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            fmts = []
            seen = set()
            for f in (info.get("formats") or []):
                h = f.get("height")
                ext = f.get("ext", "")
                label = f"{h}p" if h else ext
                if label not in seen:
                    seen.add(label)
                    fmts.append({"label": label, "format_id": f.get("format_id", ""), "ext": ext})
            return fmts

    try:
        fmts = await loop.run_in_executor(None, _fetch)
        return {"formats": fmts}
    except Exception as exc:
        logger.warning(f"Failed to fetch formats for {video_id}: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


async def _delayed_session_cleanup():
    """Triggered when client sessions disconnect. Waits 45s; if still 0 connections, auto-cleans completed files."""
    await asyncio.sleep(45)
    if len(active_connections) == 0:
        logger.info("[Session Clean] All client sessions closed. Running auto-clean on completed files...")
        clean_stale_files(max_age_seconds=60)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    logger.info(f"WebSocket client connected. Active sessions: {len(active_connections)}")
    # Send current jobs snapshot on connect
    try:
        await websocket.send_json({"type": "snapshot", "jobs": list(jobs.values())})
        while True:
            # Keep alive – wait for client ping or disconnect
            data = await websocket.receive_text()
    except (WebSocketDisconnect, Exception):
        pass
    finally:
        active_connections.discard(websocket)
        logger.info(f"WebSocket client disconnected. Active sessions: {len(active_connections)}")
        if len(active_connections) == 0:
            asyncio.create_task(_delayed_session_cleanup())


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on http://{HOST}:{PORT} (Reload: {RELOAD})")
    uvicorn.run("main:app", host=HOST, port=PORT, reload=RELOAD, log_level=LOG_LEVEL.lower())
