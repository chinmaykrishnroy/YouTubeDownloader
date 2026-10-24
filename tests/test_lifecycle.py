import asyncio
import tempfile
import threading
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
import main


class TestStorageLifecycle(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name)
        self.storage = patch.object(main, "DOWNLOADS_DIR", self.path)
        self.storage.start()
        self.job_id = "lifecycle-regression"

    def tearDown(self):
        main.jobs.pop(self.job_id, None)
        main.active_transfers.discard(self.job_id)
        self.storage.stop()
        self.temp.cleanup()

    def test_partial_cleanup_and_quota_preserve_active_download(self):
        import os
        main.jobs[self.job_id] = {"id": self.job_id, "status": "downloading"}
        partial = self.path / f"{self.job_id}.mp4.part"
        partial.write_bytes(b"active media")
        old = time.time() - 7200
        os.utime(partial, (old, old))
        with patch.object(main, "MAX_DISK_STORAGE_BYTES", 1):
            main.clean_stale_files(max_age_seconds=60)
        self.assertTrue(partial.exists())

    def test_expired_job_removes_thumbnails_and_partials(self):
        main.jobs[self.job_id] = {
            "id": self.job_id, "status": "complete", "filename": f"{self.job_id}.mp3",
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
        }
        for extension in ("mp3", "webp", "m4a.part"):
            (self.path / f"{self.job_id}.{extension}").write_bytes(b"media")
        main.clean_stale_files(max_age_seconds=60)
        self.assertEqual(list(self.path.iterdir()), [])
        self.assertNotIn(self.job_id, main.jobs)

    def test_quota_removes_completed_job_along_with_its_file(self):
        main.jobs[self.job_id] = {"id": self.job_id, "status": "complete", "filename": f"{self.job_id}.mp3"}
        (self.path / f"{self.job_id}.mp3").write_bytes(b"media")
        with patch.object(main, "MAX_DISK_STORAGE_BYTES", 1):
            main.clean_stale_files()
        self.assertNotIn(self.job_id, main.jobs)
        self.assertEqual(list(self.path.iterdir()), [])

    def test_session_removal_does_not_interrupt_an_active_file_transfer(self):
        main.jobs[self.job_id] = {"id": self.job_id, "status": "complete", "serving": True}
        media = self.path / f"{self.job_id}.mp3"
        media.write_bytes(b"media")
        main.active_transfers.add(self.job_id)
        main.remove_job_data(self.job_id)
        with patch.object(main, "MAX_DISK_STORAGE_BYTES", 1):
            main.clean_stale_files(max_age_seconds=0)
        self.assertTrue(media.exists())
        main.active_transfers.discard(self.job_id)
        main.remove_job_data(self.job_id)
        self.assertFalse(media.exists())

    def test_recent_http_activity_keeps_session_alive_after_socket_loss(self):
        main.sessions["polling-client"] = {"seen": time.monotonic()}
        try:
            with patch.object(main.asyncio, "sleep", new_callable=AsyncMock):
                asyncio.run(main._delayed_session_cleanup("polling-client"))
            self.assertIn("polling-client", main.sessions)
        finally:
            main.sessions.pop("polling-client", None)

    def test_file_symlink_cannot_escape_into_similarly_named_directory(self):
        cache = self.path / "cache"
        sibling = self.path / "cache-outside"
        cache.mkdir()
        sibling.mkdir()
        secret = sibling / "private.mp3"
        secret.write_bytes(b"outside file")
        try:
            (cache / "media.mp3").symlink_to(secret)
        except (OSError, NotImplementedError):
            self.skipTest("Symbolic links unavailable on this platform")
        with patch.object(main, "DOWNLOADS_DIR", cache):
            client = TestClient(main.app)
            client.get("/session")
            owner = client.cookies.get(main.SESSION_COOKIE)
            main.jobs[self.job_id] = {"id": self.job_id, "owner": owner, "status": "complete", "filename": "media.mp3"}
            try:
                self.assertEqual(client.get(f"/files/{self.job_id}").status_code, 403)
                self.assertTrue(secret.exists())
            finally:
                main.sessions.pop(owner, None)


class TestQueueCancellation(unittest.TestCase):
    def test_cancelled_active_job_releases_slot_for_queued_job(self):
        started = threading.Event()
        cancelled = threading.Event()
        invocations = []

        async def worker(job_id):
            invocations.append(job_id)
            if len(invocations) == 1:
                started.set()
                try:
                    await asyncio.Event().wait()
                finally:
                    cancelled.set()
            else:
                main.jobs[job_id]["status"] = "complete"

        with patch.object(main, "MAX_CONCURRENT_DOWNLOADS", 1), patch.object(main, "run_download_process", side_effect=worker):
            with TestClient(main.app) as client:
                client.get("/session")
                first = client.post("/download", json={"url": "https://youtu.be/example"}).json()["job_id"]
                self.assertTrue(started.wait(timeout=2))
                second = client.post("/download", json={"url": "https://youtu.be/example"}).json()["job_id"]
                self.assertEqual(client.get(f"/jobs/{second}").json()["status"], "queued")
                self.assertEqual(client.delete(f"/jobs/{first}").status_code, 200)
                self.assertTrue(cancelled.wait(timeout=2))
                self.assertEqual(client.get(f"/jobs/{second}").json()["status"], "complete")
                self.assertEqual(invocations, [first, second])
