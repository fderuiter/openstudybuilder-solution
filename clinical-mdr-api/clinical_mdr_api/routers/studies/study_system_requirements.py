from typing import Annotated
from fastapi import APIRouter, Body
from neomodel import db
from common.auth import rbac
from common.auth.dependencies import security
from clinical_mdr_api import utils
from clinical_mdr_api.domain_repositories.models.study_selections import (
    SystemBoundary,
    SystemConstraint,
)
from clinical_mdr_api.models.study_selections.study_selection import (
    StudySelectionSystemBoundaryCreateInput,
    StudySelectionSystemConstraintCreateInput,
)
from fastapi import Path

StudyUID = Path(description="The unique id of the study.")

router = APIRouter()


@router.post(
    "/studies/{study_uid}/system-boundaries",
    dependencies=[security, rbac.STUDY_WRITE],
    status_code=201,
    summary="Create a system boundary",
)
def create_system_boundary(
    study_uid: Annotated[str, StudyUID],
    boundary_input: Annotated[StudySelectionSystemBoundaryCreateInput, Body()],
):
    boundary = SystemBoundary(
        uid=utils.generate_uid("SystemBoundary"),
        name=boundary_input.name,
        description=boundary_input.description,
        order=0,
        accepted_version=True,
    ).save()

    query = """
        MATCH (sr:StudyRoot {uid: $study_uid})-[:LATEST]->(sv:StudyValue)
        MATCH (b:SystemBoundary {uid: $boundary_uid})
        MERGE (sv)-[:HAS_SYSTEM_BOUNDARY]->(b)
    """
    db.cypher_query(query, {"study_uid": study_uid, "boundary_uid": boundary.uid})
    return {
        "system_boundary_uid": boundary.uid,
        "name": boundary.name,
        "description": boundary.description,
    }


@router.post(
    "/studies/{study_uid}/system-constraints",
    dependencies=[security, rbac.STUDY_WRITE],
    status_code=201,
    summary="Create a system constraint",
)
def create_system_constraint(
    study_uid: Annotated[str, StudyUID],
    constraint_input: Annotated[StudySelectionSystemConstraintCreateInput, Body()],
):
    constraint = SystemConstraint(
        uid=utils.generate_uid("SystemConstraint"),
        name=constraint_input.name,
        category=constraint_input.category,
        description=constraint_input.description,
        order=0,
        accepted_version=True,
    ).save()

    query = """
        MATCH (sr:StudyRoot {uid: $study_uid})-[:LATEST]->(sv:StudyValue)
        MATCH (c:SystemConstraint {uid: $constraint_uid})
        MERGE (sv)-[:HAS_SYSTEM_CONSTRAINT]->(c)
    """
    db.cypher_query(query, {"study_uid": study_uid, "constraint_uid": constraint.uid})
    return {
        "system_constraint_uid": constraint.uid,
        "name": constraint.name,
        "category": constraint.category,
        "description": constraint.description,
    }


@router.patch(
    "/studies/{study_uid}/system-boundaries/{boundary_uid}",
    dependencies=[security, rbac.STUDY_WRITE],
    summary="Update a system boundary",
)
def update_system_boundary(
    study_uid: Annotated[str, StudyUID],
    boundary_uid: str,
    boundary_input: Annotated[StudySelectionSystemBoundaryCreateInput, Body()],
):
    boundary = SystemBoundary.nodes.get_or_none(uid=boundary_uid)
    if not boundary:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Boundary not found")
    boundary.name = boundary_input.name
    boundary.description = boundary_input.description
    boundary.save()
    return {
        "system_boundary_uid": boundary.uid,
        "name": boundary.name,
        "description": boundary.description,
    }


@router.patch(
    "/studies/{study_uid}/system-constraints/{constraint_uid}",
    dependencies=[security, rbac.STUDY_WRITE],
    summary="Update a system constraint",
)
def update_system_constraint(
    study_uid: Annotated[str, StudyUID],
    constraint_uid: str,
    constraint_input: Annotated[StudySelectionSystemConstraintCreateInput, Body()],
):
    constraint = SystemConstraint.nodes.get_or_none(uid=constraint_uid)
    if not constraint:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Constraint not found")
    constraint.name = constraint_input.name
    constraint.category = constraint_input.category
    constraint.description = constraint_input.description
    constraint.save()
    return {
        "system_constraint_uid": constraint.uid,
        "name": constraint.name,
        "category": constraint.category,
        "description": constraint.description,
    }
