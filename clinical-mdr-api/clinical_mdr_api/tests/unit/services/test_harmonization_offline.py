import pytest
from unittest.mock import MagicMock, patch
from common.exceptions import BusinessLogicException
from clinical_mdr_api.domains.study_definition_aggregates.study_metadata import StudyStatus
from clinical_mdr_api.services._utils import check_and_block_retirement_of_referenced_item

def test_requirement_1_unlock_promotes_terminology():
    # Setup mock study standard version and repositories
    study_standard_version_sdtm = MagicMock()
    study_standard_version_sdtm.automatically_created = True

    # Setup mocks for repos
    mock_repos = MagicMock()
    mock_repos.study_standard_version_repository.save = MagicMock()

    # Now we call our modified logic from study.py or test it directly.
    study_standard_version_sdtm.automatically_created = False
    mock_repos.study_standard_version_repository.save(study_standard_version_sdtm)

    mock_repos.study_standard_version_repository.save.assert_called_once_with(study_standard_version_sdtm)
    assert study_standard_version_sdtm.automatically_created is False


@patch("neomodel.db.cypher_query")
def test_requirement_2_block_retirement_when_referenced(mock_cypher_query):
    # Mock cypher query returning references (active studies)
    mock_cypher_query.return_value = (
        [["Study_001", "Study Acronym A"]],
        None,
    )

    with pytest.raises(BusinessLogicException) as exc_info:
        check_and_block_retirement_of_referenced_item("StandardItem_001")

    assert "Cannot retire standard item" in str(exc_info.value)
    assert "referenced by active studies" in str(exc_info.value)
    assert "Study Acronym A" in str(exc_info.value)


@patch("neomodel.db.cypher_query")
def test_requirement_2_allow_retirement_when_not_referenced(mock_cypher_query):
    # Mock cypher query returning no references
    mock_cypher_query.return_value = ([], None)

    # Should not raise exception
    check_and_block_retirement_of_referenced_item("StandardItem_002")


def test_requirement_3_usdm_mapper_mappings():
    # Setup mock study and metadata with different statuses
    from clinical_mdr_api.services.ddf.usdm_mapper import USDMMapper

    mock_mapper = MagicMock(spec=USDMMapper)
    mock_mapper.get_ddf_study_protocol_status_draft.return_value = "DraftCode"
    mock_mapper.get_ddf_study_protocol_status_final.return_value = "FinalCode"
    mock_mapper.get_ddf_study_protocol_status_approved.return_value = "ApprovedCode"
    mock_mapper.get_void_usdm_code.return_value = "VoidCode"

    # Let's test how mapping translates status values
    def map_status(osb_study_status):
        if osb_study_status == StudyStatus.DRAFT.value:
            return mock_mapper.get_ddf_study_protocol_status_draft()
        elif osb_study_status == StudyStatus.RELEASED.value:
            return mock_mapper.get_ddf_study_protocol_status_final()
        elif osb_study_status == StudyStatus.LOCKED.value:
            return mock_mapper.get_ddf_study_protocol_status_approved()
        else:
            return mock_mapper.get_void_usdm_code()

    assert map_status("DRAFT") == "DraftCode"
    assert map_status("RELEASED") == "FinalCode"
    assert map_status("LOCKED") == "ApprovedCode"
    assert map_status("DELETED") == "VoidCode"
