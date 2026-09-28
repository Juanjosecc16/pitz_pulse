import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.batch import BatchMessage, classify_messages, load_messages, write_results
from app.classifier.errors import LLMProviderError
from app.classifier.mock_client import MockLLMClient
from app.classifier.service import ClassifierService
from tests.fakes import ScriptedLLMClient, valid_llm_output_text

ANNEX_PATH = Path(__file__).parents[1] / "data" / "mensajes.json"


def test_loads_the_twelve_annex_messages():
    messages = load_messages(ANNEX_PATH)

    assert [message.id for message in messages] == [f"MSG-{number:02d}" for number in range(1, 13)]


def test_rejects_messages_without_id(tmp_path):
    path = tmp_path / "messages.json"
    path.write_text(json.dumps([{"message": "Hola"}]), encoding="utf-8")

    with pytest.raises(ValidationError):
        load_messages(path)


def test_classifies_all_annex_messages_with_mock():
    service = ClassifierService(MockLLMClient(), max_retries=0)

    result = classify_messages(service, load_messages(ANNEX_PATH))

    assert len(result.classifications) == 12
    assert result.failed_ids == []


def test_a_failed_message_does_not_stop_the_batch():
    client = ScriptedLLMClient(LLMProviderError("boom"), valid_llm_output_text())
    service = ClassifierService(client, max_retries=0)
    messages = [BatchMessage(id="A", message="uno"), BatchMessage(id="B", message="dos")]

    result = classify_messages(service, messages)

    assert result.failed_ids == ["A"]
    assert [classification.id for classification in result.classifications] == ["B"]


def test_writes_results_with_spanish_keys_and_utf8(tmp_path):
    service = ClassifierService(ScriptedLLMClient(valid_llm_output_text(resumen="Catálogo con error")), max_retries=0)
    classification = service.classify("MSG-01", "Error 500")
    output_path = tmp_path / "resultados.json"

    write_results(output_path, [classification])

    content = output_path.read_text(encoding="utf-8")
    assert "Catálogo" in content
    assert json.loads(content)[0]["categoria"] == "bug"
