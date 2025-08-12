import pytest

from common import exceptions
from common.config import settings
from common.utils import load_env, strtobool, validate_page_number_and_page_size


def test_strtobool():
    assert strtobool("True") == 1
    assert strtobool("true") == 1
    assert strtobool("TRUE") == 1
    assert strtobool("t") == 1
    assert strtobool("T") == 1
    assert strtobool("1") == 1

    assert strtobool("False") == 0
    assert strtobool("false") == 0
    assert strtobool("FALSE") == 0
    assert strtobool("f") == 0
    assert strtobool("F") == 0
    assert strtobool("0") == 0

    with pytest.raises(ValueError) as exc_info:
        strtobool("-invalid-")
    assert str(exc_info.value) == "invalid truth value: -invalid-"


@pytest.mark.parametrize(
    "page_number, page_size",
    [[1, 10], [2, 200], [3000, 1000], [settings.max_int_neo4j, 1]],
)
def test_validate_page_number_and_page_size(page_number, page_size):
    validate_page_number_and_page_size(page_number, page_size)


@pytest.mark.parametrize(
    "page_number, page_size",
    [
        [settings.max_int_neo4j + 1, 1],
        [settings.max_int_neo4j, 10],
        [1, settings.max_int_neo4j + 1],
        [10, settings.max_int_neo4j],
    ],
)
def test_validate_page_number_and_page_size_exceeds_max(page_number, page_size):
    with pytest.raises(exceptions.ValidationException) as exc_info:
        validate_page_number_and_page_size(page_number, page_size)
    assert (
        str(exc_info.value)
        == f"(page_number * page_size) value cannot be bigger than {settings.max_int_neo4j}"
    )


@pytest.mark.parametrize(
    "page_number, page_size, msg",
    [
        (0, 1, "page_number must be greater than or equal to 1"),
        (-1, 10, "page_number must be greater than or equal to 1"),
        (1, -1, "page_size must be greater than or equal to 0"),
        (2, -10, "page_size must be greater than or equal to 0"),
    ],
)
def test_validate_page_number_and_page_size_negative_inputs(
    page_number, page_size, msg
):
    with pytest.raises(exceptions.ValidationException) as exc_info:
        validate_page_number_and_page_size(page_number, page_size)
    assert str(exc_info.value) == msg


def test_load_env():
    env_var1 = load_env("VAR1", "value1")
    assert env_var1 == "value1"

    env_var1 = load_env("VAR1", "")
    assert env_var1 == ""

    with pytest.raises(EnvironmentError) as exc_info:
        load_env("VAR1")
    assert str(exc_info.value) == "Failed because VAR1 is not set."
