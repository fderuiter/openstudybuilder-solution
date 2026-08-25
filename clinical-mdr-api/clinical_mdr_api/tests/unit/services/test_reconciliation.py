from unittest.mock import MagicMock, patch
import pytest
from common.exceptions import BusinessLogicException
from clinical_mdr_api.models.reconciliation import (
    DiffItem,
    LineageInfo,
    ReconciliationDiffResponse,
    ReconciliationRequest,
)
from clinical_mdr_api.domains.study_definition_aggregates.study_metadata import StudyStatus
from clinical_mdr_api.services.studies.study import StudyService


def test_lineage_info_model():
    lineage = LineageInfo(
        parent_template_uid="template_123",
        parent_template_version="1.0",
        sync_status="NEEDS_REVIEW",
        requires_review=True,
    )
    assert lineage.parent_template_uid == "template_123"
    assert lineage.sync_status == "NEEDS_REVIEW"
    assert lineage.requires_review is True


def test_reconciliation_diff_response():
    diff_item = DiffItem(
        field="study_acronym",
        label="Study Acronym",
        category="Metadata",
        change_type="MODIFIED",
        current_value="Draft Study",
        template_value="Template Study",
    )
    resp = ReconciliationDiffResponse(
        study_uid="study_1",
        parent_template_uid="tmpl_1",
        parent_template_version="1.0",
        current_template_version="2.0",
        sync_status="NEEDS_REVIEW",
        diffs=[diff_item],
        total_diffs=1,
    )
    assert resp.study_uid == "study_1"
    assert len(resp.diffs) == 1
    assert resp.diffs[0].field == "study_acronym"


def test_reconcile_study_locked_study_guardrail():
    service = StudyService()
    mock_study_ar = MagicMock()
    mock_study_ar.status = StudyStatus.LOCKED  # Locked study!

    with patch.object(service._repos.study_definition_repository, "find_by_uid", return_value=mock_study_ar):
        req = ReconciliationRequest(selected_fields=["study_acronym"], comments="Merging updates")
        with pytest.raises(BusinessLogicException) as excinfo:
            service.reconcile_study(study_uid="locked_study_uid", req=req)
        assert "unlocked study drafts" in str(excinfo.value)
