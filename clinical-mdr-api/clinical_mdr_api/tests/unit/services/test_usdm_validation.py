import logging
from unittest.mock import MagicMock
import pytest

from clinical_mdr_api.domains.study_definition_aggregates.study_metadata import StudyStatus
from clinical_mdr_api.services.ddf.usdm_mapper import USDMMapper
from usdm_model import Code as USDMCode
from common.exceptions import ValidationException


class MockObject:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


@pytest.fixture
def base_mapper():
    mapper = USDMMapper(
        get_osb_study_design_cells=lambda *args, **kwargs: [],
        get_osb_study_arms=lambda *args, **kwargs: MockObject(items=[]),
        get_osb_study_epochs=lambda *args, **kwargs: MockObject(items=[]),
        get_osb_study_elements=lambda *args, **kwargs: MockObject(items=[]),
        get_osb_study_endpoints=lambda *args, **kwargs: MockObject(items=[]),
        get_osb_study_visits=lambda *args, **kwargs: MockObject(items=[]),
        get_osb_study_activities=lambda *args, **kwargs: MockObject(items=[]),
        get_osb_activity_schedules=lambda *args, **kwargs: [],
    )
    # Mock database queries/lookups to keep tests pure and database-independent
    mapper._resolve_ct_package_effective_date = lambda uid: "2026-08-06"
    mapper._load_registid_labels = lambda: {}
    return mapper


@pytest.fixture
def mock_study_builder():
    def _build(status="DRAFT", trial_phase_term=None, study_type_term=None):
        version_metadata = MockObject(study_status=status, version_number=1)
        study_description = MockObject(study_title="Test Study Title", study_short_title="Test Short Title")
        
        trial_phase_code = None
        if trial_phase_term:
            trial_phase_code = MockObject(term_uid=trial_phase_term)
            
        study_type_code = None
        if study_type_term:
            study_type_code = MockObject(term_uid=study_type_term)
            
        high_level_study_design = MockObject(
            trial_phase_code=trial_phase_code,
            study_type_code=study_type_code,
        )
        study_population = MockObject(
            sex_of_participants_code=None,
            diagnosis_group_codes=[],
            disease_condition_or_indication_codes=[],
            healthy_subject_indicator=None,
            number_of_expected_subjects=None,
            pediatric_investigation_plan_indicator=None,
            pediatric_postmarket_study_indicator=None,
            pediatric_study_indicator=None,
            planned_maximum_age_of_subjects=None,
            planned_minimum_age_of_subjects=None,
            rare_disease_indicator=None,
            relapse_criteria=None,
            stable_disease_minimum_duration=None,
            therapeutic_area_code=None,
            therapeutic_area_codes=[],
        )
        study_intervention = MockObject(
            intervention_model_code=None,
            control_type_code=None,
            trial_blinding_schema_code=None,
            trial_intent_types_codes=[],
            intervention_type_code=None,
            interventions=MockObject(items=[])
        )
        
        identification_metadata = MockObject(
            study_id="Mock Study Name",
            registry_identifiers=MockObject(items=[]),
            sponsor_identifiers=MockObject(items=[]),
        )
        
        current_metadata = MockObject(
            version_metadata=version_metadata,
            study_description=study_description,
            high_level_study_design=high_level_study_design,
            study_population=study_population,
            study_intervention=study_intervention,
            identification_metadata=identification_metadata,
        )
        
        return MockObject(uid="Study_000001", current_metadata=current_metadata)
    return _build


def test_draft_status_missing_phase_and_type_logs_warning_and_returns_placeholder(base_mapper, mock_study_builder, caplog):
    """Mapping a draft study with missing or unmapped design phases/types generates expected payload and records a warning."""
    study = mock_study_builder(status="DRAFT", trial_phase_term=None, study_type_term=None)
    
    # We want get_ct_package_term_as_usdm_code to return void code
    base_mapper.get_ct_package_term_as_usdm_code = lambda cid: base_mapper.get_void_usdm_code()
    
    with caplog.at_level(logging.WARNING):
        result = base_mapper.map(study)
        
    assert result is not None
    assert "study" in result
    
    # Verify warning logs were captured
    warnings = [rec.message for rec in caplog.records if rec.levelno == logging.WARNING]
    assert any("studyPhase" in w for w in warnings)
    assert any("studyType" in w for w in warnings)


def test_locked_status_missing_phase_and_type_raises_exception_listing_missing_attributes(base_mapper, mock_study_builder):
    """Mapping a locked study with missing or unmapped design phases raises a validation error explicitly listing them."""
    study = mock_study_builder(status="LOCKED", trial_phase_term=None, study_type_term=None)
    
    base_mapper.get_ct_package_term_as_usdm_code = lambda cid: base_mapper.get_void_usdm_code()
    
    with pytest.raises(ValidationException) as exc_info:
        base_mapper.map(study)
        
    assert "Validation failed for locked study" in str(exc_info.value)
    assert "studyPhase" in str(exc_info.value)
    assert "studyType" in str(exc_info.value)


def test_locked_status_with_valid_phase_and_type_passes(base_mapper, mock_study_builder):
    """Mapping a locked study with fully mapped trial phase and study type succeeds."""
    study = mock_study_builder(status="LOCKED", trial_phase_term="C15603", study_type_term="C98388")
    
    # Mock term resolution to return a valid code
    def mock_get_term(concept_id):
        if concept_id in ["C15603", "C98388"]:
            return USDMCode(
                id=f"code-{concept_id}",
                code=concept_id,
                codeSystem="CDISC CT",
                codeSystemVersion="2026-08-06",
                decode="Mocked Term",
                instanceType="Code"
            )
        return base_mapper.get_void_usdm_code()
        
    base_mapper.get_ct_package_term_as_usdm_code = mock_get_term
    
    result = base_mapper.map(study)
    assert result is not None


def test_unsupported_status_raises_exception(base_mapper, mock_study_builder):
    """Studies with unsupported lifecycle states trigger a validation failure immediately."""
    study = mock_study_builder(status="RELEASED")
    
    with pytest.raises(ValidationException) as exc_info:
        base_mapper.map(study)
        
    assert "Unsupported study workflow status" in str(exc_info.value)
    assert "RELEASED" in str(exc_info.value)
