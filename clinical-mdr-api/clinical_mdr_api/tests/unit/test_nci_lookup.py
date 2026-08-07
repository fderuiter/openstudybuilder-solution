import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
from clinical_mdr_api.services.integrations.nci import search_nci_concepts
from clinical_mdr_api.models.integrations.nci import NCIConcept

@pytest.mark.asyncio
async def test_search_nci_concepts_success():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.json = MagicMock(return_value={
        "concepts": [
            {"code": "C123", "name": "Concept Name 1"},
            {"code": "C456", "preferredName": "Concept Name 2"},
            {"code": "C789"} # should be ignored because name is missing
        ]
    })
    
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        results = await search_nci_concepts("test_term")
        
        mock_get.assert_called_once()
        assert len(results) == 2
        assert results[0].code == "C123"
        assert results[0].name == "Concept Name 1"
        assert results[1].code == "C456"
        assert results[1].name == "Concept Name 2"

@pytest.mark.asyncio
async def test_search_nci_concepts_http_error():
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.HTTPError("Connection failed")
        with pytest.raises(httpx.HTTPError):
            await search_nci_concepts("test_term")
