import pytest
from pydantic import ValidationError

from app.domain.enums import Category, Language, Priority, SuggestedArea
from app.domain.models import MAX_SUMMARY_WORDS, Classification


@pytest.fixture
def valid_payload() -> dict:
    """Example output from Annex B of the case specification."""
    return {
        "id": "MSG-01",
        "categoria": "bug",
        "prioridad": "alta",
        "area_sugerida": "backend",
        "idioma": "es",
        "resumen": "Vendedor de Guadalajara recibe error 500 al subir su catálogo en Excel; campaña empieza el lunes.",
        "requiere_info": True,
        "pregunta_seguimiento": "¿Nos compartes el nombre del vendedor y el archivo que intentó subir?",
    }


def test_parses_spanish_keys_into_english_attributes(valid_payload):
    classification = Classification.model_validate(valid_payload)

    assert classification.category is Category.BUG
    assert classification.priority is Priority.HIGH
    assert classification.suggested_area is SuggestedArea.BACKEND
    assert classification.language is Language.SPANISH
    assert classification.needs_info is True


def test_serializes_with_spanish_keys_and_values(valid_payload):
    classification = Classification.model_validate(valid_payload)

    assert classification.model_dump(mode="json") == valid_payload


def test_accepts_english_attribute_names():
    classification = Classification(
        id="MSG-11",
        category=Category.QUESTION,
        priority=Priority.LOW,
        suggested_area=SuggestedArea.PRODUCT,
        language=Language.PORTUGUESE,
        summary="Diferencia entre plan básico y plan pro para vendedores.",
        needs_info=False,
    )

    assert classification.model_dump(mode="json")["categoria"] == "consulta"


@pytest.mark.parametrize(
    ("field", "invalid_value"),
    [
        ("categoria", "incidente"),
        ("prioridad", "urgente"),
        ("area_sugerida", "soporte"),
        ("idioma", "en"),
    ],
)
def test_rejects_values_outside_allowed_set(valid_payload, field, invalid_value):
    valid_payload[field] = invalid_value

    with pytest.raises(ValidationError):
        Classification.model_validate(valid_payload)


@pytest.mark.parametrize("missing_field", ["id", "categoria", "prioridad", "resumen", "requiere_info"])
def test_rejects_missing_required_field(valid_payload, missing_field):
    del valid_payload[missing_field]

    with pytest.raises(ValidationError):
        Classification.model_validate(valid_payload)


def test_accepts_summary_at_word_limit(valid_payload):
    valid_payload["resumen"] = " ".join(["palabra"] * MAX_SUMMARY_WORDS)

    assert Classification.model_validate(valid_payload)


def test_rejects_summary_over_word_limit(valid_payload):
    valid_payload["resumen"] = " ".join(["palabra"] * (MAX_SUMMARY_WORDS + 1))

    with pytest.raises(ValidationError, match="maximum is 20"):
        Classification.model_validate(valid_payload)


def test_rejects_blank_summary(valid_payload):
    valid_payload["resumen"] = "   "

    with pytest.raises(ValidationError):
        Classification.model_validate(valid_payload)


@pytest.mark.parametrize("question", [None, "", "   "])
def test_requires_follow_up_question_when_info_is_needed(valid_payload, question):
    valid_payload["pregunta_seguimiento"] = question

    with pytest.raises(ValidationError, match="follow_up_question is required"):
        Classification.model_validate(valid_payload)


def test_drops_follow_up_question_when_info_is_not_needed(valid_payload):
    valid_payload["requiere_info"] = False

    classification = Classification.model_validate(valid_payload)

    assert classification.follow_up_question is None
