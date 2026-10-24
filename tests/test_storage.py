import asyncio
import os
import shutil
import sys
import time
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import main
from main import (
    DOWNLOADS_DIR,
    clean_stale_files,
    get_downloads_dir_size,
    schedule_file_cleanup,
    jobs,
)


class TestStorageAndCleanup(unittest.TestCase):
    """Test suite for storage management, auto-clean, and disk quota enforcement."""

    def setUp(self):
        # Create a fresh isolated test directory
        self.test_dir = DOWNLOADS_DIR / "test_scratch_storage"
        self.test_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        # Clean up test files
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_get_downloads_dir_size(self):
        # Create dummy file in DOWNLOADS_DIR
        test_file = DOWNLOADS_DIR / "temp_size_test.bin"
        test_file.write_bytes(b"A" * 1024)  # 1 KB
        try:
            sz = get_downloads_dir_size()
            self.assertGreaterEqual(sz, 1024)
        finally:
            test_file.unlink(missing_ok=True)

    def test_clean_stale_partial_files(self):
        # Stale partial file (>10 min old) should be deleted
        stale_part = DOWNLOADS_DIR / "stale_download.part"
        stale_part.write_bytes(b"partial bytes")
        # Set mtime to 15 minutes ago
        past_time = time.time() - 900
        os.utime(stale_part, (past_time, past_time))

        # Fresh partial file (<10 min old) should be kept
        fresh_part = DOWNLOADS_DIR / "fresh_download.part"
        fresh_part.write_bytes(b"fresh bytes")

        try:
            removed = clean_stale_files(max_age_seconds=1800)
            self.assertFalse(stale_part.exists(), "Stale partial file should have been unlinked")
            self.assertTrue(fresh_part.exists(), "Fresh partial file should be preserved")
        finally:
            stale_part.unlink(missing_ok=True)
            fresh_part.unlink(missing_ok=True)

    def test_clean_stale_completed_jobs_by_ttl(self):
        # Register a mock job completed 40 minutes ago
        old_job_id = "test_old_ttl_job"
        old_file = DOWNLOADS_DIR / f"{old_job_id}.mp3"
        old_file.write_bytes(b"dummy mp3 data")

        created_at = (datetime.now(timezone.utc) - timedelta(minutes=40)).isoformat()
        jobs[old_job_id] = {
            "id": old_job_id,
            "status": "complete",
            "filename": f"{old_job_id}.mp3",
            "created_at": created_at,
        }

        try:
            # TTL is 1800s (30 mins), so the 40 min old job should be purged
            clean_stale_files(max_age_seconds=1800)
            self.assertFalse(old_file.exists(), "File exceeding TTL should be unlinked")
            self.assertNotIn(old_job_id, jobs, "Job exceeding TTL should be popped from memory")
        finally:
            old_file.unlink(missing_ok=True)
            jobs.pop(old_job_id, None)

    def test_defensive_directory_recreation(self):
        # Deleting the downloads directory should never cause an unhandled crash
        test_file = DOWNLOADS_DIR / "pre_test.txt"
        test_file.write_text("ok")
        test_file.unlink(missing_ok=True)

        # Force clean_stale_files to execute
        removed = clean_stale_files()
        self.assertIsInstance(removed, int)
        self.assertTrue(DOWNLOADS_DIR.exists(), "DOWNLOADS_DIR should automatically exist")

    def test_schedule_file_cleanup(self):
        async def run_async():
            job_id = "test_post_dl_job"
            dummy_file = DOWNLOADS_DIR / f"{job_id}.bin"
            dummy_file.write_bytes(b"to be cleaned")
            jobs[job_id] = {
                "id": job_id,
                "status": "complete",
                "filename": f"{job_id}.bin",
            }
            try:
                self.assertTrue(dummy_file.exists())
                # Delay of 0.1s for fast unit test
                await schedule_file_cleanup(job_id, delay_seconds=0.1)
                self.assertFalse(dummy_file.exists(), "File should be unlinked by schedule_file_cleanup")
            finally:
                dummy_file.unlink(missing_ok=True)
                jobs.pop(job_id, None)

        asyncio.run(run_async())


if __name__ == "__main__":
    unittest.main()
