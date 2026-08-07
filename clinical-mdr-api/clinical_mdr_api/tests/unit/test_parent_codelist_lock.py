from unittest.mock import MagicMock, patch
import pytest

from clinical_mdr_api.services.controlled_terminologies.ct_term import CTTermService
from clinical_mdr_api.services.controlled_terminologies.ct_codelist import CTCodelistService
from clinical_mdr_api.domain_repositories.controlled_terminologies.ct_codelist_generic_repository import CTCodelistGenericRepository
from clinical_mdr_api.models.controlled_terminologies.ct_term import CTTermCreateInput, CTTermCodelistInput

@pytest.fixture(autouse=True)
def mock_neomodel_db():
    with patch("neomodel.db.begin") as mock_begin, \
         patch("neomodel.db.commit") as mock_commit, \
         patch("neomodel.db.rollback") as mock_rollback:
        yield

@patch("clinical_mdr_api.services.controlled_terminologies.ct_term.user")
@patch("clinical_mdr_api.services.controlled_terminologies.ct_term.MetaRepository")
@patch("clinical_mdr_api.services.controlled_terminologies.ct_term.is_library_editable", return_value=True)
def test_ct_term_service_create_acquires_lock(mock_is_editable, mock_meta_repo_cls, mock_user):
    mock_user_inst = MagicMock()
    mock_user_inst.id.return_value = "author1"
    mock_user.return_value = mock_user_inst

    mock_meta_repo = MagicMock()
    mock_meta_repo_cls.return_value = mock_meta_repo

    mock_attrs_ar = MagicMock()
    mock_attrs_ar.item_metadata.status = "APPROVED"
    mock_attrs_ar.ct_codelist_vo.extensible = True
    mock_attrs_ar.ct_codelist_vo.is_ordinal = False
    mock_meta_repo.ct_codelist_attribute_repository.find_by_uid.return_value = mock_attrs_ar

    mock_meta_repo.library_repository.library_exists.return_value = True
    mock_meta_repo.ct_term_attributes_repository.entity_exists_by_concept_id.return_value = False
    mock_meta_repo.ct_catalogue_repository.catalogue_exists.return_value = True

    service = CTTermService()
    
    term_input = CTTermCreateInput(
        catalogue_names=["SDTM CT"],
        codelists=[
            CTTermCodelistInput(
                codelist_uid="CL123",
                submission_value="VAL1",
                order=1
            )
        ],
        nci_preferred_name="PT",
        definition="PT def",
        sponsor_preferred_name="PT name",
        sponsor_preferred_name_sentence_case="Pt name",
        library_name="Sponsor"
    )

    with patch("clinical_mdr_api.services.controlled_terminologies.ct_term.CTTermAttributesAR") as mock_attr_ar_cls, \
         patch("clinical_mdr_api.services.controlled_terminologies.ct_term.CTTermNameAR") as mock_name_ar_cls, \
         patch("clinical_mdr_api.services.controlled_terminologies.ct_term.CTTerm") as mock_term_cls:
        
        mock_attr_ar_inst = MagicMock()
        mock_attr_ar_inst.uid = "term_uid_123"
        mock_attr_ar_cls.from_input_values.return_value = mock_attr_ar_inst

        mock_name_ar_inst = MagicMock()
        mock_name_ar_cls.from_input_values.return_value = mock_name_ar_inst

        service.create(term_input)

    mock_meta_repo.ct_codelist_attribute_repository.find_by_uid.assert_called_with(
        codelist_uid="CL123",
        for_update=True
    )


@patch("clinical_mdr_api.services.controlled_terminologies.ct_codelist.user")
@patch("clinical_mdr_api.services.controlled_terminologies.ct_codelist.MetaRepository")
def test_ct_codelist_service_add_term_acquires_lock(mock_meta_repo_cls, mock_user):
    mock_user_inst = MagicMock()
    mock_user_inst.id.return_value = "author1"
    mock_user.return_value = mock_user_inst

    mock_meta_repo = MagicMock()
    mock_meta_repo_cls.return_value = mock_meta_repo

    mock_attrs_ar = MagicMock()
    mock_attrs_ar.library.is_editable = True
    mock_attrs_ar.ct_codelist_vo.extensible = True
    mock_attrs_ar.ct_codelist_vo.is_ordinal = False
    mock_attrs_ar.ct_codelist_vo.parent_codelist_uid = None
    mock_meta_repo.ct_codelist_attribute_repository.find_by_uid.return_value = mock_attrs_ar
    mock_meta_repo.ct_codelist_aggregated_repository.get_paired_codelist_uids.return_value = (None, None)
    mock_meta_repo.ct_term_name_repository.is_library_editable_for_term.return_value = True
    mock_meta_repo.ct_term_name_repository.get_submission_values_for_term.return_value = ["VAL1"]

    service = CTCodelistService()
    
    with patch("clinical_mdr_api.services.controlled_terminologies.ct_codelist.CTCodelist") as mock_codelist_cls:
        service.add_term(
            codelist_uid="CL123",
            term_uid="T123",
            order=1,
            submission_value="VAL1"
        )

    mock_meta_repo.ct_codelist_attribute_repository.find_by_uid.assert_called_with(
        codelist_uid="CL123",
        for_update=True
    )


@patch("clinical_mdr_api.services.controlled_terminologies.ct_codelist.user")
@patch("clinical_mdr_api.services.controlled_terminologies.ct_codelist.MetaRepository")
def test_ct_codelist_service_remove_term_acquires_lock(mock_meta_repo_cls, mock_user):
    mock_user_inst = MagicMock()
    mock_user_inst.id.return_value = "author1"
    mock_user.return_value = mock_user_inst

    mock_meta_repo = MagicMock()
    mock_meta_repo_cls.return_value = mock_meta_repo

    mock_attrs_ar = MagicMock()
    mock_attrs_ar.library.is_editable = True
    mock_attrs_ar.ct_codelist_vo.extensible = True
    mock_attrs_ar.ct_codelist_vo.child_codelist_uids = []
    mock_meta_repo.ct_codelist_attribute_repository.find_by_uid.return_value = mock_attrs_ar
    mock_meta_repo.ct_codelist_aggregated_repository.get_paired_codelist_uids.return_value = (None, None)

    service = CTCodelistService()
    
    with patch("clinical_mdr_api.services.controlled_terminologies.ct_codelist.CTCodelist") as mock_codelist_cls:
        service.remove_term(
            codelist_uid="CL123",
            term_uid="T123"
        )

    mock_meta_repo.ct_codelist_attribute_repository.find_by_uid.assert_called_with(
        codelist_uid="CL123",
        for_update=True
    )


@patch("clinical_mdr_api.domain_repositories.controlled_terminologies.ct_codelist_generic_repository.CTCodelistRoot")
@patch("clinical_mdr_api.domain_repositories.controlled_terminologies.ct_codelist_generic_repository.CTTermRoot")
@patch("clinical_mdr_api.domain_repositories.controlled_terminologies.ct_codelist_generic_repository.TemplateParameterTermRoot")
def test_repository_add_term_acquires_lock(mock_param_term_root, mock_term_root, mock_codelist_root):
    mock_codelist_node = MagicMock()
    mock_codelist_root.nodes.get_or_none.return_value = mock_codelist_node

    mock_term_node = MagicMock()
    mock_term_root.nodes.get_or_none.return_value = mock_term_node

    class DummyRepo(CTCodelistGenericRepository):
        root_class = mock_codelist_root
        value_class = MagicMock()
        relationship_from_root = "has_attributes_root"
        
        def _create_aggregate_root_instance_from_cypher_result(self, codelist_dict):
            pass
        def _create_aggregate_root_instance_from_version_root_relationship_and_value(self, root, library, relationship, value, **_kwargs):
            pass
        def _maintain_parameters(self, versioned_object, root, value):
            pass
        def is_repository_related_to_attributes(self):
            return True

    repo = DummyRepo()
    repo._lock_object2 = MagicMock()

    with patch("clinical_mdr_api.domain_repositories.controlled_terminologies.ct_codelist_generic_repository.db") as mock_db, \
         patch("clinical_mdr_api.domain_repositories.controlled_terminologies.ct_codelist_generic_repository.is_codelist_in_final", return_value=True), \
         patch("clinical_mdr_api.domain_repositories.controlled_terminologies.ct_codelist_generic_repository.CTCodelistTerm") as mock_codelist_term_cls:
        
        mock_db.cypher_query.return_value = ([], MagicMock())

        repo.add_term(
            codelist_uid="CL123",
            term_uid="T123",
            author_id="author1",
            order=1,
            submission_value="VAL1"
        )

    repo._lock_object2.assert_called_with("CL123")
