#!/usr/bin/env python3
import unittest
import os
import sys
import datetime
from unittest.mock import patch, MagicMock

# Add current directory to path so we can import dependency_audit
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dependency_audit

class TestDependencyAudit(unittest.TestCase):

    @patch("builtins.open")
    @patch("os.path.exists")
    @patch("subprocess.check_output")
    @patch("subprocess.run")
    @patch("os.remove")
    def test_valid_exemptions_pass(self, mock_remove, mock_run, mock_check_output, mock_exists, mock_open):
        # We mock exemptions file to exist
        mock_exists.return_value = True

        # Mock reading valid JSON
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = """
        [
            {
                "vulnerability_id": "CVE-2026-1111",
                "justification": "Safe because of X",
                "expiration_date": "2029-12-31"
            },
            {
                "vulnerability_id": "GHSA-abcd-1234",
                "justification": "Safe because of Y",
                "expiration_date": "2029-01-01"
            }
        ]
        """
        mock_open.return_value = mock_file

        mock_check_output.return_value = "fastapi==0.131.0\n"

        mock_res = MagicMock()
        mock_res.returncode = 0
        mock_run.return_value = mock_res

        # We call main and expect SystemExit with 0 (successful pipeline pass)
        with self.assertRaises(SystemExit) as cm:
            dependency_audit.main()
        self.assertEqual(cm.exception.code, 0)

        # Verify pip-audit was called with correct arguments
        called_args = mock_run.call_args[0][0]
        self.assertEqual(called_args[0], "pip-audit")
        self.assertEqual(called_args[1], "-r")
        self.assertTrue(called_args[2].endswith(".txt"))
        self.assertEqual(called_args[3:], ["--ignore-vuln", "CVE-2026-1111", "--ignore-vuln", "GHSA-abcd-1234"])

    @patch("builtins.open")
    @patch("os.path.exists")
    def test_expired_exemption_fails(self, mock_exists, mock_open):
        mock_exists.return_value = True

        # Exemption with past expiration date ("2020-01-01")
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = """
        [
            {
                "vulnerability_id": "CVE-2026-1111",
                "justification": "Expired",
                "expiration_date": "2020-01-01"
            }
        ]
        """
        mock_open.return_value = mock_file

        # We call main and expect SystemExit with 1
        with self.assertRaises(SystemExit) as cm:
            dependency_audit.main()
        self.assertEqual(cm.exception.code, 1)

    @patch("builtins.open")
    @patch("os.path.exists")
    def test_missing_mandatory_field_fails(self, mock_exists, mock_open):
        mock_exists.return_value = True

        # Missing justification
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = """
        [
            {
                "vulnerability_id": "CVE-2026-1111",
                "expiration_date": "2029-12-31"
            }
        ]
        """
        mock_open.return_value = mock_file

        # We call main and expect SystemExit with 1
        with self.assertRaises(SystemExit) as cm:
            dependency_audit.main()
        self.assertEqual(cm.exception.code, 1)

    @patch("builtins.open")
    @patch("os.path.exists")
    def test_invalid_date_format_fails(self, mock_exists, mock_open):
        mock_exists.return_value = True

        # Invalid date format
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = """
        [
            {
                "vulnerability_id": "CVE-2026-1111",
                "justification": "Invalid date",
                "expiration_date": "31-12-2029"
            }
        ]
        """
        mock_open.return_value = mock_file

        # We call main and expect SystemExit with 1
        with self.assertRaises(SystemExit) as cm:
            dependency_audit.main()
        self.assertEqual(cm.exception.code, 1)

if __name__ == "__main__":
    unittest.main()
