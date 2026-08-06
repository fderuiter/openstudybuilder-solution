from unittest.mock import patch

from clinical_mdr_api.services.syntax_templates.generic_syntax_template_service import (
    get_affected_studies_for_template,
)


def test_get_affected_studies_for_template_objective():
    sample_rows = [
        ("Study_0001", "ACR1", "SUB1", "ID1"),
        ("Study_0002", "ACR2", None, "ID2"),
    ]

    with patch("neomodel.db.cypher_query") as mock_cypher:
        mock_cypher.return_value = (sample_rows, None)

        results = get_affected_studies_for_template("ObjectiveTemplate_000001")

        # Verify cypher_query was called
        mock_cypher.assert_called_once()
        query_arg = mock_cypher.call_args[0][0]
        assert "HAS_OBJECTIVE" in query_arg
        assert "HAS_SELECTED_OBJECTIVE" in query_arg
        assert "HAS_STUDY_OBJECTIVE" in query_arg

        # Verify mapped results
        assert len(results) == 2
        assert results[0] == {
            "uid": "Study_0001",
            "acronym": "ACR1",
            "subpart_acronym": "SUB1",
            "id": "ID1",
        }
        assert results[1] == {
            "uid": "Study_0002",
            "acronym": "ACR2",
            "subpart_acronym": None,
            "id": "ID2",
        }


def test_get_affected_studies_for_template_timeframe():
    sample_rows = []

    with patch("neomodel.db.cypher_query") as mock_cypher:
        mock_cypher.return_value = (sample_rows, None)

        results = get_affected_studies_for_template("TimeframeTemplate_000001")

        mock_cypher.assert_called_once()
        query_arg = mock_cypher.call_args[0][0]
        assert "HAS_TIMEFRAME" in query_arg
        assert "HAS_SELECTED_TIMEFRAME" in query_arg
        assert "HAS_STUDY_ENDPOINT" in query_arg
        assert len(results) == 0


def test_get_affected_studies_for_template_unknown():
    results = get_affected_studies_for_template("UnknownTemplate_000001")
    assert not results
