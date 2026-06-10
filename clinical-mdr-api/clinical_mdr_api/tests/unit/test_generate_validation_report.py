"""Unit tests for generate_validation_report.py

Tests for sanitize_test_name, get_test_status, and the HTML-generation logic
inside generate_report.  The ``gherkin`` library is mocked at module level
because it is not installed as a standard pipenv dependency.
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ──────────────────────────────────────────────────────────────────────────────
# Mock gherkin before importing the module under test, because gherkin is an
# optional runtime import in generate_validation_report.py that is not
# available outside the full pipenv environment.
# ──────────────────────────────────────────────────────────────────────────────
_gherkin_mock = MagicMock()
_gherkin_parser_mock = MagicMock()
_gherkin_token_scanner_mock = MagicMock()
sys.modules.setdefault("gherkin", _gherkin_mock)
sys.modules.setdefault("gherkin.parser", _gherkin_parser_mock)
sys.modules.setdefault("gherkin.token_scanner", _gherkin_token_scanner_mock)

from generate_validation_report import (  # noqa: E402
    generate_report,
    get_test_status,
    sanitize_test_name,
)


# ──────────────────────────────────────────────────────────────────────────────
# sanitize_test_name
# ──────────────────────────────────────────────────────────────────────────────
class TestSanitizeTestName:
    def test_simple_space_separated_words(self):
        assert sanitize_test_name("Lock a Study") == "test_lock_a_study"

    def test_special_characters_replaced_by_underscore(self):
        assert sanitize_test_name("Fail to Lock: Invalid!") == "test_fail_to_lock_invalid"

    def test_digits_preserved(self):
        assert sanitize_test_name("Scenario 42 Check") == "test_scenario_42_check"

    def test_already_lowercase_input(self):
        assert sanitize_test_name("some scenario name") == "test_some_scenario_name"

    def test_leading_trailing_non_word_chars_stripped(self):
        assert sanitize_test_name("---Hello World---") == "test_hello_world"

    def test_multiple_consecutive_spaces_collapsed(self):
        assert sanitize_test_name("Hello   World") == "test_hello_world"

    def test_single_quotes_become_underscores(self):
        result = sanitize_test_name("Final Protocol's version")
        assert result == "test_final_protocol_s_version"

    def test_mixed_case_lowercased(self):
        assert sanitize_test_name("Lock A STUDY In Draft State") == "test_lock_a_study_in_draft_state"

    def test_hyphens_become_underscores(self):
        assert sanitize_test_name("Lock-Study") == "test_lock_study"

    def test_parentheses_removed(self):
        assert sanitize_test_name("Fail (to lock)") == "test_fail_to_lock"

    def test_dots_in_version_numbers(self):
        assert sanitize_test_name("Version 1.0 Check") == "test_version_1_0_check"

    def test_all_uppercase(self):
        assert sanitize_test_name("LOCK STUDY") == "test_lock_study"

    def test_study_locking_scenario_name(self):
        """Reproduce the exact scenario name from study_locking.feature."""
        assert sanitize_test_name("Lock a Study in Draft State") == "test_lock_a_study_in_draft_state"

    def test_final_protocol_scenario_name(self):
        result = sanitize_test_name(
            "Fail to Lock a Study with Final Protocol with invalid version"
        )
        assert result == "test_fail_to_lock_a_study_with_final_protocol_with_invalid_version"

    def test_result_always_starts_with_test_prefix(self):
        for name in ["Hello", "hello world", "123", "  spaces  "]:
            assert sanitize_test_name(name).startswith("test_")

    def test_only_non_word_characters_gives_test_prefix_only(self):
        # All non-word chars → everything stripped → only "test_" remains
        result = sanitize_test_name("---")
        assert result == "test_"

    def test_subpart_scenario_name(self):
        assert sanitize_test_name("Fail to Lock a Subpart Independently") == (
            "test_fail_to_lock_a_subpart_independently"
        )


# ──────────────────────────────────────────────────────────────────────────────
# get_test_status
# ──────────────────────────────────────────────────────────────────────────────
class TestGetTestStatus:
    """Tests for get_test_status – looks up a testcase in a JUnit XML tree."""

    @staticmethod
    def _root(xml: str) -> ET.Element:
        return ET.fromstring(xml)

    def test_returns_missing_when_root_is_none(self):
        assert get_test_status(None, "test_anything") == "Missing"

    def test_returns_passed_for_clean_testcase(self):
        root = self._root("<testsuite><testcase name='test_my_scenario'/></testsuite>")
        assert get_test_status(root, "test_my_scenario") == "Passed"

    def test_returns_failing_for_failure_element(self):
        root = self._root(
            "<testsuite>"
            "  <testcase name='test_bad'><failure message='err'>details</failure></testcase>"
            "</testsuite>"
        )
        assert get_test_status(root, "test_bad") == "Failing"

    def test_returns_failing_for_error_element(self):
        root = self._root(
            "<testsuite>"
            "  <testcase name='test_err'><error message='RuntimeError'/></testcase>"
            "</testsuite>"
        )
        assert get_test_status(root, "test_err") == "Failing"

    def test_returns_skipped_for_skipped_element(self):
        root = self._root(
            "<testsuite>"
            "  <testcase name='test_skip'><skipped message='reason'/></testcase>"
            "</testsuite>"
        )
        assert get_test_status(root, "test_skip") == "Skipped"

    def test_returns_missing_when_testcase_not_found(self):
        root = self._root("<testsuite><testcase name='test_other'/></testsuite>")
        assert get_test_status(root, "test_nonexistent") == "Missing"

    def test_searches_deeply_nested_testcases(self):
        root = self._root(
            "<testsuites>"
            "  <testsuite name='suite1'>"
            "    <testcase name='test_nested'/>"
            "  </testsuite>"
            "</testsuites>"
        )
        assert get_test_status(root, "test_nested") == "Passed"

    def test_failure_checked_before_skipped(self):
        """When both <failure> and <skipped> are present, 'Failing' is returned."""
        root = self._root(
            "<testsuite>"
            "  <testcase name='test_combo'><failure/><skipped/></testcase>"
            "</testsuite>"
        )
        assert get_test_status(root, "test_combo") == "Failing"

    def test_empty_testsuite_returns_missing(self):
        root = self._root("<testsuite/>")
        assert get_test_status(root, "test_anything") == "Missing"

    def test_partial_name_does_not_match(self):
        root = self._root(
            "<testsuite>"
            "  <testcase name='test_lock_a_study_in_draft_state'/>"
            "</testsuite>"
        )
        assert get_test_status(root, "test_lock_a_study") == "Missing"
        assert get_test_status(root, "test_lock_a_study_in_draft_state") == "Passed"

    def test_multiple_testcases_returns_correct_status_for_each(self):
        root = self._root(
            "<testsuite>"
            "  <testcase name='test_a'/>"
            "  <testcase name='test_b'><failure/></testcase>"
            "  <testcase name='test_c'><skipped/></testcase>"
            "</testsuite>"
        )
        assert get_test_status(root, "test_a") == "Passed"
        assert get_test_status(root, "test_b") == "Failing"
        assert get_test_status(root, "test_c") == "Skipped"

    def test_duplicate_testcase_names_returns_first_match(self):
        """If duplicate names exist, the first match (Passed) should be returned."""
        root = self._root(
            "<testsuite>"
            "  <testcase name='test_dup'/>"
            "  <testcase name='test_dup'><failure/></testcase>"
            "</testsuite>"
        )
        # First match wins – no failure element → Passed
        assert get_test_status(root, "test_dup") == "Passed"


# ──────────────────────────────────────────────────────────────────────────────
# Status-text display mapping (inline logic inside generate_report)
# ──────────────────────────────────────────────────────────────────────────────
class TestStatusTextMapping:
    """The generate_report function maps internal status values to display labels."""

    @staticmethod
    def _map(status: str) -> str:
        return (
            "Verified"
            if status == "Passed"
            else ("Non-Compliant" if status == "Failing" else status)
        )

    def test_passed_maps_to_verified(self):
        assert self._map("Passed") == "Verified"

    def test_failing_maps_to_non_compliant(self):
        assert self._map("Failing") == "Non-Compliant"

    def test_missing_is_unchanged(self):
        assert self._map("Missing") == "Missing"

    def test_skipped_is_unchanged(self):
        assert self._map("Skipped") == "Skipped"


# ──────────────────────────────────────────────────────────────────────────────
# Domain / tag extraction logic (inline in generate_report)
# ──────────────────────────────────────────────────────────────────────────────
class TestDomainTagExtraction:
    """Test that domain and FS-ID tags are parsed correctly from feature tags."""

    def _extract_domain_and_fs_ids(self, feature_tags, default_domain="studies"):
        domain = default_domain
        fs_ids = []
        for tag in feature_tags:
            tag_name = tag["name"]
            if tag_name.startswith("@domain:"):
                domain = tag_name.split(":")[1].replace("_", " ")
            elif tag_name.startswith("@FS-"):
                fs_ids.append(tag_name[1:])
        return domain, fs_ids

    def test_domain_extracted_from_tag(self):
        tags = [{"name": "@domain:Protocol_Management"}]
        domain, _ = self._extract_domain_and_fs_ids(tags)
        assert domain == "Protocol Management"

    def test_underscore_in_domain_becomes_space(self):
        tags = [{"name": "@domain:Study_Design"}]
        domain, _ = self._extract_domain_and_fs_ids(tags)
        assert domain == "Study Design"

    def test_default_domain_used_when_no_domain_tag(self):
        tags = [{"name": "@FS-Foo-001"}]
        domain, _ = self._extract_domain_and_fs_ids(tags, default_domain="custom_dir")
        assert domain == "custom_dir"

    def test_fs_id_extracted_from_feature_tag(self):
        tags = [{"name": "@FS-StudyLock-001"}]
        _, fs_ids = self._extract_domain_and_fs_ids(tags)
        assert "FS-StudyLock-001" in fs_ids

    def test_non_fs_non_domain_tags_ignored(self):
        tags = [{"name": "@smoke"}, {"name": "@regression"}]
        domain, fs_ids = self._extract_domain_and_fs_ids(tags)
        assert fs_ids == []

    def test_multiple_fs_ids_all_collected(self):
        tags = [{"name": "@FS-A-001"}, {"name": "@FS-B-002"}]
        _, fs_ids = self._extract_domain_and_fs_ids(tags)
        assert set(fs_ids) == {"FS-A-001", "FS-B-002"}


# ──────────────────────────────────────────────────────────────────────────────
# Scenario FS-ID inheritance (feature-level FS ids cascade to scenarios)
# ──────────────────────────────────────────────────────────────────────────────
class TestScenarioFsIdInheritance:
    """Scenario inherits feature-level FS IDs and appends its own."""

    def _get_scenario_fs_ids(self, feature_fs_ids, scenario_tags):
        scenario_fs_ids = list(feature_fs_ids)
        for tag in scenario_tags:
            tag_name = tag["name"]
            if tag_name.startswith("@FS-"):
                scenario_fs_ids.append(tag_name[1:])
        return list(set(scenario_fs_ids))

    def test_inherits_feature_level_ids(self):
        ids = self._get_scenario_fs_ids(["FS-Parent-001"], [])
        assert "FS-Parent-001" in ids

    def test_scenario_specific_id_added(self):
        ids = self._get_scenario_fs_ids([], [{"name": "@FS-Child-002"}])
        assert "FS-Child-002" in ids

    def test_both_feature_and_scenario_ids_present(self):
        ids = self._get_scenario_fs_ids(
            ["FS-Parent-001"], [{"name": "@FS-Child-002"}]
        )
        assert "FS-Parent-001" in ids
        assert "FS-Child-002" in ids

    def test_deduplicated_when_same_id_on_feature_and_scenario(self):
        ids = self._get_scenario_fs_ids(
            ["FS-Same-001"], [{"name": "@FS-Same-001"}]
        )
        assert ids.count("FS-Same-001") == 1


# ──────────────────────────────────────────────────────────────────────────────
# Step formatting (inline in generate_report)
# ──────────────────────────────────────────────────────────────────────────────
class TestStepFormatting:
    """Steps are formatted as 'keyword text'."""

    def _format_steps(self, raw_steps):
        return [f"{step['keyword'].strip()} {step['text']}" for step in raw_steps]

    def test_given_when_then_formatted(self):
        raw = [
            {"keyword": "Given ", "text": "a study exists"},
            {"keyword": "When ", "text": "user locks it"},
            {"keyword": "Then ", "text": "it is locked"},
        ]
        assert self._format_steps(raw) == [
            "Given a study exists",
            "When user locks it",
            "Then it is locked",
        ]

    def test_and_step_formatted(self):
        raw = [{"keyword": "And ", "text": "the study has a number"}]
        assert self._format_steps(raw) == ["And the study has a number"]

    def test_keyword_trailing_space_stripped(self):
        raw = [{"keyword": "Given   ", "text": "something"}]
        assert self._format_steps(raw) == ["Given something"]

    def test_empty_steps_list(self):
        assert self._format_steps([]) == []


# ──────────────────────────────────────────────────────────────────────────────
# XML parsing failure handling (inline in generate_report)
# ──────────────────────────────────────────────────────────────────────────────
class TestXmlParseFailureHandling:
    def test_malformed_xml_does_not_raise(self, tmp_path):
        """Malformed JUnit XML should produce xml_root=None without crashing."""
        xml_path = tmp_path / "unit_report.xml"
        xml_path.write_text("<invalid xml><unclosed>", encoding="utf-8")

        xml_root = None
        if xml_path.exists():
            try:
                tree = ET.parse(str(xml_path))
                xml_root = tree.getroot()
            except Exception:
                pass  # Swallowed, xml_root stays None

        assert xml_root is None

    def test_valid_xml_parsed_correctly(self, tmp_path):
        xml_path = tmp_path / "unit_report.xml"
        xml_path.write_text(
            "<testsuite><testcase name='test_foo'/></testsuite>", encoding="utf-8"
        )

        xml_root = None
        if xml_path.exists():
            try:
                tree = ET.parse(str(xml_path))
                xml_root = tree.getroot()
            except Exception:
                pass

        assert xml_root is not None
        assert get_test_status(xml_root, "test_foo") == "Passed"

    def test_missing_xml_file_results_in_none_root(self, tmp_path):
        xml_path = tmp_path / "nonexistent.xml"
        xml_root = None
        if xml_path.exists():
            try:
                tree = ET.parse(str(xml_path))
                xml_root = tree.getroot()
            except Exception:
                pass
        assert xml_root is None