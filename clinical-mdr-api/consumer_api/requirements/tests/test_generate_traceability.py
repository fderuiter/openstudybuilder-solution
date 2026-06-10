# pylint: disable=redefined-outer-name
"""Unit tests for generate_traceability.py - covering functions changed in this PR."""

import textwrap
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

import consumer_api.requirements.generate_traceability as gt


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

FS_MARKDOWN_WITH_TEST_COVERAGE = textwrap.dedent(
    """\
    # Feature Name

    ## FS-Core-Study-Lifecycle-010 [`URS-ConsumerApi-Studies`]

    The system must ensure lifecycle transitions.

    ### Validation Rules

    - Data integrity stuff

    ### Test coverage

    | Test File                    | Test Function        |
    | ---------------------------- | -------------------- |
    | tests/v1/test_api_studies.py | test_get_studies_all |

    ## FS-Core-Study-Identification-010 [`URS-ConsumerApi-Studies`]

    Identification stuff.

    ### Test coverage

    | Test File                    | Test Function              |
    | ---------------------------- | -------------------------- |
    | tests/v1/test_api_studies.py | test_get_studies_filtering |
    """
)

FS_MARKDOWN_NO_TEST_COVERAGE_SECTION = textwrap.dedent(
    """\
    # Feature Name

    ## FS-Library-Feature-010 [`URS-Library`]

    A feature without a test coverage section.
    """
)

URS_MARKDOWN = textwrap.dedent(
    """\
    # URS-ConsumerApi-Studies

    Studies must be properly managed.
    """
)


@pytest.fixture()
def fs_html_with_tests():
    """HTML converted from FS markdown that contains a Test coverage table."""
    import markdown

    return markdown.markdown(FS_MARKDOWN_WITH_TEST_COVERAGE, extensions=["tables"])


@pytest.fixture()
def fs_html_no_tests():
    """HTML converted from FS markdown that has no Test coverage section."""
    import markdown

    return markdown.markdown(FS_MARKDOWN_NO_TEST_COVERAGE_SECTION, extensions=["tables"])


# ---------------------------------------------------------------------------
# extract_fs_titles_and_tests
# ---------------------------------------------------------------------------


class TestExtractFsTitlesAndTests:
    """Tests for the refactored extract_fs_titles_and_tests(html_content) function."""

    def test_accepts_single_argument(self, fs_html_with_tests):
        """Function must accept a single argument (all_tests parameter was removed)."""
        # Should not raise TypeError
        result = gt.extract_fs_titles_and_tests(fs_html_with_tests)
        assert result is not None

    def test_returns_list(self, fs_html_with_tests):
        result = gt.extract_fs_titles_and_tests(fs_html_with_tests)
        assert isinstance(result, list)

    def test_returns_correct_number_of_entries(self, fs_html_with_tests):
        """Each FS section that has a Test coverage table should produce one entry."""
        result = gt.extract_fs_titles_and_tests(fs_html_with_tests)
        assert len(result) == 2

    def test_each_entry_is_triple(self, fs_html_with_tests):
        """Each entry must be a (title, table_element, tests_list) triple."""
        result = gt.extract_fs_titles_and_tests(fs_html_with_tests)
        for entry in result:
            assert len(entry) == 3

    def test_titles_start_with_fs(self, fs_html_with_tests):
        result = gt.extract_fs_titles_and_tests(fs_html_with_tests)
        for title, _table, _tests in result:
            assert title.startswith("FS-")

    def test_tests_list_contains_file_and_method(self, fs_html_with_tests):
        result = gt.extract_fs_titles_and_tests(fs_html_with_tests)
        for _title, _table, tests_list in result:
            for test in tests_list:
                assert "file" in test
                assert "method" in test

    def test_tests_list_values(self, fs_html_with_tests):
        result = gt.extract_fs_titles_and_tests(fs_html_with_tests)
        # First FS section
        _title, _table, tests_list = result[0]
        assert tests_list[0]["file"] == "tests/v1/test_api_studies.py"
        assert tests_list[0]["method"] == "test_get_studies_all"

    def test_second_fs_section_tests(self, fs_html_with_tests):
        result = gt.extract_fs_titles_and_tests(fs_html_with_tests)
        _title, _table, tests_list = result[1]
        assert tests_list[0]["file"] == "tests/v1/test_api_studies.py"
        assert tests_list[0]["method"] == "test_get_studies_filtering"

    def test_does_not_add_test_status_column(self, fs_html_with_tests):
        """Regression: the old implementation injected a 'Test Status' <th> into the table.
        The new implementation must NOT do this."""
        result = gt.extract_fs_titles_and_tests(fs_html_with_tests)
        for _title, table_element, _tests in result:
            header_row = table_element.find("tr")
            if header_row:
                headers = [th.get_text(strip=True) for th in header_row.find_all("th")]
                assert "Test Status" not in headers

    def test_does_not_add_test_status_td(self, fs_html_with_tests):
        """Regression: the old implementation added a 'Automated'/'Missing' <td> to data rows."""
        result = gt.extract_fs_titles_and_tests(fs_html_with_tests)
        for _title, table_element, _tests in result:
            for row in table_element.find_all("tr"):
                cells = row.find_all("td")
                cell_texts = [c.get_text(strip=True) for c in cells]
                assert "Automated" not in cell_texts
                assert "Missing" not in cell_texts

    def test_empty_html_returns_empty_list(self):
        result = gt.extract_fs_titles_and_tests("")
        assert result == []

    def test_no_fs_headers_returns_empty_list(self):
        """HTML that contains h2 elements not starting with 'FS-' yields nothing."""
        import markdown

        html = markdown.markdown("## URS-SomeOtherSection\n\nContent", extensions=["tables"])
        result = gt.extract_fs_titles_and_tests(html)
        assert result == []

    def test_fs_section_without_test_coverage_table_excluded(self, fs_html_no_tests):
        """FS sections that have no 'Test coverage' subsection must not appear in results."""
        result = gt.extract_fs_titles_and_tests(fs_html_no_tests)
        assert result == []

    def test_table_element_is_beautifulsoup_tag(self, fs_html_with_tests):
        """The second element in each tuple must be a BeautifulSoup Tag (the <table> element)."""
        from bs4 import Tag

        result = gt.extract_fs_titles_and_tests(fs_html_with_tests)
        for _title, table_element, _tests in result:
            assert isinstance(table_element, Tag)
            assert table_element.name == "table"


# ---------------------------------------------------------------------------
# collect_fs_traceability
# ---------------------------------------------------------------------------


class TestCollectFsTraceability:
    """Tests for the refactored collect_fs_traceability(fs_files, full_traceability) function."""

    def _make_fs_file(self, tmp_path, content, name="fs-test.md"):
        f = tmp_path / name
        f.write_text(content, encoding="utf-8")
        return f

    def test_accepts_two_arguments(self, tmp_path):
        """Function must accept exactly two positional arguments (all_tests was removed)."""
        fs_file = self._make_fs_file(tmp_path, FS_MARKDOWN_WITH_TEST_COVERAGE)
        full_traceability = [
            {"urs_id": "URS-ConsumerApi-Studies", "fs_list": [], "text": "", "type": "URS"}
        ]
        # Should not raise TypeError
        result = gt.collect_fs_traceability([fs_file], full_traceability)
        assert result is not None

    def test_returns_set(self, tmp_path):
        """collect_fs_traceability must return a set of FS IDs."""
        fs_file = self._make_fs_file(tmp_path, FS_MARKDOWN_WITH_TEST_COVERAGE)
        full_traceability = [
            {"urs_id": "URS-ConsumerApi-Studies", "fs_list": [], "text": "", "type": "URS"}
        ]
        result = gt.collect_fs_traceability([fs_file], full_traceability)
        assert isinstance(result, set)

    def test_returns_all_fs_ids(self, tmp_path):
        """All FS section IDs must be present in the returned set."""
        fs_file = self._make_fs_file(tmp_path, FS_MARKDOWN_WITH_TEST_COVERAGE)
        full_traceability = [
            {"urs_id": "URS-ConsumerApi-Studies", "fs_list": [], "text": "", "type": "URS"}
        ]
        result = gt.collect_fs_traceability([fs_file], full_traceability)
        assert "FS-Core-Study-Lifecycle-010" in result
        assert "FS-Core-Study-Identification-010" in result

    def test_links_fs_to_urs_in_traceability(self, tmp_path):
        """FSs must be linked to the matching URS entry in full_traceability."""
        fs_file = self._make_fs_file(tmp_path, FS_MARKDOWN_WITH_TEST_COVERAGE)
        full_traceability = [
            {"urs_id": "URS-ConsumerApi-Studies", "fs_list": [], "text": "", "type": "URS"}
        ]
        gt.collect_fs_traceability([fs_file], full_traceability)
        fs_ids = [fs["fs_id"] for fs in full_traceability[0]["fs_list"]]
        assert "FS-Core-Study-Lifecycle-010" in fs_ids
        assert "FS-Core-Study-Identification-010" in fs_ids

    def test_empty_file_list_returns_empty_set(self):
        result = gt.collect_fs_traceability([], [])
        assert result == set()

    def test_fs_not_linked_to_matching_urs_does_not_crash(self, tmp_path):
        """When no URS matches, the FS is still returned in the ID set; traceability unchanged."""
        fs_file = self._make_fs_file(tmp_path, FS_MARKDOWN_WITH_TEST_COVERAGE)
        full_traceability = []  # No URS entries
        result = gt.collect_fs_traceability([fs_file], full_traceability)
        assert "FS-Core-Study-Lifecycle-010" in result

    def test_duplicate_fs_id_logs_warning(self, tmp_path, caplog):
        """When the same FS ID appears in two files a warning must be emitted."""
        import logging

        fs_file1 = self._make_fs_file(tmp_path, FS_MARKDOWN_WITH_TEST_COVERAGE, "fs-a.md")
        fs_file2 = self._make_fs_file(tmp_path, FS_MARKDOWN_WITH_TEST_COVERAGE, "fs-b.md")
        full_traceability = [
            {"urs_id": "URS-ConsumerApi-Studies", "fs_list": [], "text": "", "type": "URS"}
        ]
        with caplog.at_level(logging.WARNING):
            gt.collect_fs_traceability([fs_file1, fs_file2], full_traceability)
        assert any("Duplicate FS ID" in r.message for r in caplog.records)


# ---------------------------------------------------------------------------
# get_warnings
# ---------------------------------------------------------------------------


class TestGetWarnings:
    """Tests for the refactored get_warnings(full_traceability, all_fs_ids=set()) function."""

    def _traceability_entry(self, urs_id, fs_list=None):
        return {
            "urs_id": urs_id,
            "type": "URS",
            "text": "",
            "fs_list": fs_list or [],
        }

    def _fs_entry(self, fs_id, tests_html="", tests_list=None):
        return {
            "fs_id": fs_id,
            "type": "FS",
            "text": "",
            "tests_html": tests_html,
            "tests_list": tests_list or [],
        }

    @patch.object(gt, "get_all_tests", return_value=[])
    def test_accepts_two_positional_arguments(self, _mock_tests):
        """Must accept (full_traceability, all_fs_ids) with no third argument."""
        result = gt.get_warnings([], set())
        assert result is not None

    @patch.object(gt, "get_all_tests", return_value=[])
    def test_accepts_default_all_fs_ids(self, _mock_tests):
        """all_fs_ids must default to an empty set (no third positional arg needed)."""
        result = gt.get_warnings([])
        assert result is not None

    @patch.object(gt, "get_all_tests", return_value=[])
    def test_calls_get_all_tests_internally(self, mock_tests):
        """get_warnings must call get_all_tests() itself rather than receiving tests as a param."""
        gt.get_warnings([])
        mock_tests.assert_called_once()

    @patch.object(gt, "get_all_tests", return_value=[])
    def test_returns_string(self, _mock_tests):
        result = gt.get_warnings([])
        assert isinstance(result, str)

    @patch.object(gt, "get_all_tests", return_value=[])
    def test_no_issues_returns_none_message(self, _mock_tests):
        """When there are no problems the output should contain '-- None --'."""
        entry = self._traceability_entry(
            "URS-ConsumerApi-Studies",
            fs_list=[self._fs_entry("FS-Core-Study-Lifecycle-010", tests_html="<table/>", tests_list=[])],
        )
        all_fs_ids = {"FS-Core-Study-Lifecycle-010"}
        result = gt.get_warnings([entry], all_fs_ids)
        assert "-- None --" in result

    @patch.object(gt, "get_all_tests", return_value=[])
    def test_urs_without_fs_detected(self, _mock_tests):
        """URS entries with empty fs_list must appear in the warnings output."""
        entry = self._traceability_entry("URS-ConsumerApi-Studies", fs_list=[])
        result = gt.get_warnings([entry], set())
        assert "URS-ConsumerApi-Studies" in result

    @patch.object(gt, "get_all_tests", return_value=[])
    def test_fs_without_tests_detected(self, _mock_tests):
        """FSs with no tests_html must appear in the warnings output."""
        fs = self._fs_entry("FS-Core-Study-Lifecycle-010", tests_html="")
        entry = self._traceability_entry("URS-ConsumerApi-Studies", fs_list=[fs])
        all_fs_ids = {"FS-Core-Study-Lifecycle-010"}
        result = gt.get_warnings([entry], all_fs_ids)
        assert "FS-Core-Study-Lifecycle-010" in result

    @patch.object(gt, "get_all_tests", return_value=[])
    def test_fs_not_linked_to_urs_detected(self, _mock_tests):
        """FSs in all_fs_ids that are not linked to any URS must appear in warnings."""
        entry = self._traceability_entry("URS-ConsumerApi-Studies", fs_list=[])
        all_fs_ids = {"FS-Orphan-010"}
        result = gt.get_warnings([entry], all_fs_ids)
        assert "FS-Orphan-010" in result

    @patch.object(
        gt,
        "get_all_tests",
        return_value=[{"file": "tests/v1/test_api_studies.py", "methods": ["test_get_studies_all"]}],
    )
    def test_non_existent_test_detected(self, _mock_tests):
        """Tests referenced in the FS but absent from get_all_tests() must be flagged."""
        tests_list = [{"file": "tests/v1/test_api_studies.py", "method": "test_nonexistent_method"}]
        fs = self._fs_entry(
            "FS-Core-Study-Lifecycle-010",
            tests_html="<table/>",
            tests_list=tests_list,
        )
        entry = self._traceability_entry("URS-ConsumerApi-Studies", fs_list=[fs])
        all_fs_ids = {"FS-Core-Study-Lifecycle-010"}
        result = gt.get_warnings([entry], all_fs_ids)
        assert "test_nonexistent_method" in result

    @patch.object(
        gt,
        "get_all_tests",
        return_value=[{"file": "tests/v1/test_api_studies.py", "methods": ["test_get_studies_all"]}],
    )
    def test_existing_test_not_flagged(self, _mock_tests):
        """Tests that exist in get_all_tests() must NOT be flagged as non-existent."""
        tests_list = [{"file": "tests/v1/test_api_studies.py", "method": "test_get_studies_all"}]
        fs = self._fs_entry(
            "FS-Core-Study-Lifecycle-010",
            tests_html="<table/>",
            tests_list=tests_list,
        )
        entry = self._traceability_entry("URS-ConsumerApi-Studies", fs_list=[fs])
        all_fs_ids = {"FS-Core-Study-Lifecycle-010"}
        result = gt.get_warnings([entry], all_fs_ids)
        # No 'Non-existent tests' warning items should appear for this method
        assert "test_get_studies_all" not in result or "Non-existent" not in result

    @patch.object(gt, "get_all_tests", return_value=[])
    def test_empty_traceability_returns_none_message(self, _mock_tests):
        result = gt.get_warnings([], set())
        assert "-- None --" in result


# ---------------------------------------------------------------------------
# get_all_tests
# ---------------------------------------------------------------------------


class TestGetAllTests:
    """Tests for the refactored get_all_tests() that only scans BASE_DIR/tests."""

    def test_returns_list(self, tmp_path):
        """Must return a list."""
        with patch.object(gt, "BASE_DIR", tmp_path):
            (tmp_path / "tests").mkdir()
            result = gt.get_all_tests()
        assert isinstance(result, list)

    def test_returns_entries_with_file_and_methods_keys(self, tmp_path):
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        test_file = tests_dir / "test_sample.py"
        test_file.write_text("def test_foo():\n    pass\ndef test_bar():\n    pass\n")
        with patch.object(gt, "BASE_DIR", tmp_path):
            result = gt.get_all_tests()
        assert len(result) == 1
        assert "file" in result[0]
        assert "methods" in result[0]

    def test_discovers_test_methods_correctly(self, tmp_path):
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        test_file = tests_dir / "test_sample.py"
        test_file.write_text(
            "def test_foo():\n    pass\ndef test_bar(param):\n    pass\ndef helper():\n    pass\n"
        )
        with patch.object(gt, "BASE_DIR", tmp_path):
            result = gt.get_all_tests()
        methods = result[0]["methods"]
        assert "test_foo" in methods
        assert "test_bar" in methods
        # Non-test functions must not be included
        assert "helper" not in methods

    def test_ignores_non_py_files(self, tmp_path):
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "not_a_test.txt").write_text("def test_foo(): pass")
        (tests_dir / "test_real.py").write_text("def test_real(): pass")
        with patch.object(gt, "BASE_DIR", tmp_path):
            result = gt.get_all_tests()
        assert len(result) == 1
        assert result[0]["file"].endswith("test_real.py")

    def test_only_scans_base_dir_tests_not_core_services(self, tmp_path):
        """Regression: get_all_tests must NOT scan any directory outside BASE_DIR/tests.
        The previous implementation also walked clinical_mdr_api/tests which was removed."""
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_consumer.py").write_text("def test_consumer(): pass")

        # Simulate a sibling directory that the old code used to scan
        sibling_dir = tmp_path.parent / "clinical_mdr_api" / "tests"
        sibling_dir.mkdir(parents=True, exist_ok=True)
        (sibling_dir / "test_core.py").write_text("def test_core(): pass")

        with patch.object(gt, "BASE_DIR", tmp_path):
            result = gt.get_all_tests()

        files_found = [r["file"] for r in result]
        # Sibling directory test must NOT appear
        assert not any("test_core" in f for f in files_found)
        # But the consumer api test must appear
        assert any("test_consumer" in f for f in files_found)

    def test_relative_paths_in_results(self, tmp_path):
        """File paths in results must be relative to BASE_DIR (not absolute)."""
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_something.py").write_text("def test_x(): pass")
        with patch.object(gt, "BASE_DIR", tmp_path):
            result = gt.get_all_tests()
        assert len(result) == 1
        # Path must be relative (not start with '/')
        assert not result[0]["file"].startswith("/")

    def test_empty_tests_dir_returns_empty_list(self, tmp_path):
        (tmp_path / "tests").mkdir()
        with patch.object(gt, "BASE_DIR", tmp_path):
            result = gt.get_all_tests()
        assert result == []

    def test_nested_test_directories_are_discovered(self, tmp_path):
        """Test files in subdirectories of tests/ must also be found."""
        tests_dir = tmp_path / "tests"
        sub_dir = tests_dir / "v1"
        sub_dir.mkdir(parents=True)
        (sub_dir / "test_nested.py").write_text("def test_nested_method(): pass")
        with patch.object(gt, "BASE_DIR", tmp_path):
            result = gt.get_all_tests()
        methods_found = [m for r in result for m in r["methods"]]
        assert "test_nested_method" in methods_found

    def test_file_with_no_test_methods_still_included(self, tmp_path):
        """A .py file that exists but has no test_ functions should still appear in the list."""
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "conftest.py").write_text("import pytest\n")
        with patch.object(gt, "BASE_DIR", tmp_path):
            result = gt.get_all_tests()
        assert len(result) == 1
        assert result[0]["methods"] == []
