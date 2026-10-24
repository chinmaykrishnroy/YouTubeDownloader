import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ensure project root is in sys.path
PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from scripts.preflight_check import (
    check_dependencies,
    check_storage_permissions,
    check_ytdlp_operational,
    check_ffmpeg_tool,
    PreflightException,
    run_preflight,
)


class TestPreflightCheck(unittest.TestCase):
    """Test suite for the pre-flight verification system."""

    def test_check_dependencies_success(self):
        # All required packages are installed
        check_dependencies()

    def test_check_dependencies_missing_package(self):
        # Mocking a missing package raises PreflightException
        with patch("builtins.__import__", side_effect=ImportError("No module named 'fake_pkg'")):
            with self.assertRaises(PreflightException):
                check_dependencies()

    def test_check_storage_permissions(self):
        # Should succeed in normal environment
        check_storage_permissions()

    def test_check_storage_permissions_failure(self):
        # Mocking an un-writable path raises PreflightException
        with patch.object(Path, "write_text", side_effect=PermissionError("Access denied")):
            with self.assertRaises(PreflightException):
                check_storage_permissions()

    def test_check_ytdlp_operational_success(self):
        # Live self test
        check_ytdlp_operational(skip_network=False)

    def test_check_ytdlp_operational_skip(self):
        # Skipping network flag
        check_ytdlp_operational(skip_network=True)

    def test_check_ytdlp_operational_failure(self):
        # Mocking yt-dlp failure raises PreflightException
        import yt_dlp
        with patch.object(yt_dlp.YoutubeDL, "extract_info", side_effect=RuntimeError("Bot wall")):
            with self.assertRaises(PreflightException):
                check_ytdlp_operational(skip_network=False)

    def test_check_ffmpeg_tool(self):
        # Should not raise exception
        check_ffmpeg_tool()

    def test_run_preflight_overall_success(self):
        res = run_preflight(skip_network=True)
        self.assertEqual(res, 0)


if __name__ == "__main__":
    unittest.main()
