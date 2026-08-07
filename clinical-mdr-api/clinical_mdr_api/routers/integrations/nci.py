from typing import Annotated
from fastapi import APIRouter, Query, HTTPException
from pydantic import StringConstraints
from clinical_mdr_api.models.integrations.nci import NCIConcept
from clinical_mdr_api.services.integrations import nci as nci_service
from clinical_mdr_api.routers import _generic_descriptions
from common.auth import rbac
from common.auth.dependencies import security

router = APIRouter()

@router.get(
    "/nci-lookup",
    dependencies=[security, rbac.ANY],
    summary="Search NCI concepts directly",
    description="Query NCI concepts from external NCI EVS API asynchronously.",
    status_code=200,
    response_model=list[NCIConcept],
    responses={
        403: _generic_descriptions.ERROR_403,
    },
)
async def nci_lookup(
    q: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=3, max_length=255),
        Query(description="Search query (min 3 characters)"),
    ],
) -> list[NCIConcept]:
    try:
        return await nci_service.search_nci_concepts(q)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to query NCI EVS API: {str(exc)}")
