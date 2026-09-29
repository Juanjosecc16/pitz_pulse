"""Storage abstraction for classified requests."""

from abc import ABC, abstractmethod

from app.domain.enums import Category, Priority
from app.domain.models import StoredRequest


class RequestRepository(ABC):
    @abstractmethod
    def initialize(self) -> None:
        """Create the storage structures if they do not exist yet."""

    @abstractmethod
    def save(self, request: StoredRequest) -> None:
        """Persist a classified request."""

    @abstractmethod
    def list(self, category: Category | None = None, priority: Priority | None = None) -> list[StoredRequest]:
        """Return stored requests, newest first, optionally filtered."""
