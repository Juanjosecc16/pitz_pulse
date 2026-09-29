"""Smoke tests against the real LLM provider configured in .env.

Excluded from the default run. Execute with: python -m pytest -m live
Assertions are deliberately loose: they check the integration works and the
obvious cases are right, not the exact wording chosen by the model.
"""

import pytest

from app.classifier.factory import create_classifier_service
from app.core.config import get_settings
from app.domain.enums import Category, Language, Priority
from app.domain.models import MAX_SUMMARY_WORDS

pytestmark = pytest.mark.live


@pytest.fixture(scope="module")
def service():
    settings = get_settings()
    if settings.llm_provider == "mock":
        pytest.skip("LLM_PROVIDER=mock: set LLM_PROVIDER=anthropic and ANTHROPIC_API_KEY in .env")
    return create_classifier_service(settings)


def test_classifies_clear_spanish_bug(service):
    classification = service.classify(
        "MSG-01",
        "Hola equipo, un vendedor de Guadalajara dice que desde ayer no puede subir su catálogo, "
        "le sale error 500 al cargar el Excel. Tiene una campaña que arranca el lunes.",
        "Comercial MX",
    )

    assert classification.category is Category.BUG
    assert classification.priority is Priority.HIGH
    assert classification.language is Language.SPANISH
    assert len(classification.summary.split()) <= MAX_SUMMARY_WORDS


def test_detects_portuguese_and_summarizes_in_spanish(service):
    classification = service.classify(
        "MSG-02",
        "Oi pessoal, preciso de uma planilha com todas as vendas de agosto por estado, "
        "com o valor total e a comissão da Pitz. É para o fechamento do mês até sexta.",
        "Financeiro BR",
    )

    assert classification.category is Category.DATA
    assert classification.language is Language.PORTUGUESE
    assert "planilha" not in classification.summary.lower()


def test_asks_follow_up_for_vague_message(service):
    classification = service.classify("MSG-09", "Oigan, la plataforma está lenta.", "Operaciones MX")

    assert classification.needs_info is True
    assert classification.follow_up_question
