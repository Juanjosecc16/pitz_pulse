"""Orchestrates one classification: mask → prompt → model → parse, with retries."""

import logging
import time
from collections.abc import Callable

from app.classifier.base import LLMClient
from app.classifier.errors import (
    ClassificationFailedError,
    InvalidLLMResponseError,
    LLMProviderError,
    RetryableLLMError,
)
from app.classifier.parser import parse_classification
from app.classifier.prompt import build_prompt
from app.classifier.sanitizer import mask_sensitive_data
from app.domain.models import Classification

logger = logging.getLogger(__name__)


class ClassifierService:
    def __init__(
        self,
        client: LLMClient,
        max_retries: int = 2,
        mask_sensitive: bool = True,
        retry_base_delay_seconds: float = 1.0,
        sleep: Callable[[float], None] = time.sleep,
    ):
        self._client = client
        self._max_attempts = max_retries + 1
        self._mask_sensitive = mask_sensitive
        self._retry_base_delay = retry_base_delay_seconds
        self._sleep = sleep

    def classify(self, request_id: str, message: str, source_area: str | None = None) -> Classification:
        safe_message = mask_sensitive_data(message) if self._mask_sensitive else message
        previous_error: str | None = None
        last_error: Exception | None = None

        for attempt in range(1, self._max_attempts + 1):
            prompt = build_prompt(safe_message, source_area, previous_error)
            try:
                return parse_classification(self._client.complete(prompt), request_id)
            except InvalidLLMResponseError as error:
                previous_error = str(error)  # fed back to the model on the next attempt
                last_error = error
            except RetryableLLMError as error:
                last_error = error
            except LLMProviderError as error:
                raise ClassificationFailedError(f"{request_id}: {error}") from error

            logger.warning("Attempt %d/%d failed for %s: %s", attempt, self._max_attempts, request_id, last_error)
            if attempt < self._max_attempts:
                self._sleep(self._retry_base_delay * 2 ** (attempt - 1))

        raise ClassificationFailedError(
            f"{request_id}: could not classify after {self._max_attempts} attempts ({last_error})"
        ) from last_error
