import logging
import httpx
from common.config import settings
from clinical_mdr_api.models.integrations.nci import NCIConcept

log = logging.getLogger(__name__)

async def search_nci_concepts(query: str, page_size: int = 20) -> list[NCIConcept]:
    """
    Query the external NCI EVS API asynchronously to search for concepts.
    Does not run Neo4j/Cypher procedures.
    """
    url = settings.nci_evs_api_url
    params = {
        "terminology": "ncit",
        "term": query,
        "pageSize": page_size
    }
    
    log.info(f"Querying NCI EVS API at {url} with query '{query}'")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            log.error(f"NCI EVS API request failed: {exc}")
            raise exc

        try:
            data = response.json()
        except ValueError as exc:
            log.error(f"Failed to parse NCI EVS API response as JSON: {exc}")
            raise exc

        concepts = []
        if isinstance(data, dict):
            # The API usually returns {"concepts": [...]}
            raw_concepts = data.get("concepts", [])
            for c in raw_concepts:
                code = c.get("code")
                # EVS Concept usually has 'name' or 'preferredName'
                name = c.get("name") or c.get("preferredName") or ""
                if code and name:
                    concepts.append(NCIConcept(code=code, name=name))
        return concepts
