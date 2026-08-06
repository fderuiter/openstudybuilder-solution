import pytest

from migrations.utils import utils


@pytest.mark.parametrize(
    "input_val, output",
    [
        pytest.param(
            "japaneseTrialRegistryIdJapicNullValueCode",
            "japanese_trial_registry_id_japic_null_value_code",
        ),
        pytest.param(
            "japanese_trial_registry_id_JAPIC_null_value_code",
            "japanese_trial_registry_id_japic_null_value_code",
        ),
        pytest.param(
            "id_metadata.registry_identifiers",
            "id_metadata.registry_identifiers",
        ),
    ],
)
def test_snake_case(input_val, output):
    assert output == utils.snake_case(input_val)


@pytest.mark.parametrize(
    "db_url, expected_url, expected_user, expected_pass",
    [
        pytest.param(
            "bolt://neo4j:changeme1234@localhost:7687",
            "bolt://localhost:7687",
            "neo4j",
            "changeme1234",
            id="standard_url",
        ),
        pytest.param(
            "bolt://localhost:7687",
            "bolt://localhost:7687",
            "neo4j",
            "",
            id="missing_credentials",
        ),
        pytest.param(
            "bolt://neo4j:p@ss:w:ord@localhost:7687",
            "bolt://localhost:7687",
            "neo4j",
            "p@ss:w:ord",
            id="raw_special_characters",
        ),
        pytest.param(
            "bolt://neo4j:p%40ss%3Aw%3Aord@localhost:7687",
            "bolt://localhost:7687",
            "neo4j",
            "p@ss:w:ord",
            id="url_encoded_special_characters",
        ),
        pytest.param(
            "bolt+s://custom_user:secure@123@host:port/dbname?query=1",
            "bolt+s://host:port/dbname?query=1",
            "custom_user",
            "secure@123",
            id="complex_scheme_and_path",
        ),
        pytest.param(
            "neo4j+ssc://localhost:7687",
            "neo4j+ssc://localhost:7687",
            "neo4j",
            "",
            id="neo4j_ssc_scheme_no_creds",
        ),
        pytest.param(
            None,
            "",
            "neo4j",
            "",
            id="none_db_url",
        ),
        pytest.param(
            "",
            "",
            "neo4j",
            "",
            id="empty_db_url",
        ),
        pytest.param(
            12345,
            "",
            "neo4j",
            "",
            id="non_string_db_url",
        ),
    ],
)
def test_parse_db_url(db_url, expected_url, expected_user, expected_pass):
    url, user, password = utils.parse_db_url(db_url)
    assert url == expected_url
    assert user == expected_user
    assert password == expected_pass


def test_get_db_connection(monkeypatch):
    from neomodel import config as neoconfig
    from neomodel import db

    # Mock environment variables
    monkeypatch.setenv("DATABASE_URL", "bolt://neo4j:p@ss:w:ord@localhost:7687")
    monkeypatch.setenv("DATABASE_NAME", "testdb")
    monkeypatch.setenv("CREATE_DB", "false")

    # Mock db.set_connection and db.cypher_query
    called_connections = []
    def mock_set_connection(url):
        called_connections.append(url)
    monkeypatch.setattr(db, "set_connection", mock_set_connection)

    query_count = 0
    def mock_cypher_query(query, params=None):
        nonlocal query_count
        query_count += 1
        return [], None
    monkeypatch.setattr(db, "cypher_query", mock_cypher_query)

    # Call get_db_connection
    res = utils.get_db_connection()

    assert res == db
    # Credentials should be url-encoded in the connection string
    expected_url = "bolt://neo4j:p%40ss%3Aw%3Aord@localhost:7687/testdb"
    assert neoconfig.DATABASE_URL == expected_url
    assert expected_url in called_connections


def test_get_db_connection_with_path(monkeypatch):
    from neomodel import config as neoconfig
    from neomodel import db

    # Mock environment variables where DATABASE_URL already has a path/database name
    monkeypatch.setenv("DATABASE_URL", "bolt://neo4j:p@ss:w:ord@localhost:7687/testdb")
    monkeypatch.setenv("DATABASE_NAME", "testdb")
    monkeypatch.setenv("CREATE_DB", "false")

    # Mock db.set_connection and db.cypher_query
    called_connections = []
    def mock_set_connection(url):
        called_connections.append(url)
    monkeypatch.setattr(db, "set_connection", mock_set_connection)

    query_count = 0
    def mock_cypher_query(query, params=None):
        nonlocal query_count
        query_count += 1
        return [], None
    monkeypatch.setattr(db, "cypher_query", mock_cypher_query)

    # Call get_db_connection
    res = utils.get_db_connection()

    assert res == db
    # Credentials should be url-encoded in the connection string and database name shouldn't be duplicated
    expected_url = "bolt://neo4j:p%40ss%3Aw%3Aord@localhost:7687/testdb"
    assert neoconfig.DATABASE_URL == expected_url
    # Make sure we didn't end up with /testdb/testdb
    assert "bolt://neo4j:p%40ss%3Aw%3Aord@localhost:7687/testdb/testdb" not in called_connections


def test_get_db_connection_with_query_params(monkeypatch):
    from neomodel import config as neoconfig
    from neomodel import db

    # Mock environment variables where DATABASE_URL has query parameters and a path
    monkeypatch.setenv("DATABASE_URL", "bolt://neo4j:p@ss:w:ord@localhost:7687/testdb?policy=routing#myfragment")
    monkeypatch.setenv("DATABASE_NAME", "testdb")
    monkeypatch.setenv("CREATE_DB", "false")

    # Mock db.set_connection and db.cypher_query
    called_connections = []
    def mock_set_connection(url):
        called_connections.append(url)
    monkeypatch.setattr(db, "set_connection", mock_set_connection)

    query_count = 0
    def mock_cypher_query(query, params=None):
        nonlocal query_count
        query_count += 1
        return [], None
    monkeypatch.setattr(db, "cypher_query", mock_cypher_query)

    # Call get_db_connection
    res = utils.get_db_connection()

    assert res == db
    # Credentials should be url-encoded in the connection string and query/fragment preserved
    expected_url = "bolt://neo4j:p%40ss%3Aw%3Aord@localhost:7687/testdb?policy=routing#myfragment"
    assert neoconfig.DATABASE_URL == expected_url
    assert expected_url in called_connections



