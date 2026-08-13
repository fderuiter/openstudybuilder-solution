from typing import Annotated

import pytest
from pydantic import Field

from clinical_mdr_api.models.utils import InputModel, sanitize_html

TEXT_INPUTS = [
    (" HellO", "HellO"),
    ("hi Foo ", "hi Foo"),
    (" bL4h bla ", "bL4h bla"),
    (
        "<b><img src='' onerror='alert(\\'hax\\')'>XSS anyone? </b>",
        "<b>XSS anyone? </b>",
    ),
    ("<unknown> hi", "hi"),
    (" an <script>alert('XSS')</script> elephant", "an  elephant"),
    (" zeR+0 <img src='x' onerror='albert'>", "zeR+0"),
    ("<iframe src='javascript:alert(1)'>a</iframe>", "a"),
    ("b <div style='background:url(javascript:alert(1))'>", "b"),
    ("<a href='javascript:alert(1)'>Click me</a>", "Click me"),
    ('<body onload="alert(1)">event handler ', "event handler"),
    ("<math><mi xlink:href='javascript:alert(1)'>x</mi></math>", "x"),
    (" <img onload='javascript:alert(1)'> . ", "."),
    ("<li onmouseover=alert(1)>\nobj\n Ect\n</li>", "<li>\nobj\n Ect\n</li>"),
    (
        " <form action='javascript:alert(1)'> <input type='submit'> x abc z </form>",
        "x abc z",
    ),
    ("<div>赤辛猫カレ </div> ", "赤辛猫カレ"),
    ("<b onclick=alert(1)>Bold</b>", "<b>Bold</b>"),
    ("<p onmouseover='foo%bar'>Normal text. </p>", "<p>Normal text. </p>"),
    (
        "Global Impression - Compared to <protocol specified time point> how much changed?",
        "Global Impression - Compared to  how much changed?",
    ),
    (
        "Global Impression - Compared to < protocol specified time point> how much changed?",
        "Global Impression - Compared to &lt; protocol specified time point&gt; how much changed?",
    ),
    (
        "Global Impression - Compared to < protocol specified time point > how much changed?",
        "Global Impression - Compared to &lt; protocol specified time point &gt; how much changed?",
    ),
    (" more > or less ", "more &gt; or less"),
    ("more>0 or less ", "more&gt;0 or less"),
    ("x>=1", "x&gt;=1"),
    ("x>=1 or y>2", "x&gt;=1 or y&gt;2"),
    ("x <= 1 or y > 2", "x &lt;= 1 or y &gt; 2"),
    ("<svg onload=alert(1)><p>lol", "<p>lol</p>"),
    ("age >=11m, <12y SCD", "age &gt;=11m, &lt;12y SCD"),
]


class MockInput(InputModel):
    title: Annotated[str, Field(min_length=1)]
    body: Annotated[str, Field(min_length=1, json_schema_extra={"format": "html"})]
    tags: Annotated[list[str] | None, Field(json_schema_extra={"nullable": True})] = (
        None
    )
    whether: Annotated[bool, Field()] = False
    num: Annotated[int | None, Field(json_schema_extra={"nullable": True})] = None


@pytest.mark.parametrize(
    "input_string, expected_sanitized_string",
    TEXT_INPUTS,
)
def test_sanitize_html(
    input_string: str,
    expected_sanitized_string,
):
    sanitized = sanitize_html(input_string)
    sanitized = (
        # remove leading/trailing whitespaces to keep test params compatible with API tests
        sanitized.strip()
    )
    assert sanitized == expected_sanitized_string


@pytest.mark.parametrize(
    "input_string, expected_sanitized_string",
    TEXT_INPUTS,
)
def test_input_model(
    input_string: str,
    expected_sanitized_string,
):
    obj = MockInput(
        title=input_string,
        whether="true",
        body=input_string,
        num="0",
        extra="extra property not in model",
        tags=[input_string, expected_sanitized_string],
    )
    assert obj.title == input_string.strip()
    assert obj.body == expected_sanitized_string
    assert obj.tags == [input_string.strip(), expected_sanitized_string]

    obj = MockInput(
        title=input_string,
        body=input_string,
    )
    assert obj.title == input_string.strip()
    assert obj.body == expected_sanitized_string
    assert obj.tags is None


def test_input_model_blocks_transactional_data():
    from pydantic import ValidationError

    # Legit design-time fields should be allowed
    try:
        MockInput(
            title="Valid title",
            body="Valid body",
            healthy_subject_indicator=True,
            patient_burden=1.5,
        )
    except ValidationError:
        pytest.fail("Legitimate design-time fields were incorrectly blocked")

    # Patient/Subject/Clinical execution parameters should be blocked
    with pytest.raises(ValidationError) as exc_info:
        MockInput(title="Valid title", body="Valid body", patient_id="12345")
    assert (
        "Static API schemas reject all incoming requests that contain patient, subject, or clinical execution parameters"
        in str(exc_info.value)
    )

    with pytest.raises(ValidationError) as exc_info:
        MockInput(
            title="Valid title", body="Valid body", subject_record={"id": "abc"}
        )
    assert (
        "Static API schemas reject all incoming requests that contain patient, subject, or clinical execution parameters"
        in str(exc_info.value)
    )

    with pytest.raises(ValidationError) as exc_info:
        MockInput(
            title="Valid title",
            body="Valid body",
            clinical_execution_data={"test": "abc"},
        )
    assert (
        "Static API schemas reject all incoming requests that contain patient, subject, or clinical execution parameters"
        in str(exc_info.value)
    )

