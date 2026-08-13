import datetime
import unittest
from unittest import mock
from dataclasses import replace

from clinical_mdr_api.domains.versioned_object_aggregate import LibraryItemMetadataVO, LibraryItemStatus, LibraryVO
from clinical_mdr_api.domains.syntax_templates.template import TemplateVO, TemplateAggregateRootBase
from clinical_mdr_api.domains.libraries.object import ParametrizedTemplateVO, ParametrizedTemplateARBase
from clinical_mdr_api.services.syntax_templates.generic_syntax_template_service import GenericSyntaxTemplateService
from pydantic import BaseModel


class DummyPydanticModel(BaseModel):
    uid: str
    version: str
    status: str


class MockTemplateAR(TemplateAggregateRootBase):
    pass


class MockPreInstanceAR(ParametrizedTemplateARBase):
    pass


class DummyTemplateService(GenericSyntaxTemplateService):
    aggregate_class = MockTemplateAR
    version_class = DummyPydanticModel
    repository_interface = mock.MagicMock()
    instance_repository_interface = mock.MagicMock()
    pre_instance_repository_interface = mock.MagicMock()

    def __init__(self, author_id="test-author"):
        self.author_id = author_id
        self._repos = mock.MagicMock()

    def _transform_aggregate_root_to_pydantic_model(self, item_ar):
        return DummyPydanticModel(
            uid=item_ar.uid,
            version=item_ar.item_metadata.version,
            status=item_ar.item_metadata.status.value,
        )

    def create(self, template):
        pass

    def edit_draft(self, uid, template):
        pass


class TestReactivationService(unittest.TestCase):
    def test_reactivate_retired_service_logic(self):
        # given
        service = DummyTemplateService()
        mock_template_repo = mock.MagicMock()
        mock_pre_instance_repo = mock.MagicMock()

        # Wire repositories
        type(service).repository = mock_template_repo
        type(service).pre_instance_repository = mock_pre_instance_repo

        # Create old retired template
        old_template_vo = TemplateVO.from_repository_values(
            template_name="Old Template",
            template_name_plain="Old Template",
        )
        old_library_vo = LibraryVO.from_repository_values(
            library_name="Global Library",
            is_editable=True,
        )
        old_metadata = LibraryItemMetadataVO.from_repository_values(
            change_description="Retired template",
            status=LibraryItemStatus.RETIRED,
            author_id="test-author",
            author_username="test-user",
            start_date=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1),
            end_date=None,
            major_version=1,
            minor_version=0,
        )
        retired_template = MockTemplateAR.from_repository_values(
            uid="old-template-uid",
            sequence_id="old-template-seq",
            template=old_template_vo,
            library=old_library_vo,
            item_metadata=old_metadata,
        )

        mock_template_repo.find_by_uid.return_value = retired_template
        mock_template_repo.generate_uid_callback.return_value = "new-template-uid"
        mock_template_repo.next_available_sequence_id.return_value = "new-template-seq"

        # Create old retired pre-instance
        old_param_template_vo = ParametrizedTemplateVO.from_repository_values(
            template_name="Old Template",
            template_uid="old-template-uid",
            template_sequence_id="old-template-seq",
            parameter_terms=[],
            library_name="Global Library",
        )
        old_pre_instance_metadata = LibraryItemMetadataVO.from_repository_values(
            change_description="Retired pre-instance",
            status=LibraryItemStatus.RETIRED,
            author_id="test-author",
            author_username="test-user",
            start_date=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1),
            end_date=None,
            major_version=1,
            minor_version=0,
        )
        retired_pre_instance = MockPreInstanceAR.from_repository_values(
            uid="old-pre-uid",
            sequence_id="old-pre-seq",
            template=old_param_template_vo,
            library=old_library_vo,
            item_metadata=old_pre_instance_metadata,
        )

        mock_pre_instance_repo.find_pre_instance_uids_by_template_uid.return_value = ["old-pre-uid"]
        mock_pre_instance_repo.find_by_uid.return_value = retired_pre_instance
        mock_pre_instance_repo.generate_uid_callback.return_value = "new-pre-uid"
        mock_pre_instance_repo.next_available_sequence_id.return_value = "new-pre-seq"

        # when
        with mock.patch("neomodel.db.begin"), \
             mock.patch("neomodel.db.commit"), \
             mock.patch("neomodel.db.rollback"):
            result = service.reactivate_retired("old-template-uid")

        # then
        # 1. Old retired template's end_date should be closed (non-None) and it should be saved
        self.assertIsNotNone(retired_template.item_metadata.end_date)
        mock_template_repo.save.assert_any_call(retired_template)

        # 2. New template should be saved as FINAL with version 2.0 and new UID
        saved_items = [args[0] for args, _ in mock_template_repo.save.call_args_list]
        new_saved_templates = [x for x in saved_items if x.uid == "new-template-uid"]
        self.assertEqual(len(new_saved_templates), 1)
        new_template = new_saved_templates[0]
        self.assertEqual(new_template.item_metadata.status, LibraryItemStatus.FINAL)
        self.assertEqual(new_template.item_metadata.version, "2.0")
        self.assertIsNone(new_template.item_metadata.end_date)

        # 3. Old pre-instance's end_date should be closed and saved
        self.assertIsNotNone(retired_pre_instance.item_metadata.end_date)
        mock_pre_instance_repo.save.assert_any_call(retired_pre_instance)

        # 4. New pre-instance should be saved referencing the new template
        saved_pre_items = [args[0] for args, _ in mock_pre_instance_repo.save.call_args_list]
        new_saved_pre_instances = [x for x in saved_pre_items if x.uid == "new-pre-uid"]
        self.assertEqual(len(new_saved_pre_instances), 1)
        new_pre_instance = new_saved_pre_instances[0]
        self.assertEqual(new_pre_instance.item_metadata.status, LibraryItemStatus.FINAL)
        self.assertEqual(new_pre_instance.item_metadata.version, "2.0")
        self.assertIsNone(new_pre_instance.item_metadata.end_date)
        # Point to the newly reactivated template
        self.assertEqual(new_pre_instance.template_uid, "new-template-uid")
        self.assertEqual(new_pre_instance.template_sequence_id, "new-template-seq")

        # 5. Result model should represent the new template
        self.assertEqual(result.uid, "new-template-uid")
        self.assertEqual(result.version, "2.0")
        self.assertEqual(result.status, "Final")
