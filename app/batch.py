"""Batch classification of a JSON file of messages (used for Annex A)."""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

from pydantic import Field, TypeAdapter

from app.classifier.errors import ClassificationFailedError
from app.classifier.service import ClassifierService
from app.domain.models import Classification, RequestInput

logger = logging.getLogger(__name__)


class BatchMessage(RequestInput):
    """A message to classify that already comes with its own id."""

    id: str = Field(min_length=1)


@dataclass
class BatchResult:
    classifications: list[Classification] = field(default_factory=list)
    failed_ids: list[str] = field(default_factory=list)


def load_messages(path: Path) -> list[BatchMessage]:
    raw_messages = json.loads(path.read_text(encoding="utf-8"))
    return TypeAdapter(list[BatchMessage]).validate_python(raw_messages)


def classify_messages(service: ClassifierService, messages: list[BatchMessage]) -> BatchResult:
    """Classify every message; a failure is logged and does not stop the batch."""
    result = BatchResult()
    for message in messages:
        try:
            result.classifications.append(service.classify(message.id, message.message, message.source_area))
            logger.info("Classified %s", message.id)
        except ClassificationFailedError as error:
            logger.error("Failed %s: %s", message.id, error)
            result.failed_ids.append(message.id)
    return result


def write_results(path: Path, classifications: list[Classification]) -> None:
    payload = [classification.model_dump(mode="json") for classification in classifications]
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
