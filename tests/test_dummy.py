"""Tiny smoke tests used to validate the test harness and CI.

This file contains a simple passing test to ensure the test runner is working.
"""

import unittest

class TestDummy(unittest.TestCase):
    def test_true(self):
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
