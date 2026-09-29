"""LLMClient implementation backed by the Anthropic Messages API."""

import anthropic

from app.classifier.base import ClassificationPrompt, LLMClient
from app.classifier.errors import (
    InvalidLLMResponseError,
    LLMProviderError,
    LLMTimeoutError,
    LLMUnavailableError,
)
from app.classifier.schema import CLASSIFICATION_OUTPUT_SCHEMA

# A classification is ~150 output tokens; the margin avoids truncated JSON.
MAX_OUTPUT_TOKENS = 1024


class AnthropicClient(LLMClient):
    def __init__(self, api_key: str, model: str, temperature: float, timeout_seconds: float):
        # SDK retries are disabled: ClassifierService owns the single retry policy.
        self._client = anthropic.Anthropic(api_key=api_key, timeout=timeout_seconds, max_retries=0)
        self._model = model
        self._temperature = temperature

    def complete(self, prompt: ClassificationPrompt) -> str:
        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=MAX_OUTPUT_TOKENS,
                system=prompt.system,
                messages=[{"role": "user", "content": prompt.user}],
                output_config={"format": {"type": "json_schema", "schema": CLASSIFICATION_OUTPUT_SCHEMA}},
                # SDK 1.x dropped the sampling keyword arguments because newer models reject them;
                # Haiku 4.5 still accepts temperature, so it is sent as a raw body field.
                extra_body={"temperature": self._temperature},
            )
        except anthropic.APITimeoutError as error:
            raise LLMTimeoutError("the model did not answer in time") from error
        except (anthropic.APIConnectionError, anthropic.RateLimitError, anthropic.InternalServerError) as error:
            raise LLMUnavailableError(f"provider temporarily unavailable: {error}") from error
        except anthropic.APIStatusError as error:
            raise LLMProviderError(f"provider rejected the request ({error.status_code}): {error.message}") from error

        return self._extract_text(response)

    @staticmethod
    def _extract_text(response) -> str:
        if response.stop_reason == "max_tokens":
            raise InvalidLLMResponseError("the response was truncated (max_tokens reached)")
        if response.stop_reason == "refusal":
            raise InvalidLLMResponseError("the model refused to classify the message")

        text = "".join(block.text for block in response.content if block.type == "text")
        if not text.strip():
            raise InvalidLLMResponseError("the model returned an empty response")
        return text
