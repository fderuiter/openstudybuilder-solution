import pytest
from pydantic import ValidationError
from clinical_mdr_api.clinical_mdr_api.models.integrations.msgraph import GraphUser

def test_submodule_import():
    # Verify that the migration suite can import model definitions directly from the API submodule path
    assert GraphUser is not None

def test_pydantic_v2_parsing_and_validation():
    # Verify that GraphUser can parse and validate user payloads using the updated Pydantic v2 syntax
    payload = {
        "id": "user-uuid-12345678",
        "displayName": "Jules Verifier",
        "givenName": "Jules",
        "mail": "jules@novonordisk.com",
        "surname": "Verifier"
    }
    
    user = GraphUser.model_validate(payload)
    assert user.id == "user-uuid-12345678"
    assert user.display_name == "Jules Verifier"
    assert user.given_name == "Jules"
    assert user.email == "jules@novonordisk.com"
    assert user.surname == "Verifier"

def test_pydantic_v2_validation_error():
    # Missing required field "id"
    invalid_payload = {
        "displayName": "Invalid User"
    }
    
    with pytest.raises(ValidationError):
        GraphUser.model_validate(invalid_payload)
