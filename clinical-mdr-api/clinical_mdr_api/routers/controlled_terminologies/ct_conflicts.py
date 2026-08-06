"""CT conflicts router for Interactive Graph-Backed Resolution Dashboard."""

from typing import Annotated, Any

from fastapi import APIRouter, Body, HTTPException, Path
from neomodel import db
from pydantic import BaseModel

from common.auth import rbac
from common.auth.dependencies import security

router = APIRouter()


class ConflictItem(BaseModel):
    id: int
    type: str
    conceptId: str
    property: str
    inconsistency: str
    parentName: str | None = None


class ConflictSourceValue(BaseModel):
    rawId: int
    value: Any
    packageName: str
    packageVersion: str


class ConflictDetails(BaseModel):
    id: int
    parentLabel: str
    property: str
    inconsistency: str
    conceptId: str
    sources: list[ConflictSourceValue]


class ResolveInput(BaseModel):
    value: Any


@router.get(
    "/conflicts",
    dependencies=[security, rbac.LIBRARY_READ],
    summary="Returns all unresolved terminology inconsistencies.",
    status_code=200,
)
def get_unresolved_conflicts() -> list[ConflictItem]:
    query = """
    MATCH (gc:GroupedCodelist)-[:HAS_INCONSISTENCY]->(i:InconsistentCodelistProperties)
    WHERE NOT (i)-[:HAS_SOLUTION]->()
    OPTIONAL MATCH (gc)-[:SOURCE_CODELIST_DEF]->(rc:RawCodelist)
    WITH gc, i, collect(rc.submissionValue) as subVals
    RETURN id(i) as id, 'codelist' as type, gc.conceptId as conceptId, i.property as property, i.inconsistency as inconsistency, subVals[0] as parentName

    UNION ALL

    MATCH (gt:GroupedTerm)-[:HAS_INCONSISTENCY]->(i:InconsistentTermProperties)
    WHERE NOT (i)-[:HAS_SOLUTION]->()
    OPTIONAL MATCH (gt)-[:SOURCE_TERM_DEF]->(rt:RawTerm)
    WITH gt, i, collect(rt.preferredTerm) as prefTerms
    RETURN id(i) as id, 'term' as type, gt.conceptId as conceptId, i.property as property, i.inconsistency as inconsistency, prefTerms[0] as parentName

    UNION ALL

    MATCH (gc:GroupedCodelist)-[:HAS_INCONSISTENCY]->(i:InconsistentCodelistTerms)
    WHERE NOT (i)-[:HAS_SOLUTION]->()
    OPTIONAL MATCH (gc)-[:SOURCE_CODELIST_DEF]->(rc:RawCodelist)
    WITH gc, i, collect(rc.submissionValue) as subVals
    RETURN id(i) as id, 'codelist_terms' as type, gc.conceptId as conceptId, 'terms' as property, i.inconsistency as inconsistency, subVals[0] as parentName
    """
    results, _ = db.cypher_query(query)
    return [
        ConflictItem(
            id=row[0],
            type=row[1],
            conceptId=row[2],
            property=row[3],
            inconsistency=row[4],
            parentName=row[5],
        )
        for row in results
    ]


@router.get(
    "/conflicts/{conflict_id}",
    dependencies=[security, rbac.LIBRARY_READ],
    summary="Returns side-by-side details for a specific conflict.",
    status_code=200,
)
def get_conflict_details(conflict_id: int) -> ConflictDetails:
    query_info = """
    MATCH (g)-[:HAS_INCONSISTENCY]->(i)
    WHERE id(i) = $conflict_id
    RETURN labels(g)[0] as parentLabel, i.property as property, i.inconsistency as inconsistency, g.conceptId as conceptId, labels(i)[0] as iLabel
    """
    results_info, _ = db.cypher_query(query_info, {"conflict_id": conflict_id})
    if not results_info:
        raise HTTPException(status_code=404, detail="Conflict not found")

    parent_label = results_info[0][0]
    property_name = results_info[0][1]
    inconsistency_desc = results_info[0][2]
    concept_id = results_info[0][3]
    inconsistency_label = results_info[0][4]

    if inconsistency_label == "InconsistentCodelistTerms" and property_name == "terms":
        query_sources = """
        MATCH (g:GroupedCodelist)-[:HAS_INCONSISTENCY]->(i)
        WHERE id(i) = $conflict_id
        MATCH (g)-[:SOURCE_CODELIST_DEF]->(rc:RawCodelist)
        OPTIONAL MATCH (rc)-[:HAS_RAW_TERM]->(rt:RawTerm)
        OPTIONAL MATCH (rc)<-[:PACKAGE_CODELIST]-(p:CTPackage)
        WITH rc, p, collect(rt.submissionValue) as termList
        RETURN id(rc) as rawId, termList as value, coalesce(rc.packageName, p.name, 'Unknown Package') as packageName, coalesce(rc.packageVersion, p.version, '') as packageVersion
        """
        results_sources, _ = db.cypher_query(
            query_sources, {"conflict_id": conflict_id}
        )
    else:
        if parent_label == "GroupedCodelist":
            query_sources = """
            MATCH (g:GroupedCodelist)-[:HAS_INCONSISTENCY]->(i)
            WHERE id(i) = $conflict_id
            MATCH (g)-[:SOURCE_CODELIST_DEF]->(rc:RawCodelist)
            OPTIONAL MATCH (rc)<-[:PACKAGE_CODELIST]-(p:CTPackage)
            RETURN id(rc) as rawId, rc[$property] as value, coalesce(rc.packageName, p.name, 'Unknown Package') as packageName, coalesce(rc.packageVersion, p.version, '') as packageVersion
            """
        else:
            query_sources = """
            MATCH (g:GroupedTerm)-[:HAS_INCONSISTENCY]->(i)
            WHERE id(i) = $conflict_id
            MATCH (g)-[:SOURCE_TERM_DEF]->(rt:RawTerm)
            OPTIONAL MATCH (rt)<-[:PACKAGE_TERM]-(p:CTPackage)
            RETURN id(rt) as rawId, rt[$property] as value, coalesce(rt.packageName, p.name, 'Unknown Package') as packageName, coalesce(rt.packageVersion, p.version, '') as packageVersion
            """
        results_sources, _ = db.cypher_query(
            query_sources, {"conflict_id": conflict_id, "property": property_name}
        )

    sources = [
        ConflictSourceValue(
            rawId=row[0], value=row[1], packageName=row[2], packageVersion=row[3]
        )
        for row in results_sources
    ]

    return ConflictDetails(
        id=conflict_id,
        parentLabel=parent_label,
        property=property_name,
        inconsistency=inconsistency_desc,
        conceptId=concept_id,
        sources=sources,
    )


@router.post(
    "/conflicts/{conflict_id}/resolve",
    dependencies=[security, rbac.LIBRARY_WRITE],
    summary="Resolves a conflict by specifying the chosen value.",
    status_code=200,
)
def resolve_conflict(
    conflict_id: int,
    resolve_input: Annotated[
        ResolveInput, Body(description="The chosen value for resolution.")
    ],
) -> dict[str, str]:
    query_info = """
    MATCH (g)-[:HAS_INCONSISTENCY]->(i)
    WHERE id(i) = $conflict_id
    RETURN labels(g)[0] as parentLabel, i.property as property
    """
    results_info, _ = db.cypher_query(query_info, {"conflict_id": conflict_id})
    if not results_info:
        raise HTTPException(status_code=404, detail="Conflict not found")

    parent_label = results_info[0][0]
    property_name = results_info[0][1]
    value = resolve_input.value

    # Create Solution Node
    query_solution = """
    MATCH (g)-[:HAS_INCONSISTENCY]->(i)
    WHERE id(i) = $conflict_id
    MERGE (i)-[:HAS_SOLUTION]->(s:InconsistencySolution {solution: $value})
    """
    db.cypher_query(query_solution, {"conflict_id": conflict_id, "value": str(value)})

    # Update properties on grouped properties node
    if parent_label == "GroupedCodelist":
        query_update = """
        MATCH (g:GroupedCodelist)-[:HAS_INCONSISTENCY]->(i)
        WHERE id(i) = $conflict_id
        MERGE (g)-[:HAS_GROUPED_PROPERTIES]->(props:GroupedCodelistProperties)
        SET props += $properties_map
        """
        db.cypher_query(
            query_update,
            {"conflict_id": conflict_id, "properties_map": {property_name: value}},
        )
    elif parent_label == "GroupedTerm":
        query_update = """
        MATCH (g:GroupedTerm)-[:HAS_INCONSISTENCY]->(i)
        WHERE id(i) = $conflict_id
        MERGE (g)-[:HAS_GROUPED_PROPERTIES]->(props:GroupedTermProperties)
        SET props += $properties_map
        """
        db.cypher_query(
            query_update,
            {"conflict_id": conflict_id, "properties_map": {property_name: value}},
        )

    return {"status": "success", "message": "Conflict successfully resolved"}
