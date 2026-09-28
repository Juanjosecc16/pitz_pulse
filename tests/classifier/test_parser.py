import pytest

from app.classifier.errors import InvalidLLMResponseError
from app.classifier.parser import parse_classification
from app.domain.enums import Category
from tests.fakes import valid_llm_output_text


def test_parses_plain_json():
    classification = parse_classification(valid_llm_output_text(), "MSG-01")

    assert classification.id == "MSG-01"
    assert classification.category is Category.BUG


@pytest.mark.parametrize(
    "wrapper",
    ["```json\n{}\n```", "```\n{}\n```", "Aquí está la clasificación:\n{}\nSaludos."],
)
def test_extracts_json_wrapped_in_text_or_code_fences(wrapper):
    raw_output = wrapper.replace("{}", valid_llm_output_text())

    assert parse_classification(raw_output, "MSG-01").category is Category.BUG


def test_request_id_always_comes_from_caller():
    raw_output = valid_llm_output_text(id="INVENTED-BY-MODEL")

    assert parse_classification(raw_output, "MSG-07").id == "MSG-07"


@pytest.mark.parametrize(
    ("raw_output", "expected_message"),
    [
        ("no json here", "does not contain a JSON object"),
        ('{"categoria": "bug",}', "not valid JSON"),
        ("[1, 2, 3]", "does not contain a JSON object"),
    ],
)
def test_rejects_malformed_output(raw_output, expected_message):
    with pytest.raises(InvalidLLMResponseError, match=expected_message):
        parse_classification(raw_output, "MSG-01")


def test_rejects_values_outside_allowed_set_with_field_name():
    with pytest.raises(InvalidLLMResponseError, match="categoria"):
        parse_classification(valid_llm_output_text(categoria="incidente"), "MSG-01")
