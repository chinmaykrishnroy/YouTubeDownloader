import asyncio
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
import main


class TestPrivateSessions(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.storage = patch.object(main, "DOWNLOADS_DIR", Path(self.directory.name))
        self.storage.start()
        self.a = TestClient(main.app)
        self.b = TestClient(main.app)
        self.a.get("/session")
        self.b.get("/session")
        self.owner = self.a.cookies.get(main.SESSION_COOKIE)
        main.jobs["private-job"] = {
            "id": "private-job", "owner": self.owner, "title": "Private song",
            "status": "complete", "filename": "private-job.mp3",
        }
        (main.DOWNLOADS_DIR / "private-job.mp3").write_bytes(b"private media")

    def tearDown(self):
        main.jobs.pop("private-job", None)
        main.sessions.pop(self.owner, None)
        main.sessions.pop(self.b.cookies.get(main.SESSION_COOKIE), None)
        self.storage.stop()
        self.directory.cleanup()

    def test_other_client_cannot_list_read_delete_or_download(self):
        self.assertEqual(self.b.get("/jobs").json(), {"jobs": []})
        self.assertEqual(self.b.get("/system-status").json()["active_jobs"], 0)
        for method, path in (("get", "/jobs/private-job"), ("delete", "/jobs/private-job"), ("get", "/files/private-job")):
            self.assertEqual(getattr(self.b, method)(path).status_code, 404)
        self.assertEqual(TestClient(main.app).get("/files/private-job").status_code, 401)
        self.assertNotIn("owner", self.a.get("/jobs/private-job").json())

    def test_socket_snapshots_and_events_are_private(self):
        with self.a.websocket_connect("/ws") as a, self.b.websocket_connect("/ws") as b:
            self.assertEqual(len(a.receive_json()["jobs"]), 1)
            self.assertEqual(b.receive_json()["jobs"], [])
            self.a.delete("/jobs/private-job")
            self.assertEqual(a.receive_json(), {"type": "removed", "job_id": "private-job"})
            # A B-owned event is a sentinel: no A event may precede it.
            main.jobs["b-job"] = {"id": "b-job", "owner": self.b.cookies.get(main.SESSION_COOKIE)}
            self.b.delete("/jobs/b-job")
            self.assertEqual(b.receive_json(), {"type": "removed", "job_id": "b-job"})

    def test_delivery_consumes_file_and_queue_entry(self):
        response = self.a.get("/files/private-job")
        self.assertEqual(response.content, b"private media")
        self.assertEqual(response.headers["cache-control"], "no-store")
        self.assertFalse((main.DOWNLOADS_DIR / "private-job.mp3").exists())
        self.assertEqual(self.a.get("/jobs").json(), {"jobs": []})

    def test_disconnect_cleanup_only_removes_its_owner(self):
        other_owner = self.b.cookies.get(main.SESSION_COOKIE)
        main.jobs["other-job"] = {"id": "other-job", "owner": other_owner}
        (main.DOWNLOADS_DIR / "private-job.mp4.part").write_bytes(b"partial")
        try:
            with patch.object(main, "SESSION_DISCONNECT_GRACE_SECONDS", 0):
                asyncio.run(main._delayed_session_cleanup(self.owner))
            self.assertNotIn(self.owner, main.sessions)
            self.assertNotIn("private-job", main.jobs)
            self.assertIn("other-job", main.jobs)
            self.assertEqual(list(main.DOWNLOADS_DIR.iterdir()), [])
        finally:
            main.jobs.pop("other-job", None)

    def test_cross_origin_mutation_is_denied(self):
        self.assertEqual(self.a.delete("/jobs/private-job", headers={"Origin": "https://evil.example"}).status_code, 403)
        self.assertEqual(self.a.get("/jobs/private-job").status_code, 200)

    def test_reconnect_cancels_old_disconnect_timer(self):
        from unittest.mock import MagicMock
        timer = MagicMock()
        main.sessions[self.owner]["disconnect_task"] = timer
        with self.a.websocket_connect("/ws") as socket:
            self.assertEqual(len(socket.receive_json()["jobs"]), 1)
            timer.cancel.assert_called_once()

    def test_worker_removes_output_created_after_session_expiry(self):
        from unittest.mock import MagicMock
        ydl = MagicMock()
        def finish_after_disconnect(*args, **kwargs):
            main.remove_job_data("private-job")
            (main.DOWNLOADS_DIR / "private-job.mp3").write_bytes(b"late output")
            return {"id": "video"}
        ydl.__enter__.return_value.extract_info.side_effect = finish_after_disconnect
        with patch.object(main.yt_dlp, "YoutubeDL", return_value=ydl):
            asyncio.run(asyncio.to_thread(main.run_download, "private-job", "https://youtu.be/video", "audio", "192kbps", "Song", None))
        self.assertNotIn("private-job", main.jobs)
        self.assertEqual(list(main.DOWNLOADS_DIR.iterdir()), [])

    def test_ranges_do_not_consume_file(self):
        self.assertEqual(self.a.get("/files/private-job", headers={"Range": "bytes=0-3"}).status_code, 400)
        self.assertEqual(self.a.get("/files/private-job").content, b"private media")

    def test_session_cookie_is_private_and_not_persistent(self):
        response = TestClient(main.app).get("/session")
        cookie = response.headers["set-cookie"]
        self.assertIn("HttpOnly", cookie)
        self.assertIn("SameSite=strict", cookie)
        self.assertNotIn("Max-Age", cookie)
