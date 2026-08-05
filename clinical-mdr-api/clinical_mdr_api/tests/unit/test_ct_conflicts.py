from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from clinical_mdr_api.main import app
from common.auth.dependencies import RequiresAnyRole, oauth_scheme, validate_token

app.dependency_overrides[validate_token] = lambda: None
app.dependency_overrides[oauth_scheme] = lambda: "dummy"
RequiresAnyRole.__call__ = lambda self: None

client = TestClient(app)


def test_get_unresolved_conflicts_mocked():
    mock_db_result = (
        [
            (
                123,
                "codelist",
                "C66736",
                "definition",
                "conflicting values",
                "Codelist 1",
            ),
            (
                456,
                "term",
                "C12345",
                "preferredTerm",
                "conflicting preferred terms",
                "Term 1",
            ),
        ],
        MagicMock(),
    )
    with patch("neomodel.db.cypher_query", return_value=mock_db_result):
        response = client.get("/ct/conflicts")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["id"] == 123
        assert data[0]["type"] == "codelist"
        assert data[0]["conceptId"] == "C66736"
        assert data[0]["property"] == "definition"
        assert data[0]["inconsistency"] == "conflicting values"
        assert data[0]["parentName"] == "Codelist 1"


def test_get_conflict_details_mocked():
    # Mocking first query_info:
    # returns: parentLabel, property, inconsistency, conceptId, iLabel
    mock_info = (
        [
            (
                "GroupedCodelist",
                "definition",
                "conflicting values",
                "C66736",
                "InconsistentCodelistProperties",
            )
        ],
        MagicMock(),
    )
    # Mocking second query_sources:
    # returns: rawId, value, packageName, packageVersion
    mock_sources = (
        [(789, "Value A", "Package A", "v1"), (101, "Value B", "Package B", "v2")],
        MagicMock(),
    )

    def side_effect(query, params=None):
        if "labels(g)[0]" in query:
            return mock_info
        else:
            return mock_sources

    with patch("neomodel.db.cypher_query", side_effect=side_effect):
        response = client.get("/ct/conflicts/123")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 123
        assert data["parentLabel"] == "GroupedCodelist"
        assert data["property"] == "definition"
        assert data["conceptId"] == "C66736"
        assert len(data["sources"]) == 2
        assert data["sources"][0]["value"] == "Value A"
        assert data["sources"][0]["packageName"] == "Package A"


def test_resolve_conflict_mocked():
    mock_info = ([("GroupedCodelist", "definition")], MagicMock())
    mock_solution = ([], MagicMock())

    def side_effect(query, params=None):
        if "labels(g)[0]" in query:
            return mock_info
        else:
            return mock_solution

    with patch("neomodel.db.cypher_query", side_effect=side_effect) as mock_query:
        response = client.post(
            "/ct/conflicts/123/resolve", json={"value": "Resolved Definition"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "success"

        # Verify cypher_query was called to update solution & properties
        assert mock_query.call_count >= 3
