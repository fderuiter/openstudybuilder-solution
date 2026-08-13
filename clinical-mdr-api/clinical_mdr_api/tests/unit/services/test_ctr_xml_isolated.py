import unittest
from unittest import mock
from datetime import datetime, timezone
from clinical_mdr_api.services.ctr_xml.ctr_xml_service import ODMBuilder
from clinical_mdr_api.models.odms.form import OdmForm
from clinical_mdr_api.models.odms.item_group import OdmItemGroup, OdmItemGroupRefModel
from clinical_mdr_api.models.odms.item import OdmItem, OdmItemRefModel
from clinical_mdr_api.models.odms.common_models import (
    OdmTranslatedTextModel,
    OdmAliasModel,
    OdmRefVendor,
)
from clinical_mdr_api.models.controlled_terminologies.ct_codelist_attributes import (
    CTCodelistAttributes,
    CTCodelistAttributesSimpleModel,
)


class TestCtrXmlIsolated(unittest.TestCase):
    @mock.patch("clinical_mdr_api.domain_repositories.odms.form_repository.FormRepository.get_hydrated_forms_by_study")
    def test_odm_builder_isolated(self, mock_get_hydrated):
        # 1. Setup mock return data for our study-isolated unified repository query
        now_dt = datetime.now(timezone.utc)
        mock_data = {
            "forms": [
                OdmForm(
                    uid="form_1",
                    oid="OID_FORM_1",
                    name="Form 1",
                    repeating="No",
                    sdtm_version="1.0",
                    library_name="Sponsor",
                    start_date=now_dt,
                    end_date=None,
                    status="Final",
                    version="1.0",
                    change_description="Initial form description",
                    author_username="test_user",
                    translated_texts=[OdmTranslatedTextModel(text_type="Description", language="en", text="Form 1 Description")],
                    aliases=[OdmAliasModel(name="alias1", context="context1")],
                    item_groups=[
                        OdmItemGroupRefModel(
                            uid="ig_1",
                            oid="OID_IG_1",
                            name="Item Group 1",
                            version="1.0",
                            order_number=1,
                            mandatory="Yes",
                            collection_exception_condition_oid="cond1",
                            vendor=OdmRefVendor(attributes=[])
                        )
                    ],
                    vendor_elements=[],
                    vendor_attributes=[],
                    vendor_element_attributes=[],
                    possible_actions=[]
                )
            ],
            "item_groups": [
                OdmItemGroup(
                    uid="ig_1",
                    oid="OID_IG_1",
                    name="Item Group 1",
                    repeating="Yes",
                    is_reference_data="No",
                    sas_dataset_name="IG1",
                    origin="Sponsor",
                    purpose="Analysis",
                    comment="Comment 1",
                    library_name="Sponsor",
                    start_date=now_dt,
                    end_date=None,
                    status="Final",
                    version="1.0",
                    change_description="Initial ig description",
                    author_username="test_user",
                    translated_texts=[],
                    aliases=[],
                    sdtm_domains=[],
                    items=[
                        OdmItemRefModel(
                            uid="item_1",
                            oid="OID_ITEM_1",
                            name="Item 1",
                            version="1.0",
                            order_number=1,
                            mandatory="Yes",
                            collection_exception_condition_oid=None,
                            method_oid=None,
                            role=None,
                            role_codelist_oid=None,
                            vendor=OdmRefVendor(attributes=[])
                        )
                    ],
                    vendor_elements=[],
                    vendor_attributes=[],
                    vendor_element_attributes=[],
                    possible_actions=[]
                )
            ],
            "items": [
                OdmItem(
                    uid="item_1",
                    oid="OID_ITEM_1",
                    name="Item 1",
                    datatype="text",
                    length=10,
                    significant_digits=None,
                    sas_field_name="IT1",
                    sds_var_name="IT1",
                    origin="Sponsor",
                    comment="Comment 2",
                    prompt="Prompt 1",
                    library_name="Sponsor",
                    start_date=now_dt,
                    end_date=None,
                    status="Final",
                    version="1.0",
                    change_description="Initial item description",
                    author_username="test_user",
                    translated_texts=[],
                    aliases=[],
                    unit_definitions=[],
                    codelist=CTCodelistAttributesSimpleModel(
                        uid="codelist_1",
                        name="Codelist 1",
                        datatype="text",
                        submission_value="CL1",
                        extensible=True,
                        is_ordinal=False,
                        allows_multi_choice=True
                    ),
                    terms=[],
                    activity_instances=[],
                    vendor_elements=[],
                    vendor_attributes=[],
                    vendor_element_attributes=[],
                    possible_actions=[]
                )
            ],
            "codelists": [
                CTCodelistAttributes(
                    codelist_uid="codelist_1",
                    name="Codelist 1",
                    submission_value="CL1",
                    definition="Codelist 1 Definition",
                    extensible=True,
                    is_ordinal=False,
                    catalogue_names=[],
                    child_codelist_uids=[],
                    library_name="Sponsor",
                    start_date=now_dt,
                    end_date=None,
                    status="Final",
                    version="1.0",
                    change_description="Codelist change",
                    author_username="test_user",
                    possible_actions=[]
                )
            ]
        }
        mock_get_hydrated.return_value = mock_data

        # 2. Mock ODMBuilder internal service dependency properties
        builder = ODMBuilder("study_123")
        
        # Mock Project
        mock_project = mock.MagicMock()
        mock_project.name = "Project ABC"
        mock_project.project_number = "123"
        mock_project.start_date = now_dt
        mock_project.status = "Final"
        mock_project.version = "1.0"
        mock_project.author_username = "test_user"
        mock_project.possible_actions = []
        builder.__dict__["project"] = mock_project

        # Mock StudyMetadata
        mock_metadata = mock.MagicMock()
        mock_metadata.identification_metadata.study_number = "study_123"
        mock_metadata.identification_metadata.study_id = "study_id_123"
        mock_metadata.identification_metadata.protocol_title = "Protocol Title"
        mock_metadata.identification_metadata.study_name = "Study Name"

        mock_metadata.version_metadata.study_version = "1.0"
        mock_metadata.version_metadata.version_timestamp = now_dt
        mock_metadata.version_metadata.version_number = 1
        mock_metadata.version_metadata.study_status = "Approved"
        mock_metadata.version_metadata.version_description = "Initial Version"
        
        mock_metadata.study_description.study_short_title = "Short Title"
        mock_metadata.study_description.study_title = "Detailed Title"

        mock_metadata.study_population.healthy_subjects_only = False
        mock_metadata.study_intervention.intervention_type = None

        builder.__dict__["study_metadata"] = mock_metadata

        # Mock StudyVisit
        mock_visit = mock.MagicMock()
        mock_visit.uid = "visit_1"
        mock_visit.visit_name = "Screening"
        mock_visit.visit_type.sponsor_preferred_name = "Visit Type 1"
        mock_visit.study_epoch.sponsor_preferred_name = "Epoch 1"
        builder.__dict__["study_visits"] = [mock_visit]

        # 3. Call get_odm and assert correctness
        odm = builder.get_odm()
        self.assertIsNotNone(odm)
        self.assertEqual(len(odm.study), 1)
        self.assertEqual(odm.study[0].oid, "study_id_123")
        self.assertEqual(len(odm.study[0].meta_data_version), 1)
        
        metadata_version = odm.study[0].meta_data_version[0]
        self.assertEqual(len(metadata_version.form_def), 1)
        self.assertEqual(metadata_version.form_def[0].oid, "OID_FORM_1")
        self.assertEqual(metadata_version.form_def[0].name, "Form 1")

        self.assertEqual(len(metadata_version.item_group_def), 1)
        self.assertEqual(metadata_version.item_group_def[0].oid, "OID_IG_1")
        self.assertEqual(metadata_version.item_group_def[0].name, "Item Group 1")

        self.assertEqual(len(metadata_version.item_def), 1)
        self.assertEqual(metadata_version.item_def[0].oid, "OID_ITEM_1")
        self.assertEqual(metadata_version.item_def[0].name, "Item 1")

        self.assertEqual(len(metadata_version.code_list), 1)
        self.assertEqual(metadata_version.code_list[0].oid, "codelist_1")
        self.assertEqual(metadata_version.code_list[0].name, "Codelist 1")
