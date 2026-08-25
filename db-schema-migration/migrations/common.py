import csv

from migrations.utils.utils import api_post

try:
    from neo4j_mdr_db.db_schema import (
        CONSTRAINTS,
        FULLTEXT_INDEXES,
        INDEXES,
        REL_INDEXES,
        TEXT_INDEXES,
        build_create_constraint_query,
        build_create_node_fulltext_index_query,
        build_create_node_index_query,
        build_create_node_text_index_query,
        build_create_rel_index_query,
    )
except ImportError:
    from db_schema import (
        CONSTRAINTS,
        FULLTEXT_INDEXES,
        INDEXES,
        REL_INDEXES,
        TEXT_INDEXES,
        build_create_constraint_query,
        build_create_node_fulltext_index_query,
        build_create_node_index_query,
        build_create_node_text_index_query,
        build_create_rel_index_query,
    )

REGEX_SNAKE_CASE = r"^[a-z]+(_[a-z]+)*$"
REGEX_SNAKE_CASE_WITH_DOT = r"^[a-z.]+(_[a-z.]+)*$"


def get_target_schema():
    target_constraints = {}
    for cst in CONSTRAINTS:
        name = f"constraint_{cst[0]}_{cst[1]}"
        query = build_create_constraint_query(
            label=cst[0], property=cst[1], type=cst[2]
        )
        target_constraints[name] = query

    target_indexes = {}
    for idx in INDEXES:
        name = f"index_{idx[0]}_{idx[1]}"
        query = build_create_node_index_query(idx)
        target_indexes[name] = query

    for idx in TEXT_INDEXES:
        name = f"index_{idx[0]}_{idx[1]}"
        query = build_create_node_text_index_query(idx)
        target_indexes[name] = query

    for idx in FULLTEXT_INDEXES:
        name = idx[2]
        query = build_create_node_fulltext_index_query(idx)
        target_indexes[name] = query

    for idx in REL_INDEXES:
        name = f"index_{idx[0]}_{idx[1]}"
        query = build_create_rel_index_query(idx)
        target_indexes[name] = query

    return target_constraints, target_indexes


def reconcile_schema(db_connection, logger):
    """
    Performs a single bidirectional schema reconciliation between the current database state
    and the target schema defined in neo4j_mdr_db.db_schema.
    - Missing standard schema elements (indexes/constraints) are created.
    - Valid standard schema elements are retained.
    - Obsolete standard schema elements (indexes/constraints matching standard naming convention) are dropped.
    - Custom plugin-created or third-party indexes and constraints are preserved.
    """
    logger.info("Starting single-pass schema reconciliation...")
    target_constraints, target_indexes = get_target_schema()

    # 1. Reconcile Constraints
    existing_constraints = set()
    try:
        rows, _ = db_connection.cypher_query("SHOW ALL CONSTRAINTS YIELD name")
        for row in rows:
            if row and row[0]:
                existing_constraints.add(row[0])
    except Exception as e:
        logger.warning("Could not fetch constraints from DB: %s", e)

    # Drop obsolete standard constraints
    for db_c_name in list(existing_constraints):
        if db_c_name not in target_constraints:
            if db_c_name.startswith("constraint_"):
                logger.info("Dropping obsolete standard constraint: %s", db_c_name)
                db_connection.cypher_query(f"DROP CONSTRAINT {db_c_name}")
            else:
                logger.info("Preserving custom constraint: %s", db_c_name)

    # Create missing standard constraints
    for name, query in target_constraints.items():
        if name not in existing_constraints:
            logger.info("Creating missing standard constraint: %s", name)
            db_connection.cypher_query(query)
        else:
            logger.info("Retaining valid standard constraint: %s", name)

    # 2. Reconcile Indexes
    existing_indexes = {}
    try:
        try:
            rows, columns = db_connection.cypher_query(
                "SHOW ALL INDEXES YIELD name, type, indexProvider, owningConstraint"
            )
        except Exception:
            rows, columns = db_connection.cypher_query(
                "SHOW ALL INDEXES YIELD name, type, indexProvider"
            )
        for row in rows:
            item = dict(zip(columns, row))
            existing_indexes[item["name"]] = item
    except Exception as e:
        logger.warning("Could not fetch indexes from DB: %s", e)

    # Identify constraint-backing indexes
    constraint_backing_names = set(target_constraints.keys())
    for db_c in existing_constraints:
        if db_c.startswith("constraint_"):
            constraint_backing_names.add(db_c)

    # Drop obsolete standard indexes
    for db_idx_name, item in list(existing_indexes.items()):
        # Skip LOOKUP indexes, token-lookup indexes, and constraint-backing indexes
        if (
            item.get("owningConstraint")
            or db_idx_name in constraint_backing_names
            or item.get("type") == "LOOKUP"
            or (
                item.get("indexProvider")
                and item["indexProvider"].startswith("token-lookup")
            )
        ):
            continue

        if db_idx_name not in target_indexes:
            # Check if it follows standard index naming convention
            is_standard_naming = db_idx_name.startswith("index_") or db_idx_name in {
                "codelist_fulltext_index",
                "term_fulltext_index",
            }
            if is_standard_naming:
                logger.info("Dropping obsolete standard index: %s", db_idx_name)
                db_connection.cypher_query(f"DROP INDEX {db_idx_name}")
            else:
                logger.info("Preserving custom plugin index: %s", db_idx_name)

    # Create missing standard indexes
    for name, query in target_indexes.items():
        if name not in existing_indexes:
            logger.info("Creating missing standard index: %s", name)
            db_connection.cypher_query(query)
        else:
            logger.info("Retaining valid standard index: %s", name)

    logger.info("Single-pass schema reconciliation completed successfully.")


def migrate_indexes_and_constraints(db_connection, logger):
    logger.info("Reconciling db indexes and constraints...")
    reconcile_schema(db_connection, logger)


def migrate_ct_config_values(db_connection, logger):
    logger.info("Re-creating CTConfig values...")
    # Remove all CTConfigRoot/Value nodes and recreate them by issuing POST /configurations requests,
    # based on study fields configuration csv file.
    db_connection.cypher_query(
        "MATCH (val:CTConfigValue)-[r]-(root:CTConfigRoot) DETACH DELETE root, val"
    )
    db_connection.cypher_query(
        "MATCH (val:CTConfigValue)-[r]-(root:DeletedCTConfigRoot) DETACH DELETE root, val"
    )

    filename = (
        "studybuilder_import/datafiles/configuration/study_fields_configuration.csv"
    )
    with open(filename, encoding="utf-8", errors="ignore") as csv_file:
        for line in csv.DictReader(csv_file):
            # Replace empty strings with None
            line = {k: v if v != "" else None for k, v in line.items()}
            logger.info(
                "Adding CTConfigRoot/Value for study field '%s'",
                line["study_field_name"],
            )
            api_post(path="/configurations", payload=line)

