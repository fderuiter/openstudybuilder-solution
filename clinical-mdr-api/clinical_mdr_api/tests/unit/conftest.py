import pytest
import functools
from unittest.mock import patch, MagicMock, PropertyMock
from clinical_mdr_api.services.user_info import UserInfoService
from clinical_mdr_api.domain_repositories.controlled_terminologies.ct_codelist_name_repository import CTCodelistNameRepository
from common.auth.models import User as AuthUser

class MockCodelistRepoResult:
    def __init__(self):
        self.items = []

class MockTransaction:
    def __init__(self, *args, **kwargs):
        pass
    
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
        
    def __call__(self, *args, **kwargs):
        if args and callable(args[0]):
            # Used as a direct decorator, e.g. @db.transaction
            func = args[0]
            @functools.wraps(func)
            def wrapper(*w_args, **w_kwargs):
                return func(*w_args, **w_kwargs)
            return wrapper
        # Used as a function returning a context manager, e.g. db.transaction()
        return self

@pytest.fixture(autouse=True, scope="session")
def mock_unit_test_dependencies():
    # Patch UserInfoService
    patcher_user = patch.object(
        UserInfoService,
        "get_author_username_from_id",
        side_effect=lambda user_id: user_id
    )
    
    # Patch CTCodelistNameRepository.find_all
    patcher_codelist = patch.object(
        CTCodelistNameRepository,
        "find_all",
        return_value=MockCodelistRepoResult()
    )
    
    # Patch db.cypher_query globally to avoid attempting to connect to Neo4j
    # We return ([], None) which is a safe default for most queries
    from neomodel import db
    patcher_db = patch.object(
        db,
        "cypher_query",
        return_value=([], None)
    )
    
    # Patch Database.transaction on the class because it is a read-only property
    from neomodel.sync_.database import Database
    patcher_db_tx = patch.object(
        Database,
        "transaction",
        new_callable=PropertyMock,
        return_value=MockTransaction()
    )
    
    # Patch db.begin, db.commit, db.rollback to prevent neomodel from initiating socket/driver connections
    patcher_db_begin = patch.object(db, "begin", return_value=None)
    patcher_db_commit = patch.object(db, "commit", return_value=None)
    patcher_db_rollback = patch.object(db, "rollback", return_value=None)
    
    # Ensure _active_transaction on db is None
    db._active_transaction = None
    
    # Patch ensure_transaction decorator factory
    patcher_ensure_tx = patch(
        "clinical_mdr_api.services._utils.ensure_transaction",
        side_effect=lambda db_arg: lambda func: func
    )
    
    # Create dummy user and auth objects
    dummy_user = AuthUser(
        sub="dummy_sub",
        azp="dummy_azp",
        oid="dummy_oid",
        name="dummy_name",
        username="dummy_username",
        email="dummy_email",
        roles={"dummy_role"}
    )
    dummy_auth = MagicMock()
    dummy_auth.user = dummy_user
    
    # Patch common.auth.user.user and common.auth.user.auth
    patcher_auth_user = patch("common.auth.user.user", return_value=dummy_user)
    patcher_auth = patch("common.auth.user.auth", return_value=dummy_auth)
    
    patcher_user.start()
    patcher_codelist.start()
    patcher_db.start()
    patcher_db_tx.start()
    patcher_db_begin.start()
    patcher_db_commit.start()
    patcher_db_rollback.start()
    patcher_ensure_tx.start()
    patcher_auth_user.start()
    patcher_auth.start()
    
    yield
    
    patcher_auth.stop()
    patcher_auth_user.stop()
    patcher_ensure_tx.stop()
    patcher_db_rollback.stop()
    patcher_db_commit.stop()
    patcher_db_begin.stop()
    patcher_db_tx.stop()
    patcher_db.stop()
    patcher_codelist.stop()
    patcher_user.stop()
