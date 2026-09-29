import inspect
from types import SimpleNamespace

import anthropic
import httpx2
import pytest

from app.classifier.anthropic_client import AnthropicClient
from app.classifier.errors import (
    InvalidLLMResponseError,
    LLMProviderError,
    LLMTimeoutError,
    LLMUnavailableError,
)
from app.classifier.prompt import build_prompt

REQUEST = httpx2.Request("POST", "https://api.anthropic.com/v1/messages")


def status_error(error_class, status_code: int):
    return error_class("error", response=httpx2.Response(status_code, request=REQUEST), body=None)


def fake_response(text: str = '{"ok": true}', stop_reason: str = "end_turn"):
    return SimpleNamespace(stop_reason=stop_reason, content=[SimpleNamespace(type="text", text=text)])


@pytest.fixture
def client() -> AnthropicClient:
    return AnthropicClient(api_key="test-key", model="claude-haiku-4-5", temperature=0.0, timeout_seconds=5)


def stub_create(monkeypatch, client: AnthropicClient, result) -> dict:
    """Replace messages.create, rejecting any argument the real SDK signature would reject."""
    captured: dict = {}
    real_signature = inspect.signature(client._client.messages.create)

    def create(**kwargs):
        real_signature.bind(**kwargs)
        captured.update(kwargs)
        if isinstance(result, Exception):
            raise result
        return result

    monkeypatch.setattr(client._client.messages, "create", create)
    return captured


def test_sends_temperature_schema_and_prompts(monkeypatch, client):
    captured = stub_create(monkeypatch, client, fake_response())

    assert client.complete(build_prompt("Hola")) == '{"ok": true}'
    assert captured["extra_body"] == {"temperature": 0.0}
    assert captured["model"] == "claude-haiku-4-5"
    assert captured["output_config"]["format"]["type"] == "json_schema"
    assert "<mensaje>" in captured["messages"][0]["content"]


@pytest.mark.parametrize(
    ("sdk_error", "expected_error"),
    [
        (anthropic.APITimeoutError(request=REQUEST), LLMTimeoutError),
        (anthropic.APIConnectionError(request=REQUEST), LLMUnavailableError),
        (status_error(anthropic.RateLimitError, 429), LLMUnavailableError),
        (status_error(anthropic.InternalServerError, 500), LLMUnavailableError),
        (status_error(anthropic.AuthenticationError, 401), LLMProviderError),
        (status_error(anthropic.BadRequestError, 400), LLMProviderError),
    ],
)
def test_translates_sdk_errors(monkeypatch, client, sdk_error, expected_error):
    stub_create(monkeypatch, client, sdk_error)

    with pytest.raises(expected_error):
        client.complete(build_prompt("Hola"))


@pytest.mark.parametrize(
    "response",
    [fake_response(stop_reason="max_tokens"), fake_response(stop_reason="refusal"), fake_response(text="  ")],
)
def test_rejects_unusable_responses(monkeypatch, client, response):
    stub_create(monkeypatch, client, response)

    with pytest.raises(InvalidLLMResponseError):
        client.complete(build_prompt("Hola"))
