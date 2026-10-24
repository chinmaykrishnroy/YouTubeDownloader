import asyncio
import os
import platform
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
import main
from main import (
    app,
    jobs,
    active_connections,
    broadcast,
    _load_dotenv,
    _get_cookies_opts,
    _delayed_session_cleanup,
    periodic_cleanup_loop,
    clean_stale_files,
    embed_metadata,
    DOWNLOADS_DIR,
    lifespan,
)


class TestExtendedCoverage(unittest.TestCase):
    """Targeted tests covering edge cases, platform branches, quota eviction, and endpoints."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_load_dotenv_parsing(self):
        # Create a temporary .env file
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".env") as f:
            f.write("# Comment line\n")
            f.write("TEST_ENV_VAR_ALPHA=HelloWorld\n")
            f.write("TEST_ENV_VAR_BETA='QuotedValue'\n")
            f.write("   TEST_ENV_VAR_GAMMA = \"SpacedValue\"  \n")
            f.write("INVALID_LINE_WITHOUT_EQUALS\n")
            f_path = Path(f.name)

        try:
            _load_dotenv(f_path)
            self.assertEqual(os.environ.get("TEST_ENV_VAR_ALPHA"), "HelloWorld")
            self.assertEqual(os.environ.get("TEST_ENV_VAR_BETA"), "QuotedValue")
            self.assertEqual(os.environ.get("TEST_ENV_VAR_GAMMA"), "SpacedValue")
        finally:
            f_path.unlink(missing_ok=True)
            for k in ("TEST_ENV_VAR_ALPHA", "TEST_ENV_VAR_BETA", "TEST_ENV_VAR_GAMMA"):
                os.environ.pop(k, None)

    def test_load_dotenv_nonexistent(self):
        # Should cleanly return without exception
        _load_dotenv(Path("non_existent_dotenv_file_12345.env"))

    def test_quota_eviction_when_exceeded(self):
        # Temporarily mock MAX_DISK_STORAGE_BYTES to 1500 bytes
        orig_max = main.MAX_DISK_STORAGE_BYTES
        main.MAX_DISK_STORAGE_BYTES = 1500

        # Create 3 dummy files
        f1 = DOWNLOADS_DIR / "quota_test_file1.bin"
        f2 = DOWNLOADS_DIR / "quota_test_file2.bin"
        f1.write_bytes(b"X" * 1000)
        f2.write_bytes(b"Y" * 1000)

        # Set f1 to be older than f2
        now = os.path.getmtime(f2)
        os.utime(f1, (now - 100, now - 100))

        try:
            # Total size is 2000 > 1500 limit. Oldest file (f1) must be purged
            purged = clean_stale_files(max_age_seconds=999999)
            self.assertFalse(f1.exists(), "Older file f1 should have been purged by quota policy")
            self.assertTrue(f2.exists(), "Newer file f2 should be retained")
            self.assertGreaterEqual(purged, 1)
        finally:
            main.MAX_DISK_STORAGE_BYTES = orig_max
            f1.unlink(missing_ok=True)
            f2.unlink(missing_ok=True)

    def test_broadcast_dead_connection_pruning(self):
        async def run_async():
            # Mock WebSocket that fails on send
            mock_dead_ws = MagicMock()
            mock_dead_ws.send_json = MagicMock(side_effect=RuntimeError("Connection lost"))

            mock_alive_ws = MagicMock()
            # Asynchronous mock for healthy connection
            future = asyncio.Future()
            future.set_result(None)
            mock_alive_ws.send_json = MagicMock(return_value=future)

            active_connections.add(mock_dead_ws)
            active_connections.add(mock_alive_ws)

            try:
                await broadcast({"test": "data"})
                # Dead websocket should be pruned from set
                self.assertNotIn(mock_dead_ws, active_connections)
                self.assertIn(mock_alive_ws, active_connections)
            finally:
                active_connections.discard(mock_dead_ws)
                active_connections.discard(mock_alive_ws)

        asyncio.run(run_async())

    def test_system_status_platform_branches(self):
        # Test Darwin (macOS)
        with patch("platform.system", return_value="Darwin"):
            resp = self.client.get("/system-status")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("brew install ffmpeg", resp.json()["guide"])

        # Test Linux
        with patch("platform.system", return_value="Linux"):
            resp = self.client.get("/system-status")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("apt update", resp.json()["guide"])

    def test_related_endpoint(self):
        resp = self.client.post("/related", json={"video_id": "vg95MYlTb3c", "title": "Alan Walker Fade", "limit": 2})
        if resp.status_code == 500:
            err = resp.json().get("detail", "")
            if any(k in str(err).lower() for k in ["bot", "429", "sign in", "rate"]):
                self.skipTest(f"Live related query skipped on CI rate limit: {err}")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("results", data)
        self.assertIsInstance(data["results"], list)

    def test_formats_endpoint(self):
        # Fast query for public video formats
        resp = self.client.get("/formats/vg95MYlTb3c")
        if resp.status_code == 500:
            err = resp.json().get("detail", "")
            if any(k in str(err).lower() for k in ["bot", "429", "sign in", "rate"]):
                self.skipTest(f"Live formats query skipped on CI rate limit: {err}")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("formats", data)
        self.assertIsInstance(data["formats"], list)

    def test_formats_endpoint_invalid_video(self):
        resp = self.client.get("/formats/INVALID_ID_99999999")
        self.assertEqual(resp.status_code, 500)

    def test_cookies_opts_with_custom_path(self):
        # Create a mock cookies.txt
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".txt") as f:
            f.write("# Netscape HTTP Cookie File\n")
            c_path = Path(f.name)

        orig = main.YTDLP_COOKIES_PATH
        try:
            main.YTDLP_COOKIES_PATH = str(c_path)
            opts = _get_cookies_opts()
            self.assertIn("cookiefile", opts)
            self.assertEqual(opts["cookiefile"], str(c_path.resolve()))
        finally:
            main.YTDLP_COOKIES_PATH = orig
            c_path.unlink(missing_ok=True)

    def test_delayed_session_cleanup_logic(self):
        async def run_async():
            # Call delayed session cleanup with 0 connections
            active_connections.clear()
            # Fast test: patch sleep to return immediately
            with patch("asyncio.sleep", return_value=None):
                await _delayed_session_cleanup()

        asyncio.run(run_async())

    def test_lifespan_context_manager(self):
        async def run_async():
            async with lifespan(app):
                self.assertIsNotNone(main.cleanup_task)
                self.assertIsNotNone(main.DOWNLOAD_SEMAPHORE)
            # Yield one tick so cancellation propagates
            await asyncio.sleep(0.01)
            self.assertTrue(main.cleanup_task.cancelled() or main.cleanup_task.done())

        asyncio.run(run_async())

    def test_embed_metadata_mp4(self):
        # Create a mock MP4 file header
        mp4_path = DOWNLOADS_DIR / "test_meta.mp4"
        # Minimum ftyp atom for mp4
        mp4_path.write_bytes(b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00isommp42")
        info = {
            "title": "Test Title",
            "artist": "Test Artist",
            "album": "Test Album",
            "upload_date": "20261024",
        }
        try:
            # Should run without uncaught exceptions
            embed_metadata(mp4_path, info)
        finally:
            mp4_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
