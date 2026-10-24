#!/usr/bin/env python3
"""Comprehensive test runner for YouTube Downloader.

Executes:
1. Unit tests for helpers & format options
2. Storage, auto-clean, & quota enforcement tests
3. REST and WebSocket API endpoint tests
4. Real End-to-End NCS Fade audio download test
"""
import sys
import unittest
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))


def run_all_tests():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Discover and add test modules
    tests_dir = BASE_DIR / "tests"
    discovered = loader.discover(start_dir=str(tests_dir), pattern="test_*.py")
    suite.addTests(discovered)

    print("=" * 70)
    print("      YOUTUBE DOWNLOADER - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print(f"Discovered {suite.countTestCases()} test cases across test modules.\n")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print(f" [PASS] ALL {result.testsRun} TESTS COMPLETED SUCCESSFULLY! ")
        print("=" * 70)
        return 0
    else:
        print(f" [FAIL] {len(result.failures)} FAILURES, {len(result.errors)} ERRORS DETECTED.")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
