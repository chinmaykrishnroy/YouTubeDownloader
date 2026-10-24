import asyncio
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
import main


class TestDownloadWorkers(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "scripts").mkdir()
        self.storage = patch.object(main, "DOWNLOADS_DIR", self.root / "media")
        self.storage.start()
        main.DOWNLOADS_DIR.mkdir()
        self.base = patch.object(main, "BASE_DIR", self.root)
        self.base.start()
        main.jobs["worker-test"] = {
            "id": "worker-test", "owner": "private-owner", "status": "preparing",
            "url": "https://youtu.be/example", "format": "audio", "quality": "192kbps", "title": "Song",
        }

    async def asyncTearDown(self):
        main.jobs.pop("worker-test", None)
        self.base.stop()
        self.storage.stop()
        self.temp.cleanup()

    def worker(self, source):
        (self.root / "scripts" / "download_worker.py").write_text(source)

    async def test_worker_updates_parent_but_cannot_change_ownership(self):
        self.worker('import json,sys\njob=json.loads(sys.stdin.readline())\nprint(json.dumps({"owner":"other", "status":"complete", "filename":"worker-test.mp3", "progress":100}),flush=True)\n')
        with patch.object(main, "broadcast", new_callable=AsyncMock) as broadcast:
            await main.run_download_process("worker-test")
        self.assertEqual(main.jobs["worker-test"]["owner"], "private-owner")
        self.assertEqual(main.jobs["worker-test"]["status"], "complete")
        self.assertEqual(broadcast.call_args.args[0]["type"], "complete")

    async def test_timeout_stops_worker(self):
        self.worker('import sys,time\nsys.stdin.readline()\ntime.sleep(60)\n')
        with patch.object(main, "DOWNLOAD_TIMEOUT_SECONDS", 0.1):
            await asyncio.wait_for(main.run_download_process("worker-test"), timeout=5)
        self.assertEqual(main.jobs["worker-test"]["status"], "error")
        self.assertIn("timed out", main.jobs["worker-test"]["error"])

    async def test_cancel_stops_real_process_and_removes_partials(self):
        self.worker('import os,pathlib,sys,time\nsys.stdin.readline()\np=pathlib.Path(os.environ["DOWNLOADS_DIR_PATH"])/"worker-test.part"\np.write_bytes(b"partial")\ntime.sleep(60)\n')
        task = asyncio.create_task(main.run_download_process("worker-test"))
        partial = main.DOWNLOADS_DIR / "worker-test.part"
        for _ in range(100):
            if partial.exists():
                break
            await asyncio.sleep(0.01)
        self.assertTrue(partial.exists())
        main.jobs.pop("worker-test")
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await asyncio.wait_for(task, timeout=5)
        self.assertFalse(partial.exists())

    async def test_worker_crash_cannot_silently_leave_job_preparing(self):
        self.worker('import sys\nsys.exit(2)\n')
        with self.assertRaisesRegex(RuntimeError, "exited"):
            await main.run_download_process("worker-test")

    async def test_cancellation_during_spawn_still_reaps_process(self):
        from unittest.mock import MagicMock
        entered = asyncio.Event()
        release = asyncio.Event()
        process = MagicMock()

        async def spawn(*args, **kwargs):
            entered.set()
            await release.wait()
            return process

        with patch.object(main.asyncio, "create_subprocess_exec", side_effect=spawn), patch.object(main, "stop_download_process", new_callable=AsyncMock) as stop:
            task = asyncio.create_task(main.run_download_process("worker-test"))
            await entered.wait()
            task.cancel()
            release.set()
            with self.assertRaises(asyncio.CancelledError):
                await task
            stop.assert_awaited_once_with(process)

    async def test_audio_result_selects_media_instead_of_thumbnail(self):
        from unittest.mock import MagicMock
        thumbnail = main.DOWNLOADS_DIR / "worker-test.webp"
        audio = main.DOWNLOADS_DIR / "worker-test.mp3"
        thumbnail.write_bytes(b"thumbnail")
        audio.write_bytes(b"ID3 audio")
        ydl = MagicMock()
        ydl.__enter__.return_value.extract_info.return_value = {"id": "example"}
        ydl.__enter__.return_value.prepare_filename.return_value = str(main.DOWNLOADS_DIR / "worker-test.webm")
        with patch.object(main.yt_dlp, "YoutubeDL", return_value=ydl) as constructor, patch.object(main, "check_ffmpeg", return_value=True), patch.object(main, "broadcast", new_callable=AsyncMock):
            await asyncio.to_thread(main.run_download, "worker-test", "https://youtu.be/example", "audio", "192kbps", "Song", asyncio.get_running_loop())
        processors = constructor.call_args.args[0]["postprocessors"]
        self.assertEqual([processor["key"] for processor in processors], ["FFmpegExtractAudio", "FFmpegMetadata", "EmbedThumbnail"])
        self.assertEqual(main.jobs["worker-test"]["filename"], audio.name)
        self.assertEqual(main.jobs["worker-test"]["status"], "complete")
        self.assertFalse(thumbnail.exists())

    async def test_no_media_file_is_an_error_not_a_completed_download(self):
        from unittest.mock import MagicMock
        ydl = MagicMock()
        ydl.__enter__.return_value.extract_info.return_value = {"id": "example"}
        ydl.__enter__.return_value.prepare_filename.return_value = str(main.DOWNLOADS_DIR / "worker-test.webm")
        with patch.object(main.yt_dlp, "YoutubeDL", return_value=ydl), patch.object(main, "broadcast", new_callable=AsyncMock):
            await asyncio.to_thread(main.run_download, "worker-test", "https://youtu.be/example", "audio", "192kbps", "Song", asyncio.get_running_loop())
        self.assertEqual(main.jobs["worker-test"]["status"], "error")


class TestDownloadRequests(unittest.TestCase):
    def test_worker_changes_queued_to_preparing_before_network_work(self):
        with patch.object(main, "run_download_process", new_callable=AsyncMock) as worker:
            with TestClient(main.app) as client:
                client.get("/session")
                response = client.post("/download", json={"url": "https://youtu.be/example", "format": "audio"})
                job_id = response.json()["job_id"]
                self.assertEqual(client.get(f"/jobs/{job_id}").json()["status"], "preparing")
                self.assertEqual(response.json()["job"]["quality"], "192kbps")
                worker.assert_awaited_once_with(job_id)

    def test_worker_setup_failure_is_reported_as_error(self):
        with patch.object(main, "run_download_process", side_effect=RuntimeError("cannot start")):
            with TestClient(main.app) as client:
                client.get("/session")
                response = client.post("/download", json={"url": "https://youtu.be/example"})
                job_id = response.json()["job_id"]
                self.assertEqual(client.get(f"/jobs/{job_id}").json()["status"], "error")

    def test_invalid_format_and_quality_never_create_jobs(self):
        client = TestClient(main.app)
        client.get("/session")
        for payload in ({"format": "invalid"}, {"format": "audio", "quality": "720p"}, {"format": "video", "quality": "320kbps"}, {"quality": ""}):
            with self.subTest(payload=payload):
                response = client.post("/download", json={"url": "https://youtu.be/example", **payload})
                self.assertEqual(response.status_code, 422)

    def test_deceptive_youtube_urls_are_rejected(self):
        client = TestClient(main.app)
        client.get("/session")
        for url in ("https://youtube.com:443@evil.example/video", "https://youtube.com.evil.example/video", "https://youtube.com:invalid/video"):
            with self.subTest(url=url):
                self.assertEqual(client.post("/download", json={"url": url}).status_code, 400)
