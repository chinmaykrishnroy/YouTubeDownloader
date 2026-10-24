import shutil
import subprocess
import unittest
from pathlib import Path


class TestFrontend(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node.js required for frontend runtime checks")
    def test_player_lifecycle_and_live_connection(self):
        subprocess.run(
            [shutil.which("node"), "tests/test_frontend.js"],
            cwd=Path(__file__).resolve().parent.parent, check=True, timeout=15,
        )
