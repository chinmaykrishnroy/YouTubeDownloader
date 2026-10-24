import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote
from unittest.mock import patch

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient

from main import app, jobs, DOWNLOADS_DIR, sanitize_filename


class TestEndpoints(unittest.TestCase):
    """Test suite for HTTP REST and WebSocket endpoints."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.client.get("/session")

    def test_get_index_page(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("text/html", resp.headers["content-type"])
        self.assertIn("YT Downloader", resp.text)

    def test_get_downloads_page(self):
        resp = self.client.get("/downloads-page")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("text/html", resp.headers["content-type"])

    def test_get_favicon(self):
        resp = self.client.get("/favicon.ico")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers["content-type"], "image/svg+xml")
        self.assertIn("<svg", resp.text)

    def test_get_system_status(self):
        resp = self.client.get("/system-status")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("has_ffmpeg", data)
        self.assertIn("platform", data)
        self.assertIn("active_jobs", data)
        self.assertIsInstance(data["has_ffmpeg"], bool)

    def test_jobs_list_and_lifecycle(self):
        test_id = "test_lifecycle_job_123"
        jobs[test_id] = {
            "owner": self.client.cookies.get("yt_session"),
            "id": test_id,
            "title": "Mock Job Title",
            "status": "queued",
            "progress": 0.0,
            "filename": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        try:
            # 1. GET /jobs
            resp = self.client.get("/jobs")
            self.assertEqual(resp.status_code, 200)
            job_list = resp.json()["jobs"]
            self.assertTrue(any(j["id"] == test_id for j in job_list))

            # 2. GET /jobs/{job_id}
            resp_single = self.client.get(f"/jobs/{test_id}")
            self.assertEqual(resp_single.status_code, 200)
            self.assertEqual(resp_single.json()["title"], "Mock Job Title")

            # 3. DELETE /jobs/{job_id}
            resp_del = self.client.delete(f"/jobs/{test_id}")
            self.assertEqual(resp_del.status_code, 200)
            self.assertTrue(resp_del.json().get("ok"))
            self.assertNotIn(test_id, jobs)

            # 4. GET /jobs/{job_id} on deleted job returns 404
            resp_404 = self.client.get(f"/jobs/{test_id}")
            self.assertEqual(resp_404.status_code, 404)
        finally:
            jobs.pop(test_id, None)

    def test_path_traversal_protection(self):
        # Malicious job attempting to break out of downloads directory
        hacker_id = "test_exploit_job"
        jobs[hacker_id] = {
            "owner": self.client.cookies.get("yt_session"),
            "id": hacker_id,
            "title": "Exploit",
            "status": "complete",
            "filename": "../../etc/passwd",
        }
        try:
            resp = self.client.get(f"/files/{hacker_id}")
            # Should be blocked with 400 Bad Request or 403 Forbidden
            self.assertIn(resp.status_code, (400, 403))
        finally:
            jobs.pop(hacker_id, None)

    def test_serve_completed_file(self):
        job_id = "test_served_file_job"
        filename = f"{job_id}.mp3"
        target_file = DOWNLOADS_DIR / filename
        target_file.write_bytes(b"ID3\x03\x00\x00\x00mock audio stream")

        jobs[job_id] = {
            "owner": self.client.cookies.get("yt_session"),
            "id": job_id,
            "title": "Alan Walker - Fade",
            "status": "complete",
            "filename": filename,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        try:
            resp = self.client.get(f"/files/{job_id}")
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.headers["content-type"], "application/octet-stream")
            # Verify RFC 5987 Content-Disposition header with clean filename
            self.assertIn("Content-Disposition", resp.headers)
            self.assertIn("Alan Walker - Fade.mp3", unquote(resp.headers["Content-Disposition"]))
            self.assertEqual(resp.content, b"ID3\x03\x00\x00\x00mock audio stream")
        finally:
            target_file.unlink(missing_ok=True)
            jobs.pop(job_id, None)

    def test_serve_completed_file_with_unicode_title(self):
        job_id = "test_unicode_file_job"
        filename = f"{job_id}.mp3"
        target_file = DOWNLOADS_DIR / filename
        payload = b"mock audio stream"
        target_file.write_bytes(payload)
        jobs[job_id] = {
            "owner": self.client.cookies.get("yt_session"),
            "id": job_id,
            "status": "complete",
            "filename": filename,
        }
        try:
            for title in ("हिन्दी गाना", "日本語の曲", "Music 🎵", "Café", "song\r\n title"):
                with self.subTest(title=title):
                    target_file.write_bytes(payload)
                    jobs[job_id] = {"id": job_id, "owner": self.client.cookies.get("yt_session"), "status": "complete", "filename": filename, "title": title}
                    resp = self.client.get(f"/files/{job_id}")
                    self.assertEqual(resp.status_code, 200)
                    self.assertEqual(resp.content, payload)
                    disposition = resp.headers["content-disposition"]
                    self.assertTrue(disposition.startswith("attachment; filename*=utf-8''"))
                    self.assertEqual(unquote(disposition.split("''", 1)[1]), f"{sanitize_filename(title)}.mp3")
                    self.assertTrue(disposition.isascii())
        finally:
            target_file.unlink(missing_ok=True)
            jobs.pop(job_id, None)

    def test_download_ssrf_rejection(self):
        malicious_urls = [
            "file:///etc/passwd",
            "http://169.254.169.254/latest/meta-data/",
            "http://localhost:6379/",
            "https://evil.com/malicious.mp4",
        ]
        for url in malicious_urls:
            with self.subTest(url=url):
                resp = self.client.post("/download", json={"url": url, "format": "video", "quality": "720p"})
                self.assertEqual(resp.status_code, 400)
                self.assertIn("Invalid YouTube URL", resp.json()["detail"])

    def test_post_search(self):
        # Test real search endpoint with limit=2
        with patch("main.search_youtube", return_value=[{"id": "example", "title": "Song", "url": "https://youtu.be/example"}]) as search:
            resp = self.client.post("/search", json={"query": "NCS", "limit": 2})
            search.assert_called_once_with("NCS", 2)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("results", data)
        self.assertIsInstance(data["results"], list)
        if len(data["results"]) > 0:
            first = data["results"][0]
            self.assertIn("id", first)
            self.assertIn("title", first)
            self.assertIn("url", first)

    def test_search_failure_has_an_error_status(self):
        with patch("main.search_youtube", side_effect=RuntimeError("network unavailable")):
            resp = self.client.post("/search", json={"query": "Song"})
        self.assertEqual(resp.status_code, 503)
        self.assertIn("temporarily unavailable", resp.json()["detail"])

    def test_blank_search_is_rejected(self):
        self.assertEqual(self.client.post("/search", json={"query": "   "}).status_code, 422)

    def test_websocket_snapshot(self):
        with self.client.websocket_connect("/ws") as websocket:
            data = websocket.receive_json()
            self.assertEqual(data["type"], "snapshot")
            self.assertIn("jobs", data)


if __name__ == "__main__":
    unittest.main()
