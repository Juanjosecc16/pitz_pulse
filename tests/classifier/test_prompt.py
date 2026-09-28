import pytest

from app.classifier.prompt import (
    AREA_DESCRIPTIONS,
    CATEGORY_DESCRIPTIONS,
    PRIORITY_DESCRIPTIONS,
    SYSTEM_PROMPT,
    build_prompt,
)
from app.classifier.schema import CLASSIFICATION_OUTPUT_SCHEMA
from app.domain.enums import Category, Priority, SuggestedArea


@pytest.mark.parametrize(
    ("enum_class", "descriptions"),
    [(Category, CATEGORY_DESCRIPTIONS), (Priority, PRIORITY_DESCRIPTIONS), (SuggestedArea, AREA_DESCRIPTIONS)],
)
def test_every_allowed_value_is_described_in_system_prompt(enum_class, descriptions):
    assert set(descriptions) == set(enum_class)
    for member in enum_class:
        assert f"- {member.value}:" in SYSTEM_PROMPT


def test_schema_enums_match_domain_enums():
    properties = CLASSIFICATION_OUTPUT_SCHEMA["properties"]

    assert properties["categoria"]["enum"] == [member.value for member in Category]
    assert properties["area_sugerida"]["enum"] == [member.value for member in SuggestedArea]


def test_user_prompt_wraps_message_and_includes_source_area():
    prompt = build_prompt("Oigan, la plataforma está lenta.", "Operaciones MX")

    assert "<mensaje>\nOigan, la plataforma está lenta.\n</mensaje>" in prompt.user
    assert "Operaciones MX" in prompt.user
    assert "inválida" not in prompt.user


def test_user_prompt_includes_feedback_on_retry():
    prompt = build_prompt("Hola", previous_error="resumen: too long")

    assert "resumen: too long" in prompt.user
    assert "no informada" in prompt.user
