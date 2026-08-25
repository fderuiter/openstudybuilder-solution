import logging
import os
import sys
from typing import Optional, Tuple

import neo4j
from neo4j import GraphDatabase

from migrations.utils.utils import parse_db_url

logger = logging.getLogger("AliasManager")


class DatabaseAliasManager:
    """
    Manages logical database aliases, snapshot creation, staging database cloning,
    and automated rollback on migration failure.
    """

    def __init__(
        self,
        db_url: Optional[str] = None,
        active_alias: Optional[str] = None,
    ):
        self.db_url = db_url or os.environ.get(
            "DATABASE_URL", "bolt://neo4j:changeme1234@localhost:7687"
        )
        self.active_alias = active_alias or os.environ.get("DATABASE_NAME", "mdrdb")
        self.snapshot_db = f"{self.active_alias}_snapshot"
        self.staging_db = f"{self.active_alias}_staging"
        self._driver = None

    def get_driver(self):
        if not self._driver:
            clean_url, username, password = parse_db_url(self.db_url)
            self._driver = GraphDatabase.driver(clean_url, auth=(username, password))
        return self._driver

    def close(self):
        if self._driver:
            self._driver.close()
            self._driver = None

    def execute_system_query(self, query: str, params: Optional[dict] = None):
        """Executes a Cypher administrative query against the system database."""
        driver = self.get_driver()
        with driver.session(database="system") as session:
            result = session.run(query, params or {})
            records = list(result)
            summary = result.consume()
            return records, summary

    def prepare_snapshot_and_staging(self) -> Tuple[str, str]:
        """
        1. Identifies current target database for active_alias.
        2. Creates pre-migration snapshot database (`<alias>_snapshot`).
        3. Configures logical alias (`<alias>`) to point to the snapshot database.
        4. Creates staging database (`<alias>_staging`) cloned/copied from snapshot database.
        Returns (snapshot_db_name, staging_db_name).
        """
        logger.info(
            "Preparing pre-migration snapshot and staging database for alias '%s'...",
            self.active_alias,
        )
        try:
            # Check if active_alias exists as an alias
            source_db = self.active_alias
            try:
                records, _ = self.execute_system_query(
                    "SHOW ALIASES FOR DATABASE YIELD name, targetDatabase WHERE name = $name",
                    {"name": self.active_alias},
                )
                if records and "targetDatabase" in records[0]:
                    source_db = records[0]["targetDatabase"]
            except Exception as e:
                logger.debug("SHOW ALIASES query failed or not supported: %s", e)

            # 1. Create pre-migration snapshot database
            try:
                self.execute_system_query(
                    f"CREATE DATABASE {self.snapshot_db} IF NOT EXISTS AS COPY OF {source_db}"
                )
            except Exception as e:
                logger.warning(
                    "CREATE DATABASE AS COPY OF failed (%s), creating plain database", e
                )
                self.execute_system_query(
                    f"CREATE DATABASE {self.snapshot_db} IF NOT EXISTS"
                )

            # 2. Configure logical alias to point to snapshot_db
            try:
                self.execute_system_query(
                    f"CREATE OR REPLACE ALIAS {self.active_alias} FOR DATABASE {self.snapshot_db}"
                )
            except Exception as e:
                logger.warning(
                    "CREATE OR REPLACE ALIAS failed (%s), trying ALTER ALIAS", e
                )
                try:
                    self.execute_system_query(
                        f"ALTER ALIAS {self.active_alias} SET DATABASE TARGET {self.snapshot_db}"
                    )
                except Exception:
                    self.execute_system_query(
                        f"CREATE ALIAS {self.active_alias} IF NOT EXISTS FOR DATABASE {self.snapshot_db}"
                    )

            # 3. Drop old staging database if exists and create staging_db as copy of snapshot_db
            try:
                self.execute_system_query(
                    f"DROP DATABASE {self.staging_db} IF EXISTS DESTROY DATA"
                )
            except Exception as e:
                logger.debug("DROP DATABASE staging_db failed: %s", e)

            try:
                self.execute_system_query(
                    f"CREATE DATABASE {self.staging_db} IF NOT EXISTS AS COPY OF {self.snapshot_db}"
                )
            except Exception as e:
                logger.warning(
                    "Create staging DB as copy failed (%s), falling back to CREATE DATABASE",
                    e,
                )
                self.execute_system_query(
                    f"CREATE DATABASE {self.staging_db} IF NOT EXISTS"
                )

            logger.info(
                "Snapshot database '%s' and staging database '%s' prepared successfully.",
                self.snapshot_db,
                self.staging_db,
            )
            return self.snapshot_db, self.staging_db
        except Exception as e:
            logger.error("Failed to prepare snapshot and staging database: %s", e)
            raise

    def rollback(self):
        """
        Re-points the active logical database alias back to the pre-migration snapshot database.
        """
        logger.warning(
            "Triggering rollback: reassigning alias '%s' back to snapshot '%s'...",
            self.active_alias,
            self.snapshot_db,
        )
        try:
            try:
                self.execute_system_query(
                    f"ALTER ALIAS {self.active_alias} SET DATABASE TARGET {self.snapshot_db}"
                )
            except Exception as e:
                logger.warning(
                    "ALTER ALIAS failed (%s), trying CREATE OR REPLACE ALIAS", e
                )
                self.execute_system_query(
                    f"CREATE OR REPLACE ALIAS {self.active_alias} FOR DATABASE {self.snapshot_db}"
                )
            logger.info(
                "Rollback complete. Active alias '%s' points to '%s'.",
                self.active_alias,
                self.snapshot_db,
            )
        except Exception as e:
            logger.error("Error during alias rollback: %s", e)
            raise

    def promote_staging(self):
        """
        Swaps the primary database alias to point to the staging database and cleans up temporary staging aliases.
        """
        logger.info(
            "Promoting staging database '%s' to active alias '%s'...",
            self.staging_db,
            self.active_alias,
        )
        try:
            try:
                self.execute_system_query(
                    f"ALTER ALIAS {self.active_alias} SET DATABASE TARGET {self.staging_db}"
                )
            except Exception as e:
                logger.warning(
                    "ALTER ALIAS failed (%s), trying CREATE OR REPLACE ALIAS", e
                )
                self.execute_system_query(
                    f"CREATE OR REPLACE ALIAS {self.active_alias} FOR DATABASE {self.staging_db}"
                )

            # Cleanup temporary staging alias if existing
            temp_staging_alias = f"{self.active_alias}_temp_staging"
            try:
                self.execute_system_query(f"DROP ALIAS {temp_staging_alias} IF EXISTS")
            except Exception as e:
                logger.debug("Temp staging alias drop failed: %s", e)

            logger.info(
                "Promotion complete. Active alias '%s' now points to '%s'.",
                self.active_alias,
                self.staging_db,
            )
        except Exception as e:
            logger.error("Error promoting staging database: %s", e)
            raise
