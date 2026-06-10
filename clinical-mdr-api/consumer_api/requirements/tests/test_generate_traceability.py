"""Unit tests for generate_traceability.py.

Tests focus on functions changed in the PR:
- extract_fs_titles_and_tests(): removed all_tests param; no longer injects "Test Status" column
- collect_fs_traceability(): removed all_tests param
- get_warnings(): removed tests param; now calls get_all_tests() internally; all_fs_ids has default
- get_all_tests(): simplified to only scan BASE_DIR/"tests" (no longer scans core_services_dir)
"""

import os
import textwrap
from pathlib import Path
from unittest.mock import MagicMock, call, mock_open, patch

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FS_MD_WITH_TESTS = textwrap.dedent(
    """\
    # Some Feature

    ## FS-Feature-Get-010 [`URS-SomeURS`]

    Feature description.

    ### Test coverage

    | Test File                    | Test Function   |
    | ---------------------------- | --------------- |
    | tests/v1/test_api.py         | test_get_item   |
    | tests/v1/test_api.py         | test_post_item  |
    """
)

FS_MD_WITHOUT_TESTS = textwrap.dedent(
    """\
    # Another Feature

    ## FS-Feature-NoTest-010 [`URS-SomeURS`]

    Feature without tests.
    """
)

FS_MD_MULTIPLE_FS = textwrap.dedent(
    """\
    # Multi Feature Doc

    ## FS-Feature-Alpha-010 [`URS-AlphaURS`]

    Alpha feature.

    ### Test coverage

    | Test File              | Test Function  |
    | ---------------------- | -------------- |
    | tests/v1/test_a.py     | test_alpha     |

    ## FS-Feature-Beta-010 [`URS-BetaURS`]

    Beta feature.

    ### Test coverage

    | Test File              | Test Function  |
    | ---------------------- | -------------- |
    | tests/v1/test_b.py     | test_beta      |
    """
)

NON_FS_MD = textwrap.dedent(
    """\
    # Overview

    ## SomeSection-010 [`URS-SomeURS`]

    A section that does not start with FS-.

    ### Test coverage

    | Test File          | Test Function |
    | ------------------ | ------------- |
    | tests/v1/other.py  | test_other    |
    """
)


def _render_md(md_text: str) -> str:
    """Convert markdown text to HTML using the same settings as the module."""
    import markdown

    return markdown.markdown(md_text, extensions=["fenced_code", "tables"])


# ---------------------------------------------------------------------------
# Import the module under test
# ---------------------------------------------------------------------------

import sys

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[3]),  # clinical-mdr-api root
)

from consumer_api.requirements.generate_traceability import (
    collect_fs_traceability,
    extract_fs_titles_and_tests,
    get_all_tests,
    get_warnings,
)


# ===========================================================================
# Tests for extract_fs_titles_and_tests()
# ===========================================================================


class TestExtractFsTitlesAndTests:
    """Tests for extract_fs_titles_and_tests(html_content)."""

    def test_returns_list(self):
        html = _render_md(FS_MD_WITH_TESTS)
        result = extract_fs_titles_and_tests(html)
        assert isinstance(result, list)

    def test_extracts_fs_title(self):
        html = _render_md(FS_MD_WITH_TESTS)
        result = extract_fs_titles_and_tests(html)
        assert len(result) == 1
        title, _table, _tests = result[0]
        assert title.startswith("FS-Feature-Get-010")

    def test_extracts_test_entries(self):
        html = _render_md(FS_MD_WITH_TESTS)
        result = extract_fs_titles_and_tests(html)
        _, _table, tests = result[0]
        assert len(tests) == 2
        assert {"file": "tests/v1/test_api.py", "method": "test_get_item"} in tests
        assert {"file": "tests/v1/test_api.py", "method": "test_post_item"} in tests

    def test_does_not_add_test_status_column(self):
        """After the PR, extract_fs_titles_and_tests must NOT inject a 'Test Status' column."""
        html = _render_md(FS_MD_WITH_TESTS)
        result = extract_fs_titles_and_tests(html)
        _, table_element, _ = result[0]
        # Verify header row has no 'Test Status' <th>
        header_row = table_element.find("tr")
        ths = [th.get_text(strip=True) for th in header_row.find_all("th")]
        assert "Test Status" not in ths

    def test_does_not_add_test_status_data_cells(self):
        """After the PR, no data cells with 'Automated' or 'Missing' should be injected."""
        html = _render_md(FS_MD_WITH_TESTS)
        result = extract_fs_titles_and_tests(html)
        _, table_element, _ = result[0]
        all_td_texts = [td.get_text(strip=True) for td in table_element.find_all("td")]
        assert "Automated" not in all_td_texts
        assert "Missing" not in all_td_texts

    def test_ignores_non_fs_headers(self):
        html = _render_md(NON_FS_MD)
        result = extract_fs_titles_and_tests(html)
        assert result == []

    def test_fs_without_test_coverage_section(self):
        html = _render_md(FS_MD_WITHOUT_TESTS)
        result = extract_fs_titles_and_tests(html)
        # No "Test coverage" h3 exists, so nothing is appended
        assert result == []

    def test_multiple_fs_entries(self):
        html = _render_md(FS_MD_MULTIPLE_FS)
        result = extract_fs_titles_and_tests(html)
        assert len(result) == 2
        titles = [r[0] for r in result]
        assert any("FS-Feature-Alpha-010" in t for t in titles)
        assert any("FS-Feature-Beta-010" in t for t in titles)

    def test_multiple_fs_each_has_correct_tests(self):
        html = _render_md(FS_MD_MULTIPLE_FS)
        result = extract_fs_titles_and_tests(html)
        tests_by_title = {r[0].split()[0]: r[2] for r in result}
        assert tests_by_title["FS-Feature-Alpha-010"] == [
            {"file": "tests/v1/test_a.py", "method": "test_alpha"}
        ]
        assert tests_by_title["FS-Feature-Beta-010"] == [
            {"file": "tests/v1/test_b.py", "method": "test_beta"}
        ]

    def test_empty_html(self):
        result = extract_fs_titles_and_tests("")
        assert result == []

    def test_accepts_only_html_content_string(self):
        """Signature changed: no longer accepts all_tests parameter."""
        import inspect

        sig = inspect.signature(extract_fs_titles_and_tests)
        params = list(sig.parameters.keys())
        assert params == ["html_content"], (
            "extract_fs_titles_and_tests should only have html_content parameter"
        )


# ===========================================================================
# Tests for collect_fs_traceability()
# ===========================================================================


class TestCollectFsTraceability:
    """Tests for collect_fs_traceability(fs_files, full_traceability)."""

    def test_signature_no_all_tests_param(self):
        """After the PR, the function must NOT have an all_tests parameter."""
        import inspect

        sig = inspect.signature(collect_fs_traceability)
        params = list(sig.parameters.keys())
        assert "all_tests" not in params

    def test_returns_set(self, tmp_path):
        fs_file = tmp_path / "fs-test.md"
        fs_file.write_text(FS_MD_WITH_TESTS)
        full_traceability = [
            {"urs_id": "URS-SomeURS", "type": "URS", "text": "", "fs_list": []}
        ]
        result = collect_fs_traceability([fs_file], full_traceability)
        assert isinstance(result, set)

    def test_adds_fs_id_to_set(self, tmp_path):
        fs_file = tmp_path / "fs-test.md"
        fs_file.write_text(FS_MD_WITH_TESTS)
        full_traceability = [
            {"urs_id": "URS-SomeURS", "type": "URS", "text": "", "fs_list": []}
        ]
        result = collect_fs_traceability([fs_file], full_traceability)
        assert "FS-Feature-Get-010" in result

    def test_links_fs_to_matching_urs(self, tmp_path):
        fs_file = tmp_path / "fs-test.md"
        fs_file.write_text(FS_MD_WITH_TESTS)
        full_traceability = [
            {"urs_id": "URS-SomeURS", "type": "URS", "text": "", "fs_list": []}
        ]
        collect_fs_traceability([fs_file], full_traceability)
        fs_list = full_traceability[0]["fs_list"]
        assert len(fs_list) == 1
        assert fs_list[0]["fs_id"] == "FS-Feature-Get-010"

    def test_does_not_link_fs_to_mismatched_urs(self, tmp_path):
        fs_file = tmp_path / "fs-test.md"
        fs_file.write_text(FS_MD_WITH_TESTS)
        full_traceability = [
            {"urs_id": "URS-DifferentURS", "type": "URS", "text": "", "fs_list": []}
        ]
        collect_fs_traceability([fs_file], full_traceability)
        assert full_traceability[0]["fs_list"] == []

    def test_multiple_fs_files(self, tmp_path):
        file1 = tmp_path / "fs-alpha.md"
        file1.write_text(FS_MD_MULTIPLE_FS)
        full_traceability = [
            {
                "urs_id": "URS-AlphaURS",
                "type": "URS",
                "text": "",
                "fs_list": [],
            },
            {
                "urs_id": "URS-BetaURS",
                "type": "URS",
                "text": "",
                "fs_list": [],
            },
        ]
        result = collect_fs_traceability([file1], full_traceability)
        assert "FS-Feature-Alpha-010" in result
        assert "FS-Feature-Beta-010" in result

    def test_empty_file_list(self):
        full_traceability = []
        result = collect_fs_traceability([], full_traceability)
        assert result == set()

    def test_duplicate_fs_id_logs_warning(self, tmp_path, caplog):
        import logging

        fs_file1 = tmp_path / "fs-dup1.md"
        fs_file1.write_text(FS_MD_WITH_TESTS)
        fs_file2 = tmp_path / "fs-dup2.md"
        fs_file2.write_text(FS_MD_WITH_TESTS)
        full_traceability = [
            {"urs_id": "URS-SomeURS", "type": "URS", "text": "", "fs_list": []}
        ]
        with caplog.at_level(logging.WARNING):
            collect_fs_traceability([fs_file1, fs_file2], full_traceability)
        assert any("Duplicate" in msg for msg in caplog.messages)

    def test_fs_entry_contains_tests_list(self, tmp_path):
        fs_file = tmp_path / "fs-test.md"
        fs_file.write_text(FS_MD_WITH_TESTS)
        full_traceability = [
            {"urs_id": "URS-SomeURS", "type": "URS", "text": "", "fs_list": []}
        ]
        collect_fs_traceability([fs_file], full_traceability)
        fs_entry = full_traceability[0]["fs_list"][0]
        assert "tests_list" in fs_entry
        assert len(fs_entry["tests_list"]) == 2


# ===========================================================================
# Tests for get_warnings()
# ===========================================================================


class TestGetWarnings:
    """Tests for get_warnings(full_traceability, all_fs_ids=set())."""

    def test_signature_no_tests_param(self):
        """After the PR, get_warnings must NOT have a 'tests' parameter."""
        import inspect

        sig = inspect.signature(get_warnings)
        params = list(sig.parameters.keys())
        assert "tests" not in params

    def test_all_fs_ids_has_default_empty_set(self):
        """After the PR, all_fs_ids should have a default value of set()."""
        import inspect

        sig = inspect.signature(get_warnings)
        param = sig.parameters.get("all_fs_ids")
        assert param is not None
        assert param.default == set()

    def test_calls_get_all_tests_internally(self):
        """After the PR, get_warnings should call get_all_tests() by itself."""
        with patch(
            "consumer_api.requirements.generate_traceability.get_all_tests",
            return_value=[],
        ) as mock_get_tests:
            get_warnings([], set())
        mock_get_tests.assert_called_once()

    def test_returns_none_warning_when_all_ok(self, tmp_path):
        """When everything is linked correctly, should return no-warnings HTML."""
        with patch(
            "consumer_api.requirements.generate_traceability.get_all_tests",
            return_value=[
                {"file": "tests/v1/test_api.py", "methods": ["test_get_item"]}
            ],
        ):
            full_traceability = [
                {
                    "urs_id": "URS-SomeURS",
                    "type": "URS",
                    "text": "",
                    "fs_list": [
                        {
                            "fs_id": "FS-Feature-Get-010",
                            "tests_html": "<table>...</table>",
                            "tests_list": [
                                {
                                    "file": "tests/v1/test_api.py",
                                    "method": "test_get_item",
                                }
                            ],
                        }
                    ],
                }
            ]
            result = get_warnings(
                full_traceability, {"FS-Feature-Get-010"}
            )
        assert "-- None --" in result

    def test_warns_urs_without_fs(self):
        with patch(
            "consumer_api.requirements.generate_traceability.get_all_tests",
            return_value=[],
        ):
            full_traceability = [
                {
                    "urs_id": "URS-Orphan",
                    "type": "URS",
                    "text": "",
                    "fs_list": [],
                }
            ]
            result = get_warnings(full_traceability, set())
        assert "URS-Orphan" in result
        assert "URSs without linked FSs" in result

    def test_warns_fs_without_tests(self):
        with patch(
            "consumer_api.requirements.generate_traceability.get_all_tests",
            return_value=[],
        ):
            full_traceability = [
                {
                    "urs_id": "URS-SomeURS",
                    "type": "URS",
                    "text": "",
                    "fs_list": [
                        {
                            "fs_id": "FS-NoTest-010",
                            "tests_html": "",
                            "tests_list": [],
                        }
                    ],
                }
            ]
            result = get_warnings(
                full_traceability, {"FS-NoTest-010"}
            )
        assert "FS-NoTest-010" in result
        assert "FSs without linked tests" in result

    def test_warns_fs_not_linked_to_urs(self):
        with patch(
            "consumer_api.requirements.generate_traceability.get_all_tests",
            return_value=[],
        ):
            # FS-Unlinked-010 is in all_fs_ids but not in any full_traceability fs_list
            full_traceability = [
                {
                    "urs_id": "URS-SomeURS",
                    "type": "URS",
                    "text": "",
                    "fs_list": [],
                }
            ]
            result = get_warnings(
                full_traceability, {"FS-Unlinked-010"}
            )
        assert "FS-Unlinked-010" in result
        assert "FSs without linked URS" in result

    def test_warns_non_existent_test(self):
        with patch(
            "consumer_api.requirements.generate_traceability.get_all_tests",
            return_value=[],  # No tests exist on disk
        ):
            full_traceability = [
                {
                    "urs_id": "URS-SomeURS",
                    "type": "URS",
                    "text": "",
                    "fs_list": [
                        {
                            "fs_id": "FS-Feature-010",
                            "tests_html": "<table/>",
                            "tests_list": [
                                {
                                    "file": "tests/v1/test_api.py",
                                    "method": "test_missing_method",
                                }
                            ],
                        }
                    ],
                }
            ]
            result = get_warnings(
                full_traceability, {"FS-Feature-010"}
            )
        assert "test_missing_method" in result
        assert "Non-existent tests" in result

    def test_no_warnings_html_when_all_good(self):
        with patch(
            "consumer_api.requirements.generate_traceability.get_all_tests",
            return_value=[
                {"file": "tests/v1/test_api.py", "methods": ["test_get_item"]}
            ],
        ):
            full_traceability = [
                {
                    "urs_id": "URS-SomeURS",
                    "type": "URS",
                    "text": "",
                    "fs_list": [
                        {
                            "fs_id": "FS-Feature-010",
                            "tests_html": "<table/>",
                            "tests_list": [
                                {
                                    "file": "tests/v1/test_api.py",
                                    "method": "test_get_item",
                                }
                            ],
                        }
                    ],
                }
            ]
            result = get_warnings(
                full_traceability, {"FS-Feature-010"}
            )
        assert "-- None --" in result

    def test_callable_with_only_full_traceability(self):
        """all_fs_ids defaults to set(), so get_warnings can be called with one arg."""
        with patch(
            "consumer_api.requirements.generate_traceability.get_all_tests",
            return_value=[],
        ):
            # Should not raise
            result = get_warnings([])
        assert isinstance(result, str)


# ===========================================================================
# Tests for get_all_tests()
# ===========================================================================


class TestGetAllTests:
    """Tests for get_all_tests() after PR simplification."""

    def test_returns_list(self, tmp_path):
        with patch(
            "consumer_api.requirements.generate_traceability.BASE_DIR", tmp_path
        ):
            tests_dir = tmp_path / "tests"
            tests_dir.mkdir()
            result = get_all_tests()
        assert isinstance(result, list)

    def test_finds_test_methods_in_py_file(self, tmp_path):
        with patch(
            "consumer_api.requirements.generate_traceability.BASE_DIR", tmp_path
        ):
            tests_dir = tmp_path / "tests"
            tests_dir.mkdir()
            test_file = tests_dir / "test_sample.py"
            test_file.write_text(
                "def test_foo():\n    pass\n\ndef test_bar():\n    pass\n"
            )
            result = get_all_tests()
        assert len(result) == 1
        entry = result[0]
        assert "test_foo" in entry["methods"]
        assert "test_bar" in entry["methods"]

    def test_ignores_non_py_files(self, tmp_path):
        with patch(
            "consumer_api.requirements.generate_traceability.BASE_DIR", tmp_path
        ):
            tests_dir = tmp_path / "tests"
            tests_dir.mkdir()
            (tests_dir / "not_a_test.txt").write_text("def test_ignored(): pass")
            result = get_all_tests()
        assert result == []

    def test_file_path_relative_to_base_dir(self, tmp_path):
        with patch(
            "consumer_api.requirements.generate_traceability.BASE_DIR", tmp_path
        ):
            tests_dir = tmp_path / "tests"
            tests_dir.mkdir()
            test_file = tests_dir / "test_sample.py"
            test_file.write_text("def test_something(): pass")
            result = get_all_tests()
        assert len(result) == 1
        # Path must be relative to BASE_DIR (tmp_path), not absolute
        assert not os.path.isabs(result[0]["file"])
        assert result[0]["file"].startswith("tests")

    def test_does_not_scan_parent_core_services_dir(self, tmp_path):
        """After the PR, get_all_tests should NOT walk clinical_mdr_api/tests."""
        with patch(
            "consumer_api.requirements.generate_traceability.BASE_DIR", tmp_path
        ):
            # Create a sibling directory that the old code used to scan
            core_dir = tmp_path.parent / "clinical_mdr_api"
            core_tests = core_dir / "tests"
            core_tests.mkdir(parents=True, exist_ok=True)
            (core_tests / "test_core.py").write_text("def test_core_method(): pass")

            # consumer_api tests dir - empty
            tests_dir = tmp_path / "tests"
            tests_dir.mkdir()

            result = get_all_tests()

        # Should find nothing since consumer_api tests dir is empty
        assert result == []

    def test_scans_subdirectories_recursively(self, tmp_path):
        with patch(
            "consumer_api.requirements.generate_traceability.BASE_DIR", tmp_path
        ):
            tests_dir = tmp_path / "tests"
            sub_dir = tests_dir / "v1"
            sub_dir.mkdir(parents=True)
            test_file = sub_dir / "test_subdir.py"
            test_file.write_text("def test_in_subdir(): pass")
            result = get_all_tests()
        assert len(result) == 1
        assert "test_in_subdir" in result[0]["methods"]
        assert "v1" in result[0]["file"]

    def test_empty_tests_directory(self, tmp_path):
        with patch(
            "consumer_api.requirements.generate_traceability.BASE_DIR", tmp_path
        ):
            tests_dir = tmp_path / "tests"
            tests_dir.mkdir()
            result = get_all_tests()
        assert result == []

    def test_py_file_with_no_test_methods(self, tmp_path):
        with patch(
            "consumer_api.requirements.generate_traceability.BASE_DIR", tmp_path
        ):
            tests_dir = tmp_path / "tests"
            tests_dir.mkdir()
            test_file = tests_dir / "helpers.py"
            test_file.write_text("def helper_func(): pass\ndef another(): pass\n")
            result = get_all_tests()
        assert len(result) == 1
        assert result[0]["methods"] == []

    def test_result_dict_has_file_and_methods_keys(self, tmp_path):
        with patch(
            "consumer_api.requirements.generate_traceability.BASE_DIR", tmp_path
        ):
            tests_dir = tmp_path / "tests"
            tests_dir.mkdir()
            (tests_dir / "test_something.py").write_text("def test_x(): pass")
            result = get_all_tests()
        assert "file" in result[0]
        assert "methods" in result[0]
