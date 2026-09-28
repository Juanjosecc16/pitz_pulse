"""Abstraction over language-model providers.

The service depends on this interface, not on a concrete SDK, so providers
(Anthropic, mock, others) can be swapped without touching the pipeline.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ClassificationPrompt:
    """Everything a client may need to classify one message."""

    system: str
    user: str
    message: str
    source_area: str | None = None


class LLMClient(ABC):
    @abstractmethod
    def complete(self, prompt: ClassificationPrompt) -> str:
        """Return the raw model output (expected to be a JSON object as text).

        Implementations must translate provider-specific failures into the
        exceptions defined in app.classifier.errors.
        """
