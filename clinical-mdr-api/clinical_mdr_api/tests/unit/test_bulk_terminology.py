from unittest.mock import MagicMock, patch
import pytest

from clinical_mdr_api.models.controlled_terminologies.ct_term import CTTerm
from clinical_mdr_api.models.controlled_terminologies.ct_codelist import CTCodelist

@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    from clinical_mdr_api.main import app
    from common.auth.dependencies import RequiresAnyRole, oauth_scheme, validate_token

    # Store original overrides
    original_overrides = app.dependency_overrides.copy()

    try:
        # Set overrides
        app.dependency_overrides[validate_token] = lambda: None
        app.dependency_overrides[oauth_scheme] = lambda: "dummy"

        # Patch RequiresAnyRole.__call__ to bypass RBAC globally during these tests
        with patch.object(RequiresAnyRole, "__call__", new=lambda self: None):
            test_client = TestClient(app)
            yield test_client
    finally:
        # Restore original overrides
        app.dependency_overrides = original_overrides


def test_create_bulk_terms_mocked(client):
    mock_response = [
        CTTerm(
            term_uid="term1_uid",
            catalogue_names=["CDISC CT"],
            concept_id="C10101",
            nci_preferred_name="NCI Term 1",
            definition="Definition 1",
            sponsor_preferred_name="Term 1",
            sponsor_preferred_name_sentence_case="Term 1 Case",
            library_name="Sponsor",
            codelists=[],
            possible_actions=[]
        ),
        CTTerm(
            term_uid="term2_uid",
            catalogue_names=["CDISC CT"],
            concept_id="C10102",
            nci_preferred_name="NCI Term 2",
            definition="Definition 2",
            sponsor_preferred_name="Term 2",
            sponsor_preferred_name_sentence_case="Term 2 Case",
            library_name="Sponsor",
            codelists=[],
            possible_actions=[]
        )
    ]
    
    mock_user = MagicMock()
    mock_user.id.return_value = "dummy_user_id"
    
    with patch("clinical_mdr_api.services.controlled_terminologies.ct_term.user", return_value=mock_user):
        # We patch the service layer to avoid hitting the actual database
        with patch("clinical_mdr_api.services.controlled_terminologies.ct_term.CTTermService.create_bulk", return_value=mock_response):
            payload = [
                {
                    "catalogue_names": ["CDISC CT"],
                    "library_name": "Sponsor",
                    "nci_preferred_name": "NCI Term 1",
                    "definition": "Definition 1",
                    "concept_id": "C10101",
                    "sponsor_preferred_name": "Term 1",
                    "sponsor_preferred_name_sentence_case": "Term 1 Case",
                    "codelists": []
                },
                {
                    "catalogue_names": ["CDISC CT"],
                    "library_name": "Sponsor",
                    "nci_preferred_name": "NCI Term 2",
                    "definition": "Definition 2",
                    "concept_id": "C10102",
                    "sponsor_preferred_name": "Term 2",
                    "sponsor_preferred_name_sentence_case": "Term 2 Case",
                    "codelists": []
                }
            ]
            
            response = client.post("/ct/terms/bulk", json=payload)
            assert response.status_code == 201


def test_add_terms_to_codelist_bulk_mocked(client):
    mock_response = CTCodelist(
        catalogue_names=["CDISC CT"],
        codelist_uid="cl_123",
        parent_codelist_uid=None,
        child_codelist_uids=[],
        paired_codes_codelist_uid=None,
        paired_names_codelist_uid=None,
        name="Codelist 1",
        submission_value="SUBVAL",
        nci_preferred_name="NCI Codelist",
        definition="Definition of codelist",
        extensible=True,
        is_ordinal=False,
        codelist_type="DEFAULT",
        library_name="Sponsor",
        sponsor_preferred_name="Sponsor Codelist Name",
        template_parameter=False,
        possible_actions=[],
    )
    mock_user = MagicMock()
    mock_user.id.return_value = "dummy_user_id"
    
    with patch("clinical_mdr_api.services.controlled_terminologies.ct_codelist.user", return_value=mock_user):
        with patch("clinical_mdr_api.services.controlled_terminologies.ct_codelist.CTCodelistService.add_terms_bulk", return_value=mock_response):
            payload = [
                {
                    "term_uid": "term_abc",
                    "order": 1,
                    "submission_value": "SUBVAL1",
                    "ordinal": 1.0
                },
                {
                    "term_uid": "term_xyz",
                    "order": 2,
                    "submission_value": "SUBVAL2",
                    "ordinal": 2.0
                }
            ]
            
            response = client.post("/ct/codelists/cl_123/terms/bulk", json=payload)
            assert response.status_code == 201
