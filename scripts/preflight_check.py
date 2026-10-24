#!/usr/bin/env python3
"""Pre-flight verification script for YouTube Downloader.

Validates that all mandatory components are installed, configured, and
operational before the application starts:
1. Core Python dependencies (fastapi, uvicorn, yt_dlp, aiofiles, mutagen, pydantic)
2. Storage write permissions in downloads directory
3. yt-dlp functional test & YouTube connectivity verification
4. FFmpeg tool availability check
"""
import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))


class PreflightException(Exception):
    """Raised when a mandatory pre-flight check fails."""
    pass


def check_dependencies():
    """Verify that all mandatory Python packages can be imported."""
    print("  [1/4] Checking Python dependencies...", end=" ", flush=True)
    required = {
        "fastapi": "fastapi",
        "uvicorn": "uvicorn",
        "yt_dlp": "yt-dlp",
        "aiofiles": "aiofiles",
        "mutagen": "mutagen",
        "pydantic": "pydantic",
        "httpx": "httpx",
    }
    missing = []
    for mod_name, pkg_name in required.items():
        try:
            __import__(mod_name)
        except ImportError:
            missing.append(pkg_name)

    if missing:
        print("FAILED")
        raise PreflightException(
            f"Missing mandatory Python dependencies: {', '.join(missing)}.\n"
            f"  Resolution: Run 'pip install -r requirements.txt' in your virtual environment."
        )
    print("OK")


def check_storage_permissions():
    """Verify that downloads directory exists and has write permissions."""
    print("  [2/4] Verifying downloads directory permissions...", end=" ", flush=True)
    import main
    downloads_dir = main.DOWNLOADS_DIR
    try:
        downloads_dir.mkdir(parents=True, exist_ok=True)
        probe_file = downloads_dir / ".write_probe.tmp"
        probe_file.write_text("probe_ok", encoding="utf-8")
        probe_file.unlink(missing_ok=True)
    except Exception as exc:
        print("FAILED")
        raise PreflightException(
            f"Downloads directory '{downloads_dir}' is not writable: {exc}.\n"
            f"  Resolution: Check directory permissions or change DOWNLOADS_DIR_PATH in .env."
        )
    print("OK")


def check_ytdlp_operational(skip_network: bool = False):
    """Perform live self-test of yt-dlp extractor and YouTube connectivity."""
    print("  [3/4] Performing yt-dlp functional test & YouTube connectivity...", end=" ", flush=True)
    if skip_network:
        print("SKIPPED (--skip-network)")
        return

    import main
    import yt_dlp

    ydl_opts = main._get_base_ydl_opts()
    ydl_opts["extract_flat"] = True
    ydl_opts["quiet"] = True
    ydl_opts["no_warnings"] = True

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Query a minimal search ping without downloading any media
            res = ydl.extract_info("ytsearch1:ping", download=False)
            entries = res.get("entries", []) if res else []
            if not entries:
                raise RuntimeError("yt-dlp returned 0 results for basic search test.")
    except Exception as exc:
        print("FAILED")
        raise PreflightException(
            f"yt-dlp mandatory self-test failed: {exc}\n\n"
            f"  Possible Causes & Resolutions:\n"
            f"  1. No Internet / DNS failure: Check your network connection.\n"
            f"  2. YouTube Bot Protection / 429 Block: If running on a cloud VPS or datacenter IP,\n"
            f"     YouTube requires cookies or a proxy. In your .env file, configure:\n"
            f"       YTDLP_COOKIES_PATH=./cookies.txt\n"
            f"       YTDLP_PROXY=http://username:password@proxy:port\n"
            f"  3. Outdated yt-dlp: Update yt-dlp by running:\n"
            f"       pip install --upgrade yt-dlp"
        )
    print("OK")


def check_ffmpeg_tool():
    """Check FFmpeg installation (informative check)."""
    print("  [4/4] Checking FFmpeg audio/video encoder...", end=" ", flush=True)
    import main
    has_ff = main.check_ffmpeg()
    if has_ff:
        print("OK (Available)")
    else:
        print("WARNING (Not found)")
        print(
            "        Notice: FFmpeg is not installed. 1080p muxing & MP3 conversion will be disabled.\n"
            "        Run 'winget install Gyan.FFmpeg' (Windows) or 'apt install ffmpeg' (Linux) to install."
        )


def run_preflight(skip_network: bool = False):
    """Execute all pre-flight checks. Exits with code 1 if any mandatory check fails."""
    print("=" * 65)
    print("   YouTube Downloader - Pre-Flight Component Verification")
    print("=" * 65)

    try:
        check_dependencies()
        check_storage_permissions()
        check_ytdlp_operational(skip_network=skip_network)
        check_ffmpeg_tool()
    except PreflightException as exc:
        print("\n" + "!" * 65)
        print(" [FATAL ERROR] PRE-FLIGHT COMPONENT CHECK FAILED")
        print("!" * 65)
        print(f"\n{exc}\n")
        print("The application will NOT start because a mandatory component is broken.")
        print("Please resolve the issue above before restarting.")
        print("!" * 65 + "\n")
        sys.exit(1)
    except Exception as exc:
        print(f"\n[UNEXPECTED ERROR] {exc}")
        sys.exit(1)

    print("-" * 65)
    print(" [OK] All mandatory components passed verification. Starting server...")
    print("=" * 65 + "\n")
    return 0


if __name__ == "__main__":
    skip_net = "--skip-network" in sys.argv or "--build-time" in sys.argv
    run_preflight(skip_network=skip_net)
