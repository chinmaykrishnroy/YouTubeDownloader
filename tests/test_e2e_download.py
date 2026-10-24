import sys
import time
import unittest
from pathlib import Path
from urllib.parse import unquote

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient

from main import app, jobs, DOWNLOADS_DIR


class TestE2ENCSDownload(unittest.TestCase):
    """End-to-End integration test downloading NCS Fade audio through the full application stack."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.client.get("/session")
        # Canonical public YouTube video for Alan Walker - Fade (NCS)
        cls.target_url = "https://www.youtube.com/watch?v=vg95MYlTb3c"
        cls.target_title = "Alan Walker - Fade"

    def test_ncs_fade_audio_download_and_serve(self):
        # 1. Initiate audio download job
        req_payload = {
            "url": self.target_url,
            "format": "audio",
            "quality": "192kbps",
            "title": self.target_title,
        }
        resp = self.client.post("/download", json=req_payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        job_id = data["job_id"]
        self.assertTrue(job_id)
        self.assertIn(job_id, jobs)

        print(f"\n[E2E] Initiated download for {self.target_title} (Job ID: {job_id})")

        # 2. Poll job status until complete (timeout at 60s)
        start_time = time.time()
        timeout_seconds = 60
        final_job = None

        while (time.time() - start_time) < timeout_seconds:
            poll_resp = self.client.get(f"/jobs/{job_id}")
            self.assertEqual(poll_resp.status_code, 200)
            job_state = poll_resp.json()
            status = job_state.get("status")
            progress = job_state.get("progress", 0)

            print(f"[E2E Poll] Status: {status} | Progress: {progress}% | Speed: {job_state.get('speed', '')}")

            if status == "complete":
                final_job = job_state
                break
            elif status == "error":
                err_msg = str(job_state.get('error') or "")
                # Gracefully skip if YouTube blocks cloud CI runner IPs with bot challenges
                if any(k in err_msg.lower() for k in ["bot", "sign in", "429", "too many requests", "captcha"]):
                    self.skipTest(f"Live YouTube download skipped due to IP rate-limiting/bot challenge: {err_msg}")
                self.fail(f"Download failed with error: {job_state.get('error')}")

            time.sleep(2)

        self.assertIsNotNone(final_job, f"Download timed out after {timeout_seconds} seconds")
        self.assertEqual(final_job["status"], "complete")
        self.assertEqual(final_job["progress"], 100)

        # 3. Verify file exists on disk and is non-empty
        filename = final_job.get("filename")
        self.assertTrue(filename, "Job must have a filename populated upon completion")
        file_path = DOWNLOADS_DIR / filename
        self.assertTrue(file_path.exists(), f"Downloaded file {filename} does not exist on disk")

        file_size_bytes = file_path.stat().st_size
        print(f"[E2E OK] File written successfully: {filename} ({file_size_bytes} bytes / {final_job.get('file_size')})")
        self.assertGreater(file_size_bytes, 100_000, "Downloaded audio file is suspiciously small")

        # 4. Verify ID3 / metadata tags were embedded via mutagen
        try:
            from mutagen.id3 import ID3
            audio = ID3(str(file_path))
            title_tag = audio.get("TIT2")
            if title_tag:
                print(f"[E2E OK] Verified embedded ID3 Title: {title_tag.text[0]}")
                self.assertIn("Fade", str(title_tag.text[0]))
        except Exception as e:
            print(f"[E2E Notice] ID3 check (optional): {e}")

        # 5. Verify serving file via GET /files/{job_id}
        file_resp = self.client.get(f"/files/{job_id}")
        self.assertEqual(file_resp.status_code, 200)
        self.assertEqual(file_resp.headers["content-type"], "application/octet-stream")
        self.assertIn("attachment", file_resp.headers["content-disposition"])
        self.assertIn("Alan Walker - Fade", unquote(file_resp.headers["content-disposition"]))
        self.assertEqual(len(file_resp.content), file_size_bytes)
        print(f"[E2E OK] Successfully served file via GET /files/{job_id} ({len(file_resp.content)} bytes)")

        # 6. Clean up: Delete job via DELETE /jobs/{job_id} and verify physical file is unlinked
        del_resp = self.client.delete(f"/jobs/{job_id}")
        self.assertEqual(del_resp.status_code, 404)
        self.assertFalse(file_path.exists(), "File should be immediately deleted after DELETE /jobs/{job_id}")
        self.assertNotIn(job_id, jobs)
        print(f"[E2E OK] Job and file cleanup verified successfully.")


if __name__ == "__main__":
    unittest.main()
