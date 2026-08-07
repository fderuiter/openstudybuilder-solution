import pytest
from unittest.mock import MagicMock, patch
from clinical_mdr_api.services.studies.study_interventions import StudyInterventionsService

def test_mk_table_offline():
    # Setup mock compound
    mock_compound = MagicMock()
    mock_compound.study_compound_uid = "comp_1"
    
    # Mock compound basic attributes
    mock_compound.compound.name = "Test Compound Name"
    mock_compound.type_of_treatment.term_name = "Test Treatment Type"
    
    # Mock delivery device and dispenser as SimpleCodelistTermModel
    mock_device = MagicMock()
    mock_device.term_name = "Device 1"
    mock_compound.delivery_device = mock_device
    
    mock_dispenser = MagicMock()
    mock_dispenser.term_name = "Dispenser 1"
    mock_compound.dispenser = mock_dispenser
    mock_compound.dispensed_in = None
    
    mock_compound.other_info = "Take with water"
    
    # Mock dose frequency
    mock_freq = MagicMock()
    mock_freq.term_name = "BID"
    mock_compound.dose_frequency = mock_freq
    
    # Setup mock pharmaceutical products in medicinal_product
    mock_med_prod = MagicMock()
    mock_pp_simple = MagicMock()
    mock_pp_simple.uid = "pp_1"
    mock_med_prod.pharmaceutical_products = [mock_pp_simple]
    mock_compound.medicinal_product = mock_med_prod
    
    compounds = [mock_compound]
    
    # Setup mock arms
    mock_arm = MagicMock()
    mock_arm.name = "Arm A"
    arms = {"comp_1": [mock_arm]}
    
    # Setup mock dosing
    mock_dosing = MagicMock()
    mock_dosing.dose_value.value = 50.0
    mock_dosing.dose_value.unit_label = "mg"
    dosings = {"comp_1": [mock_dosing]}
    
    # Mock PharmaceuticalProductService to return full pp with dosage forms, routes of admin, and strength
    with patch("clinical_mdr_api.services.concepts.pharmaceutical_products_service.PharmaceuticalProductService") as MockServiceClass:
        mock_service = MockServiceClass.return_value
        
        # Mock full pharmaceutical product
        mock_full_pp = MagicMock()
        
        # Dosage forms
        mock_df = MagicMock()
        mock_df.term_name = "Tablet"
        mock_full_pp.dosage_forms = [mock_df]
        
        # Routes of administration
        mock_roa = MagicMock()
        mock_roa.term_name = "Oral"
        mock_full_pp.routes_of_administration = [mock_roa]
        
        # Formulations / Ingredient strength
        mock_ingredient = MagicMock()
        mock_ingredient.strength.value = 5.0
        mock_ingredient.strength.unit_label = "mg/mL"
        mock_formulation = MagicMock()
        mock_formulation.ingredients = [mock_ingredient]
        mock_full_pp.formulations = [mock_formulation]
        
        mock_service.get_by_uid.return_value = mock_full_pp
        
        # Call mk_table
        table = StudyInterventionsService.mk_table(compounds, arms, dosings)
        
        # Assertions
        assert len(table.rows) == 14, "Must have exactly 14 rows"
        
        # Verify columns length (1 header col + 1 compound col)
        for row in table.rows:
            assert len(row.cells) == 2, "Each row must have exactly 2 cells"
            
        # Check specific rows and formatted text
        # Row 0: Intervention/Arm name
        assert table.rows[0].cells[1].text == "Arm A"
        
        # Row 1: Intervention name
        assert table.rows[1].cells[1].text == "Test Compound Name"
        
        # Row 2: Intervention type
        assert table.rows[2].cells[1].text == "Test Treatment Type"
        
        # Row 3: Investigational or non-investigational
        assert table.rows[3].cells[1].text == "Not Specified"
        
        # Row 4: Pharmaceutical form
        assert table.rows[4].cells[1].text == "Tablet"
        
        # Row 5: Route of administration
        assert table.rows[5].cells[1].text == "Oral"
        
        # Row 6: Medical-device (if applicable)
        assert "Device 1" in table.rows[6].cells[1].text
        assert "Dispenser 1" in table.rows[6].cells[1].text
        
        # Row 7: Trial product strength
        assert table.rows[7].cells[1].text == "5 mg/mL"
        
        # Row 8: Dose and dose frequency
        assert "50 mg" in table.rows[8].cells[1].text
        assert "BID" in table.rows[8].cells[1].text
        
        # Row 9: Dosing instructions and administration
        assert table.rows[9].cells[1].text == "Take with water"
        
        # Check other fallback rows
        for i in [10, 11, 12, 13]:
            assert table.rows[i].cells[1].text == "Not Specified"
            
        # Ensure no "?" placeholder in the entire table
        for r_idx, row in enumerate(table.rows):
            for c_idx, cell in enumerate(row.cells):
                assert "?" not in cell.text, f"Found raw question mark in row {r_idx}, col {c_idx}"
