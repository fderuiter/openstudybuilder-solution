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
    ],
)
def test_parse_db_url(db_url, expected_url, expected_user, expected_pass):
    url, user, password = utils.parse_db_url(db_url)
    assert url == expected_url
    assert user == expected_user
    assert password == expected_pass
