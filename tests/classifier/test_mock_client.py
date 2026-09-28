import json
from pathlib import Path

import pytest

from app.classifier.mock_client import MockLLMClient
from app.classifier.service import ClassifierService
from app.domain.enums import Category, Language, Priority

ANNEX_MESSAGES = json.loads((Path(__file__).parents[2] / "data" / "mensajes.json").read_text(encoding="utf-8"))


@pytest.fixture
def service() -> ClassifierService:
    return ClassifierService(MockLLMClient(), max_retries=0)


@pytest.mark.parametrize("annex_message", ANNEX_MESSAGES, ids=lambda message: message["id"])
def test_mock_output_passes_validation_for_every_annex_message(service, annex_message):
    classification = service.classify(annex_message["id"], annex_message["message"], annex_message["source_area"])

    assert classification.id == annex_message["id"]


@pytest.mark.parametrize(
    ("message", "category", "priority", "language"),
    [
        ("Hola, le sale error 500 al cargar el Excel.", Category.BUG, Priority.HIGH, Language.SPANISH),
        ("Oi pessoal, preciso de uma planilha com as vendas.", Category.DATA, Priority.MEDIUM, Language.PORTUGUESE),
        ("Me pueden dar acceso al panel?", Category.ACCESS, Priority.MEDIUM, Language.SPANISH),
        ("Qual é a diferença entre os planos? Não soube explicar.", Category.QUESTION, Priority.LOW, Language.PORTUGUESE),
    ],
)
def test_mock_keyword_rules(service, message, category, priority, language):
    classification = service.classify("TEST", message)

    assert (classification.category, classification.priority, classification.language) == (category, priority, language)


def test_mock_asks_for_more_info_on_vague_messages(service):
    classification = service.classify("MSG-09", "Oigan, la plataforma está lenta.")

    assert classification.needs_info is True
    assert classification.follow_up_question
