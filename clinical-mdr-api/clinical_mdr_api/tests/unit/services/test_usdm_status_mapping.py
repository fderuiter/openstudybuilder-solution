import unittest
from unittest.mock import MagicMock, patch
from usdm_model import Code as USDMCode, StudyDefinitionDocument, StudyDefinitionDocumentVersion

from clinical_mdr_api.domains.study_definition_aggregates.study_metadata import StudyStatus
from clinical_mdr_api.services.ddf.usdm_mapper import USDMMapper
from common.exceptions import ValidationException


class TestUSDMStatusMapping(unittest.TestCase):
    def setUp(self):
        # Create the mapper with dummy services
        self.mapper = USDMMapper(
            get_osb_study_design_cells=MagicMock(),
            get_osb_study_arms=MagicMock(),
            get_osb_study_epochs=MagicMock(),
            get_osb_study_elements=MagicMock(),
            get_osb_study_endpoints=MagicMock(),
            get_osb_study_visits=MagicMock(),
            get_osb_study_activities=MagicMock(),
            get_osb_activity_schedules=MagicMock(),
        )

    def test_map_released_status_success(self):
        # Arrange
        study = MagicMock()
        version_metadata = MagicMock()
        version_metadata.study_status = "RELEASED"
        version_metadata.version_number = 1
        study.current_metadata.version_metadata = version_metadata

        mock_code = USDMCode(
            id="resolved_id",
            code="C25425",
            codeSystem="CDISC CT",
            codeSystemVersion="2026-08-07",
            decode="Approved",
            instanceType="Code",
        )

        with patch.object(
            self.mapper, "get_ct_package_term_as_usdm_code", return_value=mock_code
        ) as mock_get_term:
            # Act
            doc = self.mapper._get_study_definition_document(study)

            # Assert
            mock_get_term.assert_called_once_with("C25425")
            self.assertIsInstance(doc, StudyDefinitionDocument)
            self.assertEqual(len(doc.versions), 1)
            self.assertEqual(doc.versions[0].status, mock_code)
            self.assertEqual(doc.versions[0].version, "1")

    def test_map_draft_status_success(self):
        # Arrange
        study = MagicMock()
        version_metadata = MagicMock()
        version_metadata.study_status = StudyStatus.DRAFT  # Test enum handling
        version_metadata.version_number = None
        study.current_metadata.version_metadata = version_metadata

        mock_code = USDMCode(
            id="resolved_id_draft",
            code="C85255",
            codeSystem="CDISC CT",
            codeSystemVersion="2026-08-07",
            decode="Draft",
            instanceType="Code",
        )

        with patch.object(
            self.mapper, "get_ct_package_term_as_usdm_code", return_value=mock_code
        ) as mock_get_term:
            # Act
            doc = self.mapper._get_study_definition_document(study)

            # Assert
            mock_get_term.assert_called_once_with("C85255")
            self.assertEqual(doc.versions[0].status, mock_code)
            self.assertEqual(doc.versions[0].version, "DRAFT")

    def test_map_locked_status_success(self):
        # Arrange
        study = MagicMock()
        version_metadata = MagicMock()
        version_metadata.study_status = "LOCKED"
        version_metadata.version_number = 2
        study.current_metadata.version_metadata = version_metadata

        mock_code = USDMCode(
            id="resolved_id_locked",
            code="C25508",
            codeSystem="CDISC CT",
            codeSystemVersion="2026-08-07",
            decode="Final",
            instanceType="Code",
        )

        with patch.object(
            self.mapper, "get_ct_package_term_as_usdm_code", return_value=mock_code
        ) as mock_get_term:
            # Act
            doc = self.mapper._get_study_definition_document(study)

            # Assert
            mock_get_term.assert_called_once_with("C25508")
            self.assertEqual(doc.versions[0].status, mock_code)
            self.assertEqual(doc.versions[0].version, "2")

    def test_unmapped_status_raises_validation_exception(self):
        # Arrange
        study = MagicMock()
        version_metadata = MagicMock()
        version_metadata.study_status = "UNMAPPED_XYZ"
        version_metadata.version_number = 1
        study.current_metadata.version_metadata = version_metadata

        # Act & Assert
        with self.assertRaises(ValidationException) as context:
            self.mapper._get_study_definition_document(study)
        self.assertIn("UNMAPPED_XYZ", str(context.exception))

    def test_null_status_raises_validation_exception(self):
        # Arrange
        study = MagicMock()
        version_metadata = MagicMock()
        version_metadata.study_status = None
        version_metadata.version_number = 1
        study.current_metadata.version_metadata = version_metadata

        # Act & Assert
        with self.assertRaises(ValidationException):
            self.mapper._get_study_definition_document(study)

    def test_void_returned_code_raises_validation_exception(self):
        # Arrange
        study = MagicMock()
        version_metadata = MagicMock()
        version_metadata.study_status = "RELEASED"
        version_metadata.version_number = 1
        study.current_metadata.version_metadata = version_metadata

        void_code = USDMCode(
            id=self.mapper._id_manager.get_id(USDMCode.__name__, "VOID_CODE"),
            code="",
            codeSystem="",
            codeSystemVersion="",
            decode="",
            instanceType="Code",
        )

        with patch.object(
            self.mapper, "get_ct_package_term_as_usdm_code", return_value=void_code
        ) as mock_get_term:
            # Act & Assert
            with self.assertRaises(ValidationException) as context:
                self.mapper._get_study_definition_document(study)
            self.assertIn("could not be resolved", str(context.exception))
