#!/usr/bin/env python3
import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Add current directory to path so we can import dependency_audit
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dependency_audit

class TestDependencyAudit(unittest.TestCase):
    @patch("dependency_audit.tomllib.load")
    @patch("builtins.open")
    @patch("os.path.exists")
    def test_extract_ignore_vulns(self, mock_exists, mock_open, mock_toml_load):
        # We want os.path.exists to return True for Pipfile, but False for other things like cleanup checks if mocked
        def exists_side_effect(path):
            if "Pipfile" in path:
                return True
            return False
        mock_exists.side_effect = exists_side_effect

        mock_toml_load.return_value = {
            "scripts": {
                "audit": "python -m pip_audit --ignore-vuln CVE-2026-4539 --ignore-vuln=GHSA-jj8c-mmj3-mmgv --ignore-vuln CVE-2025-71176"
            }
        }

        # Mock pipenv and pip-audit execution to prevent actual shell calls
        with patch("subprocess.check_output") as mock_check_output, \
             patch("subprocess.run") as mock_run, \
             patch("os.remove") as mock_remove:
            
            # Setup subprocess mock
            mock_check_output.return_value = "fastapi==0.131.0\n"
            
            # Configure mock_run return value to have returncode = 0
            mock_res = MagicMock()
            mock_res.returncode = 0
            mock_run.return_value = mock_res
            
            # We call main and expect SystemExit with 0
            with self.assertRaises(SystemExit) as cm:
                dependency_audit.main()
            self.assertEqual(cm.exception.code, 0)
            
            # Verify the pipenv requirements command was called in the correct folder
            mock_check_output.assert_called_with(["pipenv", "requirements"], cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")), text=True)
            
            # Verify pip-audit was called with correct arguments
            # We don't know the exact random filename, so we check using mock_run's actual arguments
            called_args = mock_run.call_args[0][0]
            self.assertEqual(called_args[0], "pip-audit")
            self.assertEqual(called_args[1], "-r")
            self.assertTrue(called_args[2].endswith(".txt"))
            self.assertEqual(called_args[3:], ["--ignore-vuln", "CVE-2026-4539", "--ignore-vuln", "GHSA-jj8c-mmj3-mmgv", "--ignore-vuln", "CVE-2025-71176"])

if __name__ == "__main__":
    unittest.main()
