import pytest

from app.classifier.errors import (
    ClassificationFailedError,
    LLMProviderError,
    LLMTimeoutError,
    LLMUnavailableError,
)
from app.classifier.service import ClassifierService
from tests.fakes import ScriptedLLMClient, valid_llm_output_text


def build_service(client: ScriptedLLMClient, max_retries: int = 2, **kwargs) -> tuple[ClassifierService, list]:
    delays: list[float] = []
    service = ClassifierService(client, max_retries=max_retries, sleep=delays.append, **kwargs)
    return service, delays


def test_returns_classification_on_first_attempt():
    client = ScriptedLLMClient(valid_llm_output_text())
    service, delays = build_service(client)

    classification = service.classify("MSG-01", "Error 500 al subir catálogo", "Comercial MX")

    assert classification.id == "MSG-01"
    assert len(client.prompts) == 1
    assert delays == []


def test_retries_invalid_output_and_feeds_error_back_to_model():
    client = ScriptedLLMClient("not json", valid_llm_output_text())
    service, _ = build_service(client)

    service.classify("MSG-01", "Error 500")

    assert len(client.prompts) == 2
    assert "Tu respuesta anterior fue inválida" in client.prompts[1].user


@pytest.mark.parametrize("transient_error", [LLMTimeoutError("timeout"), LLMUnavailableError("503")])
def test_retries_transient_errors_with_exponential_backoff(transient_error):
    client = ScriptedLLMClient(transient_error, transient_error, valid_llm_output_text())
    service, delays = build_service(client, retry_base_delay_seconds=1.0)

    service.classify("MSG-01", "Error 500")

    assert delays == [1.0, 2.0]


def test_fails_after_exhausting_retries():
    client = ScriptedLLMClient(LLMTimeoutError("timeout"), "not json", "still not json")
    service, _ = build_service(client, max_retries=2)

    with pytest.raises(ClassificationFailedError, match="after 3 attempts"):
        service.classify("MSG-01", "Error 500")


def test_does_not_retry_provider_errors():
    client = ScriptedLLMClient(LLMProviderError("invalid api key"), valid_llm_output_text())
    service, _ = build_service(client)

    with pytest.raises(ClassificationFailedError, match="invalid api key"):
        service.classify("MSG-01", "Error 500")
    assert len(client.prompts) == 1


def test_masks_sensitive_data_before_calling_model():
    client = ScriptedLLMClient(valid_llm_output_text())
    service, _ = build_service(client, mask_sensitive=True)

    service.classify("MSG-08", "Nota fiscal com CNPJ 12.345.678/0001-90 errado")

    assert "12.345.678/0001-90" not in client.prompts[0].user
    assert "[CNPJ]" in client.prompts[0].user


def test_masking_can_be_disabled():
    client = ScriptedLLMClient(valid_llm_output_text())
    service, _ = build_service(client, mask_sensitive=False)

    service.classify("MSG-08", "CNPJ 12.345.678/0001-90")

    assert "12.345.678/0001-90" in client.prompts[0].user
