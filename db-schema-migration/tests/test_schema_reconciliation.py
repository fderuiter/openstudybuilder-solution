import logging
from unittest.mock import MagicMock, patch

import pytest
from migrations.common import get_target_schema, reconcile_schema
import run_sequential


@pytest.fixture
def mock_logger():
    return logging.getLogger("TestSchemaReconciliation")


def test_get_target_schema():
    target_constraints, target_indexes = get_target_schema()
    assert isinstance(target_constraints, dict)
    assert isinstance(target_indexes, dict)
    assert len(target_constraints) > 0
    assert len(target_indexes) > 0

    # Verify standard naming patterns
    for name, query in target_constraints.items():
        assert name.startswith("constraint_")
        assert "CREATE CONSTRAINT" in query

    for name, query in target_indexes.items():
        assert name.startswith("index_") or name in {
            "codelist_fulltext_index",
            "term_fulltext_index",
        }
        assert "CREATE" in query and "INDEX" in query


def test_reconcile_schema_creates_missing_and_retains_valid(mock_logger):
    target_constraints, target_indexes = get_target_schema()

    sample_c_name = next(iter(target_constraints.keys()))
    sample_i_name = next(iter(target_indexes.keys()))

    mock_db = MagicMock()

    def mock_cypher_query(query, *args, **kwargs):
        if "SHOW ALL CONSTRAINTS" in query:
            return ([(sample_c_name,)], ["name"])
        elif "SHOW ALL INDEXES" in query:
            return (
                [(sample_i_name, "RANGE", "range", None)],
                ["name", "type", "indexProvider", "owningConstraint"],
            )
        return ([], None)

    mock_db.cypher_query.side_effect = mock_cypher_query

    reconcile_schema(mock_db, mock_logger)

    executed_queries = [call_args[0][0] for call_args in mock_db.cypher_query.call_args_list]

    # Check that sample_c_name and sample_i_name were NOT dropped
    for query in executed_queries:
        assert f"DROP CONSTRAINT {sample_c_name}" not in query
        assert f"DROP INDEX {sample_i_name}" not in query

    # Check that missing constraints and indexes WERE created
    for name, create_query in target_constraints.items():
        if name != sample_c_name:
            assert any(create_query in q for q in executed_queries), f"Expected creation query for {name}"

    for name, create_query in target_indexes.items():
        if name != sample_i_name:
            assert any(create_query in q for q in executed_queries), f"Expected creation query for {name}"


def test_reconcile_schema_drops_obsolete_standard_elements(mock_logger):
    obsolete_constraint = "constraint_ObsoleteEntity_uid"
    obsolete_index = "index_ObsoleteEntity_uid"

    mock_db = MagicMock()

    def mock_cypher_query(query, *args, **kwargs):
        if "SHOW ALL CONSTRAINTS" in query:
            return ([(obsolete_constraint,)], ["name"])
        elif "SHOW ALL INDEXES" in query:
            return (
                [(obsolete_index, "RANGE", "range", None)],
                ["name", "type", "indexProvider", "owningConstraint"],
            )
        return ([], None)

    mock_db.cypher_query.side_effect = mock_cypher_query

    reconcile_schema(mock_db, mock_logger)

    executed_queries = [call_args[0][0] for call_args in mock_db.cypher_query.call_args_list]

    # Obsolete standard constraint and index must be dropped
    assert f"DROP CONSTRAINT {obsolete_constraint}" in executed_queries
    assert f"DROP INDEX {obsolete_index}" in executed_queries


def test_reconcile_schema_preserves_custom_plugin_indexes(mock_logger):
    custom_index_1 = "custom_graph_analytics_idx"
    custom_index_2 = "plugin_gds_pagerank"
    custom_constraint = "custom_third_party_constraint"
    lookup_index = "LOOKUP_INDEX"

    mock_db = MagicMock()

    def mock_cypher_query(query, *args, **kwargs):
        if "SHOW ALL CONSTRAINTS" in query:
            return ([(custom_constraint,)], ["name"])
        elif "SHOW ALL INDEXES" in query:
            return (
                [
                    (custom_index_1, "RANGE", "range", None),
                    (custom_index_2, "FULLTEXT", "community-fulltext", None),
                    (lookup_index, "LOOKUP", "token-lookup", None),
                ],
                ["name", "type", "indexProvider", "owningConstraint"],
            )
        return ([], None)

    mock_db.cypher_query.side_effect = mock_cypher_query

    reconcile_schema(mock_db, mock_logger)

    executed_queries = [call_args[0][0] for call_args in mock_db.cypher_query.call_args_list]

    # Custom plugin indexes and constraints MUST NOT be dropped
    assert f"DROP CONSTRAINT {custom_constraint}" not in executed_queries
    assert f"DROP INDEX {custom_index_1}" not in executed_queries
    assert f"DROP INDEX {custom_index_2}" not in executed_queries
    assert f"DROP INDEX {lookup_index}" not in executed_queries


@patch("subprocess.run")
@patch("migrations.common.migrate_indexes_and_constraints")
@patch("migrations.utils.utils.get_db_connection")
def test_run_sequential_execution_order(mock_get_db, mock_reconcile, mock_subprocess):
    execution_order = []

    def mock_subp_run(cmd, **kwargs):
        execution_order.append(("subprocess", cmd[2]))
        return MagicMock(returncode=0)

    mock_subprocess.side_effect = mock_subp_run

    def mock_reconcile_func(db, logger):
        execution_order.append(("reconcile", "single_pass"))

    mock_reconcile.side_effect = mock_reconcile_func

    run_sequential.main()

    # Verify that subprocess calls (migrations and data corrections) happened before reconcile
    subp_calls = [item for item in execution_order if item[0] == "subprocess"]
    reconcile_calls = [item for item in execution_order if item[0] == "reconcile"]

    assert len(subp_calls) > 0
    assert len(reconcile_calls) == 1

    # Check order: migrations run first, data corrections run second, reconcile runs last!
    last_event = execution_order[-1]
    assert last_event == ("reconcile", "single_pass")

    # Verify migration files ran before correction files
    migration_indices = [
        i for i, item in enumerate(execution_order) if "migrations." in item[1]
    ]
    correction_indices = [
        i for i, item in enumerate(execution_order) if "data_corrections." in item[1]
    ]

    assert max(migration_indices) < min(correction_indices)
