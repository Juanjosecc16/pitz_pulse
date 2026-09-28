"""Builds the classifier according to the configuration."""

from app.classifier.base import LLMClient
from app.classifier.mock_client import MockLLMClient
from app.classifier.service import ClassifierService
from app.core.config import Settings, get_settings


def create_llm_client(settings: Settings) -> LLMClient:
    if settings.llm_provider == "anthropic":
        from app.classifier.anthropic_client import AnthropicClient  # SDK is only loaded when needed

        return AnthropicClient(
            api_key=settings.anthropic_api_key.get_secret_value(),
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            timeout_seconds=settings.llm_timeout_seconds,
        )
    return MockLLMClient()


def create_classifier_service(settings: Settings | None = None) -> ClassifierService:
    settings = settings or get_settings()
    return ClassifierService(
        client=create_llm_client(settings),
        max_retries=settings.llm_max_retries,
        mask_sensitive=settings.mask_sensitive_data,
    )
