# pylint: disable=unused-wildcard-import,wildcard-import

from clinical_mdr_api.tests.fixtures.app import *
from clinical_mdr_api.tests.fixtures.auth import *
from clinical_mdr_api.tests.fixtures.database import *
from clinical_mdr_api.tests.fixtures.logging import *
from clinical_mdr_api.tests.fixtures.routes import *
from clinical_mdr_api.tests.fixtures.study import *
from clinical_mdr_api.tests.fixtures.tracing import *


def pytest_configure(config):
    """Register custom pytest markers"""
    # Register the order marker so pytest can recognize it
    config.addinivalue_line("markers", "order: mark test to run in a specific order")


def pytest_addoption(parser):
    """add custom command-line options to Pytest"""

    parser.addoption(
        "--keep-db",
        action="store_true",
        default=False,
        help="Do not destroy the test database after test run",
    )
    parser.addoption(
        "--enable-tracing",
        action="store_true",
        default=False,
        help="Enables logging of tracing messages of OpenCensus tracer",
    )


import pytest
from unittest.mock import patch, MagicMock
from functools import wraps

def mock_enter(self):
    return self

def mock_exit(self, exc_type, exc_val, exc_tb):
    pass

def mock_cypher_query(self, *args, **kwargs):
    return [], []

@pytest.fixture(scope="module", autouse=True)
def mock_user_info_service(request):
    """Globally mock UserInfoService.get_author_username_from_id, CTCodelistNameRepository.find_all, common.auth.user.auth, neomodel transaction boundaries, and cypher queries for all unit tests."""
    node_path = str(request.node.path if hasattr(request.node, "path") else request.node.fspath)
    if "unit" in request.node.nodeid or "unit" in node_path:
        mock_codelist_result = MagicMock()
        mock_codelist_result.items = []
        mock_auth = MagicMock()
        mock_user = MagicMock()
        mock_user.id.return_value = "test_author"
        mock_user.username = "test_author"
        mock_user.name = "Test Author"
        mock_user.email = "test@example.com"
        mock_auth.user = mock_user
        with patch("clinical_mdr_api.services.user_info.UserInfoService.get_author_username_from_id", side_effect=lambda *args, **kwargs: args[-1] if args else "test_author"), \
             patch("clinical_mdr_api.domains.study_definition_aggregates.study_configuration.CTCodelistNameRepository.find_all", return_value=mock_codelist_result), \
             patch("common.auth.user.auth", return_value=mock_auth), \
             patch("neomodel.sync_.transaction.TransactionProxy.__enter__", mock_enter), \
             patch("neomodel.sync_.transaction.TransactionProxy.__exit__", mock_exit), \
             patch("neomodel.sync_.database.Database.cypher_query", mock_cypher_query):
            yield
    else:
        yield

