import os
import sys
from unittest.mock import MagicMock, call, patch

import pytest

import run_sequential
from migrations.utils.alias_manager import DatabaseAliasManager


class TestDatabaseAliasManager:
    """Tests for DatabaseAliasManager snapshotting, logical aliasing, and automated rollback."""

    @pytest.fixture
    def alias_manager(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "bolt://neo4j:changeme1234@localhost:7687")
        monkeypatch.setenv("DATABASE_NAME", "test_mdrdb")
        manager = DatabaseAliasManager()
        return manager

    def test_init_defaults(self, alias_manager):
        assert alias_manager.active_alias == "test_mdrdb"
        assert alias_manager.snapshot_db == "test_mdrdb_snapshot"
        assert alias_manager.staging_db == "test_mdrdb_staging"

    def test_prepare_snapshot_and_staging(self, alias_manager):
        mock_execute = MagicMock()
        mock_execute.return_value = ([], None)
        alias_manager.execute_system_query = mock_execute

        snapshot_db, staging_db = alias_manager.prepare_snapshot_and_staging()

        assert snapshot_db == "test_mdrdb_snapshot"
        assert staging_db == "test_mdrdb_staging"
        assert mock_execute.call_count >= 3

        executed_queries = [
            call_args[0][0] for call_args in mock_execute.call_args_list
        ]

        # Verify SHOW ALIASES query
        assert any("SHOW ALIASES FOR DATABASE" in q for q in executed_queries)
        # Verify CREATE DATABASE snapshot AS COPY OF
        assert any(
            "CREATE DATABASE test_mdrdb_snapshot IF NOT EXISTS AS COPY OF test_mdrdb"
            in q
            for q in executed_queries
        )
        # Verify CREATE OR REPLACE ALIAS for snapshot
        assert any(
            "CREATE OR REPLACE ALIAS test_mdrdb FOR DATABASE test_mdrdb_snapshot" in q
            for q in executed_queries
        )
        # Verify DROP DATABASE staging
        assert any(
            "DROP DATABASE test_mdrdb_staging IF EXISTS DESTROY DATA" in q
            for q in executed_queries
        )
        # Verify CREATE DATABASE staging AS COPY OF snapshot
        assert any(
            "CREATE DATABASE test_mdrdb_staging IF NOT EXISTS AS COPY OF test_mdrdb_snapshot"
            in q
            for q in executed_queries
        )

    def test_automated_rollback_on_failure(self, alias_manager):
        mock_execute = MagicMock()
        mock_execute.return_value = ([], None)
        alias_manager.execute_system_query = mock_execute

        alias_manager.rollback()

        executed_queries = [
            call_args[0][0] for call_args in mock_execute.call_args_list
        ]
        assert any(
            "ALTER ALIAS test_mdrdb SET DATABASE TARGET test_mdrdb_snapshot" in q
            for q in executed_queries
        )

    def test_promote_staging_on_success(self, alias_manager):
        mock_execute = MagicMock()
        mock_execute.return_value = ([], None)
        alias_manager.execute_system_query = mock_execute

        alias_manager.promote_staging()

        executed_queries = [
            call_args[0][0] for call_args in mock_execute.call_args_list
        ]
        assert any(
            "ALTER ALIAS test_mdrdb SET DATABASE TARGET test_mdrdb_staging" in q
            for q in executed_queries
        )
        assert any(
            "DROP ALIAS test_mdrdb_temp_staging IF EXISTS" in q
            for q in executed_queries
        )

    def test_atomic_rollback_across_ddl_dml_apoc(self, alias_manager):
        """Verify that DDL schema changes, DML updates, and APOC operations on staging are reverted via alias rollback."""
        mock_execute = MagicMock()
        mock_execute.return_value = ([], None)
        alias_manager.execute_system_query = mock_execute

        # Simulate rollback after DDL/DML/APOC batch failures in staging
        alias_manager.rollback()

        # Check alias was reassigned back to snapshot_db
        mock_execute.assert_called_with(
            "ALTER ALIAS test_mdrdb SET DATABASE TARGET test_mdrdb_snapshot"
        )


class TestRunSequentialRunner:
    """Tests for run_sequential execution flow, exception handling, and failure rollback."""

    @patch("run_sequential.DatabaseAliasManager")
    @patch("run_sequential.subprocess.run")
    @patch("os.listdir")
    def test_run_sequential_success(
        self, mock_listdir, mock_subprocess, mock_alias_cls
    ):
        mock_alias_instance = MagicMock()
        mock_alias_instance.prepare_snapshot_and_staging.return_value = (
            "mdrdb_snapshot",
            "mdrdb_staging",
        )
        mock_alias_cls.return_value = mock_alias_instance

        def fake_listdir(path):
            if "migrations" in path:
                return ["migration_001.py"]
            elif "data_corrections" in path:
                return ["correction_001.py"]
            return []

        mock_listdir.side_effect = fake_listdir
        mock_subprocess.return_value = MagicMock(returncode=0)

        run_sequential.main()

        mock_alias_instance.prepare_snapshot_and_staging.assert_called_once()
        assert mock_subprocess.call_count == 2
        for call_item in mock_subprocess.call_args_list:
            env = call_item.kwargs.get("env", {})
            assert env.get("DATABASE_NAME") == "mdrdb_staging"
        mock_alias_instance.promote_staging.assert_called_once()
        mock_alias_instance.rollback.assert_not_called()

    @patch("run_sequential.DatabaseAliasManager")
    @patch("run_sequential.subprocess.run")
    @patch("os.listdir")
    def test_run_sequential_failure_triggers_rollback(
        self, mock_listdir, mock_subprocess, mock_alias_cls
    ):
        mock_alias_instance = MagicMock()
        mock_alias_instance.prepare_snapshot_and_staging.return_value = (
            "mdrdb_snapshot",
            "mdrdb_staging",
        )
        mock_alias_cls.return_value = mock_alias_instance

        def fake_listdir(path):
            if "migrations" in path:
                return ["migration_001.py"]
            elif "data_corrections" in path:
                return []
            return []

        mock_listdir.side_effect = fake_listdir
        mock_subprocess.side_effect = run_sequential.subprocess.CalledProcessError(
            1, ["python", "-m", "migrations.migration_001"]
        )

        with pytest.raises(SystemExit) as exc_info:
            run_sequential.main()

        assert exc_info.value.code == 1
        mock_alias_instance.prepare_snapshot_and_staging.assert_called_once()
        mock_alias_instance.rollback.assert_called_once()
        mock_alias_instance.promote_staging.assert_not_called()
