import datetime
import unittest
from unittest.mock import MagicMock, patch
import pytest

# Mock neomodel transaction control methods so they don't attempt connection
patch("neomodel.db.begin", MagicMock()).start()
patch("neomodel.db.commit", MagicMock()).start()
patch("neomodel.db.rollback", MagicMock()).start()

from clinical_mdr_api.domains.study_definition_aggregates.study_metadata import (
    StudyStatus,
)
from clinical_mdr_api.domains.study_selections.study_disease_milestone import (
    StudyDiseaseMilestoneVO,
    StudyDiseaseMilestoneType,
    DiseaseMilestoneTypeNamedTuple,
    TypeNameDefinition,
)
from clinical_mdr_api.models.study_selections.study_disease_milestone import (
    StudyDiseaseMilestoneEditInput,
)
from clinical_mdr_api.services.studies.study_disease_milestone import (
    StudyDiseaseMilestoneService,
)
from common.exceptions import ValidationException, NotFoundException
from clinical_mdr_api.repositories._utils import FilterOperator


class TestStudyDiseaseMilestoneServiceUnit(unittest.TestCase):
    @patch("clinical_mdr_api.services.studies.study_disease_milestone.MetaRepository")
    @patch("clinical_mdr_api.services.studies.study_disease_milestone.user")
    @patch("clinical_mdr_api.services.studies.study_disease_milestone.UserInfoService.get_author_username_from_id")
    def test_transform_all_to_response_model_validation(self, mock_get_username, mock_user, mock_meta_repo):
        mock_get_username.return_value = "test_username"
        mock_user.return_value.id.return_value = "test_user"
        mock_repo = MagicMock()
        mock_repo.create_ctlist_definition.return_value = {
            "Disease_Milestone_Type_0001": {"name": "Type 1", "definition": "Def 1"}
        }
        mock_meta_repo.return_value.study_disease_milestone_repository = mock_repo

        service = StudyDiseaseMilestoneService()

        # Setup StudyDiseaseMilestoneType dictionary for validation (must be done after service instantiation)
        StudyDiseaseMilestoneType.clear()
        StudyDiseaseMilestoneType["Disease_Milestone_Type_0001"] = DiseaseMilestoneTypeNamedTuple(
            name="Disease_Milestone_Type_0001",
            value=TypeNameDefinition(named="Type 1", definition="Def 1")
        )

        # Valid milestone
        valid_vo = StudyDiseaseMilestoneVO(
            uid="Milestone_000001",
            study_uid="Study_000001",
            order=1,
            status=StudyStatus.DRAFT,
            start_date=datetime.datetime.now(datetime.timezone.utc),
            author_id="test_user",
            author_username="test_username",
            disease_milestone_type="Disease_Milestone_Type_0001",
            disease_milestone_type_name="Type 1",
            disease_milestone_type_definition="Def 1",
            repetition_indicator=True,
        )
        response_model = service._transform_all_to_response_model(valid_vo)
        self.assertEqual(response_model.uid, "Milestone_000001")
        self.assertEqual(response_model.study_uid, "Study_000001")

        # Missing UID
        invalid_vo_no_uid = StudyDiseaseMilestoneVO(
            uid=None,
            study_uid="Study_000001",
            order=1,
            status=StudyStatus.DRAFT,
            start_date=datetime.datetime.now(datetime.timezone.utc),
            author_id="test_user",
            author_username="test_username",
            disease_milestone_type="Disease_Milestone_Type_0001",
            disease_milestone_type_name="Type 1",
            disease_milestone_type_definition="Def 1",
            repetition_indicator=True,
        )
        with self.assertRaises(ValidationException) as context:
            service._transform_all_to_response_model(invalid_vo_no_uid)
        self.assertIn("Milestone UID is missing or corrupt", str(context.exception))

        # Empty/corrupt UID
        invalid_vo_empty_uid = StudyDiseaseMilestoneVO(
            uid="",
            study_uid="Study_000001",
            order=1,
            status=StudyStatus.DRAFT,
            start_date=datetime.datetime.now(datetime.timezone.utc),
            author_id="test_user",
            author_username="test_username",
            disease_milestone_type="Disease_Milestone_Type_0001",
            disease_milestone_type_name="Type 1",
            disease_milestone_type_definition="Def 1",
            repetition_indicator=True,
        )
        with self.assertRaises(ValidationException) as context:
            service._transform_all_to_response_model(invalid_vo_empty_uid)
        self.assertIn("Milestone UID is missing or corrupt", str(context.exception))

        # Missing study_uid
        invalid_vo_no_study_uid = StudyDiseaseMilestoneVO(
            uid="Milestone_000001",
            study_uid=None,
            order=1,
            status=StudyStatus.DRAFT,
            start_date=datetime.datetime.now(datetime.timezone.utc),
            author_id="test_user",
            author_username="test_username",
            disease_milestone_type="Disease_Milestone_Type_0001",
            disease_milestone_type_name="Type 1",
            disease_milestone_type_definition="Def 1",
            repetition_indicator=True,
        )
        with self.assertRaises(ValidationException) as context:
            service._transform_all_to_response_model(invalid_vo_no_study_uid)
        self.assertIn("Study UID is missing or corrupt", str(context.exception))

    @patch("clinical_mdr_api.services.studies.study_disease_milestone.MetaRepository")
    @patch("clinical_mdr_api.services.studies.study_disease_milestone.user")
    @patch("clinical_mdr_api.services.studies.study_disease_milestone.UserInfoService.get_author_username_from_id")
    def test_validate_update_skips_redundant_query(self, mock_get_username, mock_user, mock_meta_repo):
        mock_get_username.return_value = "test_username"
        mock_user.return_value.id.return_value = "test_user"
        mock_repo = MagicMock()
        mock_repo.create_ctlist_definition.return_value = {
            "Disease_Milestone_Type_0001": {"name": "Type 1", "definition": "Def 1"}
        }
        mock_meta_repo.return_value.study_disease_milestone_repository = mock_repo

        service = StudyDiseaseMilestoneService()

        # Setup StudyDiseaseMilestoneType dictionary for validation (must be done after service instantiation)
        StudyDiseaseMilestoneType.clear()
        StudyDiseaseMilestoneType["Disease_Milestone_Type_0001"] = DiseaseMilestoneTypeNamedTuple(
            name="Disease_Milestone_Type_0001",
            value=TypeNameDefinition(named="Type 1", definition="Def 1")
        )
        StudyDiseaseMilestoneType["Disease_Milestone_Type_0002"] = DiseaseMilestoneTypeNamedTuple(
            name="Disease_Milestone_Type_0002",
            value=TypeNameDefinition(named="Type 2", definition="Def 2")
        )

        # Existing VO
        existing_vo = StudyDiseaseMilestoneVO(
            uid="Milestone_000001",
            study_uid="Study_000001",
            order=1,
            status=StudyStatus.DRAFT,
            start_date=datetime.datetime.now(datetime.timezone.utc),
            author_id="test_user",
            author_username="test_username",
            disease_milestone_type="Disease_Milestone_Type_0001",
            disease_milestone_type_name="Type 1",
            disease_milestone_type_definition="Def 1",
            repetition_indicator=True,
        )

        # 1. Update with no type change (type is None in partial update)
        edit_input_no_type_change = StudyDiseaseMilestoneEditInput(
            disease_milestone_type=None,
            repetition_indicator=False,
        )
        service._validate_update(edit_input_no_type_change, existing_vo)
        # Verify find_all_disease_milestones_by_study was NOT called
        mock_repo.find_all_disease_milestones_by_study.assert_not_called()

        # 2. Update with identical type (no change)
        edit_input_same_type = StudyDiseaseMilestoneEditInput(
            disease_milestone_type="Disease_Milestone_Type_0001",
            repetition_indicator=False,
        )
        service._validate_update(edit_input_same_type, existing_vo)
        mock_repo.find_all_disease_milestones_by_study.assert_not_called()

        # 3. Update with a different type (should trigger validation and database query)
        edit_input_diff_type = StudyDiseaseMilestoneEditInput(
            disease_milestone_type="Disease_Milestone_Type_0002",
            repetition_indicator=False,
        )
        mock_repo.find_all_disease_milestones_by_study.return_value = []
        service._validate_update(edit_input_diff_type, existing_vo)
        mock_repo.find_all_disease_milestones_by_study.assert_called_once_with(
            study_uid="Study_000001"
        )


@patch("clinical_mdr_api.services.studies.study_disease_milestone.UserInfoService.get_author_username_from_id")
@patch("clinical_mdr_api.services.studies.study_disease_milestone.user")
@patch("clinical_mdr_api.services.studies.study_disease_milestone.MetaRepository")
def test_find_by_uid_scopes_to_study(mock_meta_repo_cls, mock_user, mock_get_username):
    # Setup mocks
    mock_get_username.return_value = "author_username_1"
    mock_user.return_value.id.return_value = "author_1"
    mock_repo = MagicMock()
    mock_meta_repo_cls.return_value.study_disease_milestone_repository = mock_repo
    
    mock_repo.create_ctlist_definition.return_value = {}
    
    service = StudyDiseaseMilestoneService()
    
    # Mock find_by_uid returning a dummy VO
    mock_vo = MagicMock()
    mock_vo.uid = "milestone_123"
    mock_vo.study_uid = "study_abc"
    mock_vo.order = 1
    mock_vo.status.value = "DRAFT"
    mock_vo.start_date = datetime.datetime.now()
    mock_vo.author_id = "author_1"
    mock_vo.disease_milestone_type = "dm_type_1"
    mock_vo.disease_milestone_type_name = "DM Type 1"
    mock_vo.disease_milestone_type_definition = "DM Type 1 Def"
    mock_vo.repetition_indicator = False
    
    mock_repo.find_by_uid.return_value = mock_vo
    
    # Call service
    service.find_by_uid("milestone_123", study_uid="study_abc")
    
    # Assert repository find_by_uid was called with study_uid
    mock_repo.find_by_uid.assert_called_once_with(uid="milestone_123", study_uid="study_abc")


@patch("clinical_mdr_api.services.studies.study_disease_milestone.user")
@patch("clinical_mdr_api.services.studies.study_disease_milestone.MetaRepository")
def test_find_by_uid_not_found_raises_not_found_exception(mock_meta_repo_cls, mock_user):
    # Setup mocks
    mock_user.return_value.id.return_value = "author_1"
    mock_repo = MagicMock()
    mock_meta_repo_cls.return_value.study_disease_milestone_repository = mock_repo
    
    mock_repo.create_ctlist_definition.return_value = {}
    mock_repo.find_by_uid.side_effect = NotFoundException("Study Disease Milestone", "milestone_123")
    
    service = StudyDiseaseMilestoneService()
    
    # Expect NotFoundException (which maps to 404)
    with pytest.raises(NotFoundException):
        service.find_by_uid("milestone_123", study_uid="study_abc")


@patch("clinical_mdr_api.services.studies.study_disease_milestone.user")
@patch("clinical_mdr_api.services.studies.study_disease_milestone.MetaRepository")
@patch("clinical_mdr_api.services.studies.study_disease_milestone.acquire_write_lock_study_value")
def test_edit_validates_milestone_belongs_to_study_before_locking(
    mock_acquire_lock, mock_meta_repo_cls, mock_user
):
    # Setup mocks
    mock_user.return_value.id.return_value = "author_1"
    mock_repo = MagicMock()
    mock_meta_repo_cls.return_value.study_disease_milestone_repository = mock_repo
    
    mock_repo.create_ctlist_definition.return_value = {}
    
    # If the milestone doesn't belong to the study, repo find_by_uid raises NotFoundException
    mock_repo.find_by_uid.side_effect = NotFoundException("Study Disease Milestone", "milestone_123")
    
    service = StudyDiseaseMilestoneService()
    edit_input = StudyDiseaseMilestoneEditInput()
    
    # Expect NotFoundException
    with pytest.raises(NotFoundException):
        service.edit("study_abc", "milestone_123", edit_input)
        
    # Verify find_by_uid was called first, and acquire_write_lock_study_value was never called!
    mock_repo.find_by_uid.assert_called_once_with(uid="milestone_123", study_uid="study_abc")
    mock_acquire_lock.assert_not_called()


@patch("clinical_mdr_api.services.studies.study_disease_milestone.user")
@patch("clinical_mdr_api.services.studies.study_disease_milestone.MetaRepository")
@patch("clinical_mdr_api.services.studies.study_disease_milestone.acquire_write_lock_study_value")
def test_delete_validates_milestone_belongs_to_study_before_locking(
    mock_acquire_lock, mock_meta_repo_cls, mock_user
):
    # Setup mocks
    mock_user.return_value.id.return_value = "author_1"
    mock_repo = MagicMock()
    mock_meta_repo_cls.return_value.study_disease_milestone_repository = mock_repo
    
    mock_repo.create_ctlist_definition.return_value = {}
    mock_repo.find_by_uid.side_effect = NotFoundException("Study Disease Milestone", "milestone_123")
    
    service = StudyDiseaseMilestoneService()
    
    with pytest.raises(NotFoundException):
        service.delete("study_abc", "milestone_123")
        
    mock_repo.find_by_uid.assert_called_once_with(uid="milestone_123", study_uid="study_abc")
    mock_acquire_lock.assert_not_called()


@patch("clinical_mdr_api.services.studies.study_disease_milestone.user")
@patch("clinical_mdr_api.services.studies.study_disease_milestone.MetaRepository")
@patch("clinical_mdr_api.services.studies.study_disease_milestone.acquire_write_lock_study_value")
def test_reorder_validates_milestone_belongs_to_study_before_locking(
    mock_acquire_lock, mock_meta_repo_cls, mock_user
):
    # Setup mocks
    mock_user.return_value.id.return_value = "author_1"
    mock_repo = MagicMock()
    mock_meta_repo_cls.return_value.study_disease_milestone_repository = mock_repo
    
    mock_repo.create_ctlist_definition.return_value = {}
    mock_repo.find_by_uid.side_effect = NotFoundException("Study Disease Milestone", "milestone_123")
    
    service = StudyDiseaseMilestoneService()
    
    with pytest.raises(NotFoundException):
        service.reorder("study_abc", "milestone_123", new_order=2)
        
    mock_repo.find_by_uid.assert_called_once_with(uid="milestone_123", study_uid="study_abc")
    mock_acquire_lock.assert_not_called()


@patch("clinical_mdr_api.services.studies.study_disease_milestone.user")
@patch("clinical_mdr_api.services.studies.study_disease_milestone.MetaRepository")
def test_distinct_headers_scopes_by_study(mock_meta_repo_cls, mock_user):
    # Setup mocks
    mock_user.return_value.id.return_value = "author_1"
    mock_repo = MagicMock()
    mock_meta_repo_cls.return_value.study_disease_milestone_repository = mock_repo
    
    mock_repo.create_ctlist_definition.return_value = {}
    
    service = StudyDiseaseMilestoneService()
    
    # Call get_distinct_values_for_header
    service.get_distinct_values_for_header(
        field_name="status",
        study_uid="study_abc",
        study_value_version="v1.0.0",
        search_string="test",
        filter_by=None,
    )
    
    # Verify repo distinct headers is called with study parameters
    mock_repo.get_distinct_headers.assert_called_once_with(
        field_name="status",
        study_uid="study_abc",
        study_value_version="v1.0.0",
        search_string="test",
        filter_by=None,
        filter_operator=FilterOperator.AND,
        page_size=10,
    )
