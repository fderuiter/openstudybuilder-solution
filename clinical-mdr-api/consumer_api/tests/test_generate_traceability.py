"""Unit tests for consumer_api/requirements/generate_traceability.py

Covers only the functions changed in this PR:
  - extract_fs_titles_and_tests   (removed all_tests param + Test Status column injection)
  - collect_fs_traceability       (removed all_tests param)
  - get_warnings                  (removed tests param; now calls get_all_tests() internally)
  - get_all_tests                 (simplified: only scans consumer_api/tests/)
"""

import os
import re
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# The module uses absolute paths derived from __file__, so we import the
# functions directly rather than relying on module-level path constants.
from consumer_api.requirements.generate_traceability import (
    collect_fs_traceability,
    extract_fs_titles_and_tests,
    get_all_tests,
    get_warnings,
)


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _html_with_fs_and_test_table(fs_id: str, test_file: str, test_method: str) -> str:
    """Build minimal HTML representing one FS section with a 'Test coverage' table."""
    return (
        f"<h2>{fs_id} [URS-FOO]</h2>"
        "<h3>Test coverage</h3>"
        "<table>"
        "<tr><th>Test File</th><th>Test Function</th></tr>"
        f"<tr><td>{test_file}</td><td>{test_method}</td></tr>"
        "</table>"
    )


def _html_without_test_coverage(fs_id: str) -> str:
    return f"<h2>{fs_id} [URS-FOO]</h2><p>Some description.</p>"


def _html_non_fs_header() -> str:
    return "<h2>Other-Section</h2><h3>Test coverage</h3><table></table>"


# ──────────────────────────────────────────────────────────────────────────────
# extract_fs_titles_and_tests
# ──────────────────────────────────────────────────────────────────────────────
class TestExtractFsTitlesAndTests:
    """Tests for extract_fs_titles_and_tests(html_content)."""

    def test_returns_empty_list_for_empty_html(self):
        assert extract_fs_titles_and_tests("") == []

    def test_returns_empty_list_when_no_fs_headers(self):
        html = "<h2>Introduction</h2><p>Some text</p>"
        assert extract_fs_titles_and_tests(html) == []

    def test_returns_empty_list_for_non_fs_h2_with_test_coverage(self):
        html = _html_non_fs_header()
        assert extract_fs_titles_and_tests(html) == []

    def test_extracts_fs_title_test_file_and_method(self):
        html = _html_with_fs_and_test_table("FS-Foo-010", "tests/test_foo.py", "test_bar")
        result = extract_fs_titles_and_tests(html)

        assert len(result) == 1
        title, table_elem, tests_list = result[0]
        assert title == "FS-Foo-010 [URS-FOO]"
        assert len(tests_list) == 1
        assert tests_list[0]["file"] == "tests/test_foo.py"
        assert tests_list[0]["method"] == "test_bar"

    def test_extracts_multiple_test_rows(self):
        html = (
            "<h2>FS-Bar-020 [URS-BAR]</h2>"
            "<h3>Test coverage</h3>"
            "<table>"
            "<tr><th>Test File</th><th>Test Function</th></tr>"
            "<tr><td>tests/a.py</td><td>test_one</td></tr>"
            "<tr><td>tests/b.py</td><td>test_two</td></tr>"
            "</table>"
        )
        result = extract_fs_titles_and_tests(html)
        assert len(result) == 1
        _, _, tests_list = result[0]
        assert len(tests_list) == 2
        assert tests_list[0] == {"file": "tests/a.py", "method": "test_one"}
        assert tests_list[1] == {"file": "tests/b.py", "method": "test_two"}

    def test_skips_fs_section_without_test_coverage_header(self):
        html = _html_without_test_coverage("FS-Baz-030")
        result = extract_fs_titles_and_tests(html)
        assert result == []

    def test_does_not_add_test_status_column_to_header(self):
        """Regression: 'Test Status' column must NOT be injected (was removed in PR)."""
        html = _html_with_fs_and_test_table("FS-Qux-040", "tests/test_qux.py", "test_x")
        result = extract_fs_titles_and_tests(html)
        _, table_elem, _ = result[0]
        header_text = str(table_elem)
        assert "Test Status" not in header_text

    def test_does_not_add_status_td_to_rows(self):
        """Regression: status <td> must NOT be appended to rows (was removed in PR)."""
        html = _html_with_fs_and_test_table("FS-Qux-050", "tests/test_qux.py", "test_y")
        result = extract_fs_titles_and_tests(html)
        _, table_elem, tests_list = result[0]
        # The original code would inject "Automated" or "Missing" cells; ensure they're absent
        row_text = str(table_elem)
        assert "Automated" not in row_text
        assert "Missing" not in row_text

    def test_handles_multiple_fs_sections(self):
        html = (
            "<h2>FS-A-001 [URS-A]</h2>"
            "<h3>Test coverage</h3>"
            "<table>"
            "<tr><td>tests/a.py</td><td>test_a</td></tr>"
            "</table>"
            "<h2>FS-B-002 [URS-B]</h2>"
            "<h3>Test coverage</h3>"
            "<table>"
            "<tr><td>tests/b.py</td><td>test_b</td></tr>"
            "</table>"
        )
        result = extract_fs_titles_and_tests(html)
        titles = [r[0] for r in result]
        assert "FS-A-001 [URS-A]" in titles
        assert "FS-B-002 [URS-B]" in titles

    def test_ignores_h3_elements_that_are_not_test_coverage(self):
        html = (
            "<h2>FS-Ign-010 [URS-IGN]</h2>"
            "<h3>Overview</h3>"
            "<p>Some text</p>"
            "<h3>Test coverage</h3>"
            "<table>"
            "<tr><td>tests/ign.py</td><td>test_ign</td></tr>"
            "</table>"
        )
        result = extract_fs_titles_and_tests(html)
        assert len(result) == 1
        _, _, tests_list = result[0]
        assert tests_list[0]["file"] == "tests/ign.py"

    def test_stops_at_next_h2(self):
        """Test coverage table after the next h2 should NOT be attributed to the first FS."""
        html = (
            "<h2>FS-Stop-001 [URS-STOP]</h2>"
            "<p>Desc</p>"
            "<h2>FS-Stop-002 [URS-STOP2]</h2>"
            "<h3>Test coverage</h3>"
            "<table>"
            "<tr><td>tests/stop.py</td><td>test_stop</td></tr>"
            "</table>"
        )
        result = extract_fs_titles_and_tests(html)
        # Only the second FS section has a test coverage table
        assert len(result) == 1
        title, _, _ = result[0]
        assert "FS-Stop-002" in title

    def test_function_signature_accepts_only_html_content(self):
        """The function must accept a single positional argument (no all_tests param)."""
        import inspect
        sig = inspect.signature(extract_fs_titles_and_tests)
        params = list(sig.parameters.keys())
        assert params == ["html_content"]


# ──────────────────────────────────────────────────────────────────────────────
# get_all_tests
# ──────────────────────────────────────────────────────────────────────────────
class TestGetAllTests:
    """Tests for get_all_tests() – now only scans consumer_api/tests/."""

    def test_returns_list(self):
        result = get_all_tests()
        assert isinstance(result, list)

    def test_each_item_has_file_and_methods_keys(self):
        result = get_all_tests()
        for item in result:
            assert "file" in item
            assert "methods" in item

    def test_methods_are_list_of_strings(self):
        result = get_all_tests()
        for item in result:
            assert isinstance(item["methods"], list)

    def test_discovers_test_functions(self, tmp_path):
        """get_all_tests() should find test_* functions in .py files."""
        import consumer_api.requirements.generate_traceability as gt

        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        py_file = tests_dir / "test_sample.py"
        py_file.write_text(
            "def test_foo():\n    pass\ndef test_bar():\n    pass\ndef helper():\n    pass\n",
            encoding="utf-8",
        )

        with patch.object(gt, "BASE_DIR", tmp_path):
            result = get_all_tests()

        file_entries = [e for e in result if "test_sample.py" in e["file"]]
        assert len(file_entries) == 1
        assert "test_foo" in file_entries[0]["methods"]
        assert "test_bar" in file_entries[0]["methods"]
        assert "helper" not in file_entries[0]["methods"]

    def test_ignores_non_python_files(self, tmp_path):
        """Non-.py files should not appear in results."""
        import consumer_api.requirements.generate_traceability as gt

        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "data.json").write_text('{"key": "value"}', encoding="utf-8")
        (tests_dir / "test_sample.py").write_text("def test_x(): pass\n", encoding="utf-8")

        with patch.object(gt, "BASE_DIR", tmp_path):
            result = get_all_tests()

        for item in result:
            assert item["file"].endswith(".py")

    def test_file_paths_are_relative_to_base_dir(self, tmp_path):
        """File paths should be relative to BASE_DIR (consumer_api/)."""
        import consumer_api.requirements.generate_traceability as gt

        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_rel.py").write_text("def test_something(): pass\n", encoding="utf-8")

        with patch.object(gt, "BASE_DIR", tmp_path):
            result = get_all_tests()

        file_entries = [e for e in result if "test_rel.py" in e["file"]]
        assert len(file_entries) == 1
        # Path must be relative (no leading /)
        assert not file_entries[0]["file"].startswith("/")

    def test_does_not_scan_core_services_dir(self, tmp_path):
        """Regression: core services tests directory must NOT be scanned (was removed in PR)."""
        import consumer_api.requirements.generate_traceability as gt

        # Simulate consumer_api/ with tests/
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_consumer.py").write_text("def test_consumer(): pass\n", encoding="utf-8")

        # Simulate the old core services path (sibling clinical_mdr_api)
        core_tests_dir = tmp_path.parent / "clinical_mdr_api" / "tests"
        # This directory may or may not exist; the new code must not traverse it

        with patch.object(gt, "BASE_DIR", tmp_path):
            result = get_all_tests()

        # All discovered files must be under tmp_path/tests, not under clinical_mdr_api
        for item in result:
            assert "clinical_mdr_api" not in item["file"]

    def test_empty_tests_dir_returns_empty_list(self, tmp_path):
        import consumer_api.requirements.generate_traceability as gt

        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()

        with patch.object(gt, "BASE_DIR", tmp_path):
            result = get_all_tests()

        assert result == []

    def test_nested_test_files_discovered(self, tmp_path):
        """Test files in subdirectories of tests/ should also be found."""
        import consumer_api.requirements.generate_traceability as gt

        sub = tmp_path / "tests" / "v1"
        sub.mkdir(parents=True)
        (sub / "test_api.py").write_text("def test_endpoint(): pass\n", encoding="utf-8")

        with patch.object(gt, "BASE_DIR", tmp_path):
            result = get_all_tests()

        file_entries = [e for e in result if "test_api.py" in e["file"]]
        assert len(file_entries) == 1
        assert "test_endpoint" in file_entries[0]["methods"]


# ──────────────────────────────────────────────────────────────────────────────
# get_warnings
# ──────────────────────────────────────────────────────────────────────────────
class TestGetWarnings:
    """Tests for get_warnings(full_traceability, all_fs_ids=set()).

    The function now calls get_all_tests() internally, so we patch it via
    the module to avoid filesystem dependence.
    """

    def _call(self, full_traceability, all_fs_ids=None, mock_tests=None):
        import consumer_api.requirements.generate_traceability as gt

        if mock_tests is None:
            mock_tests = []
        if all_fs_ids is None:
            all_fs_ids = set()

        with patch.object(gt, "get_all_tests", return_value=mock_tests):
            return get_warnings(full_traceability, all_fs_ids)

    def test_returns_string(self):
        result = self._call([])
        assert isinstance(result, str)

    def test_no_warnings_returns_none_placeholder(self):
        """When everything is linked correctly, output should say '-- None --'."""
        traceability = [
            {
                "urs_id": "URS-FOO",
                "fs_list": [
                    {
                        "fs_id": "FS-Foo-010",
                        "tests_html": "<table></table>",
                        "tests_list": [],
                    }
                ],
            }
        ]
        result = self._call(traceability, all_fs_ids={"FS-Foo-010"})
        assert "-- None --" in result

    def test_warns_urs_without_linked_fs(self):
        traceability = [{"urs_id": "URS-BAR", "fs_list": []}]
        result = self._call(traceability)
        assert "URS-BAR" in result

    def test_warns_fs_without_linked_tests(self):
        traceability = [
            {
                "urs_id": "URS-BAZ",
                "fs_list": [
                    {
                        "fs_id": "FS-Baz-010",
                        "tests_html": "",   # No tests HTML
                        "tests_list": [],
                    }
                ],
            }
        ]
        result = self._call(traceability, all_fs_ids={"FS-Baz-010"})
        assert "FS-Baz-010" in result

    def test_warns_non_existent_tests(self):
        """A test listed in FS but absent from discovered tests should trigger a warning."""
        traceability = [
            {
                "urs_id": "URS-QUX",
                "fs_list": [
                    {
                        "fs_id": "FS-Qux-010",
                        "tests_html": "<table/>",
                        "tests_list": [
                            {"file": "tests/test_qux.py", "method": "test_missing_fn"}
                        ],
                    }
                ],
            }
        ]
        # Provide no matching test in mock_tests
        result = self._call(traceability, all_fs_ids={"FS-Qux-010"}, mock_tests=[])
        assert "test_missing_fn" in result

    def test_no_warning_when_test_exists(self):
        """A test listed in FS that IS in discovered tests must NOT trigger a warning."""
        traceability = [
            {
                "urs_id": "URS-QUX",
                "fs_list": [
                    {
                        "fs_id": "FS-Qux-010",
                        "tests_html": "<table/>",
                        "tests_list": [
                            {"file": "tests/test_qux.py", "method": "test_real_fn"}
                        ],
                    }
                ],
            }
        ]
        mock_tests = [{"file": "tests/test_qux.py", "methods": ["test_real_fn"]}]
        result = self._call(traceability, all_fs_ids={"FS-Qux-010"}, mock_tests=mock_tests)
        assert "test_real_fn" not in result

    def test_warns_fs_not_linked_to_any_urs(self):
        """An FS ID in all_fs_ids but not linked to any URS entry should produce a warning."""
        traceability = [
            {"urs_id": "URS-ONE", "fs_list": [{"fs_id": "FS-One-001", "tests_html": "", "tests_list": []}]}
        ]
        # FS-Orphan-999 exists but is not linked to any URS
        all_fs_ids = {"FS-One-001", "FS-Orphan-999"}
        result = self._call(traceability, all_fs_ids=all_fs_ids)
        assert "FS-Orphan-999" in result

    def test_function_signature_has_default_all_fs_ids(self):
        """all_fs_ids must have a default value (set()) per the PR change."""
        import inspect
        from consumer_api.requirements.generate_traceability import get_warnings

        sig = inspect.signature(get_warnings)
        params = sig.parameters
        assert "all_fs_ids" in params
        assert params["all_fs_ids"].default is not inspect.Parameter.empty

    def test_function_no_longer_has_tests_parameter(self):
        """The tests parameter must have been removed from the signature."""
        import inspect
        from consumer_api.requirements.generate_traceability import get_warnings

        sig = inspect.signature(get_warnings)
        assert "tests" not in sig.parameters

    def test_calls_get_all_tests_internally(self):
        """get_warnings must call get_all_tests() itself (not receive tests from caller)."""
        import consumer_api.requirements.generate_traceability as gt

        traceability = [{"urs_id": "URS-INTERNAL", "fs_list": []}]
        with patch.object(gt, "get_all_tests", return_value=[]) as mock_fn:
            get_warnings(traceability)
            mock_fn.assert_called_once()

    def test_empty_traceability_no_crash(self):
        result = self._call([])
        assert isinstance(result, str)

    def test_multiple_urs_without_fs_all_reported(self):
        traceability = [
            {"urs_id": "URS-ALPHA", "fs_list": []},
            {"urs_id": "URS-BETA", "fs_list": []},
        ]
        result = self._call(traceability)
        assert "URS-ALPHA" in result
        assert "URS-BETA" in result


# ──────────────────────────────────────────────────────────────────────────────
# collect_fs_traceability
# ──────────────────────────────────────────────────────────────────────────────
class TestCollectFsTraceability:
    """Tests for collect_fs_traceability(fs_files, full_traceability)."""

    def _write_fs_file(self, tmp_path, content: str) -> Path:
        f = tmp_path / "fs.md"
        f.write_text(content, encoding="utf-8")
        return f

    def test_returns_set_of_fs_ids(self, tmp_path):
        md = (
            "## FS-Col-010 [URS-COL]\n"
            "\nSome description.\n"
            "\n### Test coverage\n\n"
            "| Test File | Test Function |\n"
            "| --- | --- |\n"
            "| tests/test_col.py | test_col |\n"
        )
        fs_file = self._write_fs_file(tmp_path, md)
        traceability = [{"urs_id": "URS-COL", "fs_list": []}]
        result = collect_fs_traceability([fs_file], traceability)
        assert isinstance(result, set)
        assert "FS-Col-010" in result

    def test_links_fs_to_matching_urs_entry(self, tmp_path):
        md = (
            "## FS-Link-010 [URS-LINK]\n"
            "\nDescription.\n"
            "\n### Test coverage\n\n"
            "| Test File | Test Function |\n"
            "| --- | --- |\n"
            "| tests/test_link.py | test_link |\n"
        )
        fs_file = self._write_fs_file(tmp_path, md)
        traceability = [{"urs_id": "URS-LINK", "fs_list": []}]
        collect_fs_traceability([fs_file], traceability)
        assert len(traceability[0]["fs_list"]) == 1
        assert traceability[0]["fs_list"][0]["fs_id"] == "FS-Link-010"

    def test_function_signature_has_no_all_tests_param(self):
        """collect_fs_traceability must not accept an all_tests parameter."""
        import inspect
        sig = inspect.signature(collect_fs_traceability)
        assert "all_tests" not in sig.parameters

    def test_accepts_empty_file_list(self):
        result = collect_fs_traceability([], [])
        assert result == set()

    def test_empty_full_traceability_no_crash(self, tmp_path):
        md = "## FS-NoURS-010 [URS-MISSING]\n\nDesc.\n"
        fs_file = self._write_fs_file(tmp_path, md)
        result = collect_fs_traceability([fs_file], [])
        assert isinstance(result, set)

    def test_warns_on_duplicate_fs_id(self, tmp_path, caplog):
        """Duplicate FS IDs in multiple files should trigger a warning log."""
        import logging

        md = (
            "## FS-Dup-010 [URS-DUP]\n\nDesc.\n"
            "\n### Test coverage\n\n"
            "| Test File | Test Function |\n| --- | --- |\n| f.py | t |\n"
        )
        f1 = tmp_path / "fs1.md"
        f2 = tmp_path / "fs2.md"
        f1.write_text(md, encoding="utf-8")
        f2.write_text(md, encoding="utf-8")
        traceability = [{"urs_id": "URS-DUP", "fs_list": []}]
        with caplog.at_level(logging.WARNING):
            collect_fs_traceability([f1, f2], traceability)
        assert any("Duplicate" in r.message for r in caplog.records)

    def test_does_not_link_to_wrong_urs(self, tmp_path):
        md = "## FS-Wrong-010 [URS-X]\n\nDesc.\n"
        fs_file = self._write_fs_file(tmp_path, md)
        traceability = [{"urs_id": "URS-Y", "fs_list": []}]
        collect_fs_traceability([fs_file], traceability)
        assert traceability[0]["fs_list"] == []
