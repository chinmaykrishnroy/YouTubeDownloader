import os
import sys
import unittest
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from main import (
    sanitize_filename,
    format_duration,
    format_view_count,
    get_ydl_format,
    check_ffmpeg,
    _get_cookies_opts,
    _get_base_ydl_opts,
)


class TestHelpers(unittest.TestCase):
    """Test suite for utility and helper functions in main.py."""

    def test_sanitize_filename_basic(self):
        self.assertEqual(sanitize_filename("valid_filename"), "valid_filename")
        self.assertEqual(sanitize_filename("Clean Title 2026"), "Clean Title 2026")

    def test_sanitize_filename_illegal_chars(self):
        # Disallowed: \ / * ? : " < > |
        dirty = 'Alan Walker / Fade: "Remix" <Official> | 2026? *NCS*'
        clean = sanitize_filename(dirty)
        for char in '\\/*?:"<>|':
            self.assertNotIn(char, clean)
        self.assertIn("Alan Walker", clean)
        self.assertIn("Fade", clean)

    def test_sanitize_filename_edge_cases(self):
        # Empty or only disallowed characters
        self.assertEqual(sanitize_filename("   "), "download")
        self.assertEqual(sanitize_filename("..."), "download")
        self.assertEqual(sanitize_filename(':::???***'), "download")

    def test_format_duration_none(self):
        self.assertEqual(format_duration(None), "")

    def test_format_duration_seconds(self):
        self.assertEqual(format_duration(0), "0:00")
        self.assertEqual(format_duration(9), "0:09")
        self.assertEqual(format_duration(45), "0:45")

    def test_format_duration_minutes(self):
        self.assertEqual(format_duration(60), "1:00")
        self.assertEqual(format_duration(264), "4:24")  # NCS Fade duration
        self.assertEqual(format_duration(600), "10:00")

    def test_format_duration_hours(self):
        self.assertEqual(format_duration(3600), "1:00:00")
        self.assertEqual(format_duration(3665), "1:01:05")
        self.assertEqual(format_duration(7325), "2:02:05")

    def test_format_view_count_none(self):
        self.assertEqual(format_view_count(None), "N/A views")

    def test_format_view_count_under_1k(self):
        self.assertEqual(format_view_count(0), "0 views")
        self.assertEqual(format_view_count(500), "500 views")
        self.assertEqual(format_view_count(999), "999 views")

    def test_format_view_count_thousands(self):
        self.assertEqual(format_view_count(1000), "1.0K views")
        self.assertEqual(format_view_count(1500), "1.5K views")
        self.assertEqual(format_view_count(99999), "100.0K views")

    def test_format_view_count_millions(self):
        self.assertEqual(format_view_count(1_000_000), "1.0M views")
        self.assertEqual(format_view_count(2_450_000), "2.5M views")
        self.assertEqual(format_view_count(450_000_000), "450.0M views")

    def test_get_ydl_format_audio_with_ffmpeg(self):
        opts_320 = get_ydl_format("audio", "320kbps", has_ffmpeg=True)
        self.assertEqual(opts_320["format"], "bestaudio/best")
        self.assertTrue(any(pp.get("preferredquality") == "320" for pp in opts_320.get("postprocessors", [])))

        opts_192 = get_ydl_format("audio", "192kbps", has_ffmpeg=True)
        self.assertTrue(any(pp.get("preferredquality") == "192" for pp in opts_192.get("postprocessors", [])))

    def test_get_ydl_format_audio_without_ffmpeg(self):
        opts = get_ydl_format("audio", "320kbps", has_ffmpeg=False)
        self.assertEqual(opts["format"], "bestaudio/best")
        self.assertNotIn("postprocessors", opts)

    def test_get_ydl_format_video_resolutions(self):
        opts_1080 = get_ydl_format("video", "1080p", has_ffmpeg=True)
        self.assertIn("1080", opts_1080["format"])

        opts_720 = get_ydl_format("video", "720p", has_ffmpeg=True)
        self.assertIn("720", opts_720["format"])

        opts_no_ff = get_ydl_format("video", "720p", has_ffmpeg=False)
        self.assertEqual(opts_no_ff["format"], "best[height<=720]/best")

    def test_check_ffmpeg(self):
        # Should return a boolean without throwing
        res = check_ffmpeg()
        self.assertIsInstance(res, bool)

    def test_get_base_ydl_opts(self):
        base_opts = _get_base_ydl_opts()
        self.assertTrue(base_opts["quiet"])
        self.assertTrue(base_opts["no_warnings"])
        self.assertIn("User-Agent", base_opts["http_headers"])


if __name__ == "__main__":
    unittest.main()
