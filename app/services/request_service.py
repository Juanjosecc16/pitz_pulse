"""Use cases of the API: submit a request (classify + store) and list requests."""

import uuid
from collections.abc import Callable
from datetime import datetime, timezone

from app.classifier.service import ClassifierService
from app.domain.enums import Category, Priority
from app.domain.models import RequestInput, StoredRequest
from app.repository.base import RequestRepository


def generate_request_id() -> str:
    return f"REQ-{uuid.uuid4().hex[:8].upper()}"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RequestService:
    def __init__(
        self,
        classifier: ClassifierService,
        repository: RequestRepository,
        id_factory: Callable[[], str] = generate_request_id,
        clock: Callable[[], datetime] = utc_now,
    ):
        self._classifier = classifier
        self._repository = repository
        self._id_factory = id_factory
        self._clock = clock

    def submit(self, request_input: RequestInput) -> StoredRequest:
        """Classify a new request and persist it. Raises ClassificationFailedError on LLM failure."""
        request_id = self._id_factory()
        classification = self._classifier.classify(request_id, request_input.message, request_input.source_area)
        stored_request = StoredRequest(
            **classification.model_dump(by_alias=False),
            message=request_input.message,
            source_area=request_input.source_area,
            created_at=self._clock(),
        )
        self._repository.save(stored_request)
        return stored_request

    def list(self, category: Category | None = None, priority: Priority | None = None) -> list[StoredRequest]:
        return self._repository.list(category=category, priority=priority)
