from datetime import datetime, timedelta, timezone

import pytest

from app.domain.enums import Category, Language, Priority, SuggestedArea
from app.domain.models import StoredRequest
from app.repository.sqlite_repository import SQLiteRequestRepository

BASE_TIME = datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc)


def build_request(request_id: str, category: Category, priority: Priority, minutes: int = 0) -> StoredRequest:
    return StoredRequest(
        id=request_id,
        category=category,
        priority=priority,
        suggested_area=SuggestedArea.BACKEND,
        language=Language.SPANISH,
        summary="Resumen de prueba.",
        needs_info=False,
        message="Mensaje original",
        source_area="Soporte MX",
        created_at=BASE_TIME + timedelta(minutes=minutes),
    )


@pytest.fixture
def repository(tmp_path) -> SQLiteRequestRepository:
    repository = SQLiteRequestRepository(tmp_path / "test.db")
    repository.initialize()
    return repository


def test_round_trip_keeps_every_field(repository):
    request = build_request("REQ-1", Category.BUG, Priority.HIGH)
    request.needs_info, request.follow_up_question = True, "¿Desde cuándo?"

    repository.save(request)

    assert repository.list() == [request]


def test_lists_newest_first(repository):
    repository.save(build_request("OLD", Category.BUG, Priority.HIGH, minutes=0))
    repository.save(build_request("NEW", Category.BUG, Priority.HIGH, minutes=5))

    assert [request.id for request in repository.list()] == ["NEW", "OLD"]


@pytest.mark.parametrize(
    ("category", "priority", "expected_ids"),
    [
        (Category.BUG, None, {"BUG-HIGH", "BUG-LOW"}),
        (None, Priority.HIGH, {"BUG-HIGH", "DATA-HIGH"}),
        (Category.BUG, Priority.LOW, {"BUG-LOW"}),
        (Category.ACCESS, None, set()),
    ],
)
def test_filters_by_category_and_priority(repository, category, priority, expected_ids):
    repository.save(build_request("BUG-HIGH", Category.BUG, Priority.HIGH))
    repository.save(build_request("BUG-LOW", Category.BUG, Priority.LOW))
    repository.save(build_request("DATA-HIGH", Category.DATA, Priority.HIGH))

    result = repository.list(category=category, priority=priority)

    assert {request.id for request in result} == expected_ids


def test_initialize_is_idempotent(repository):
    repository.initialize()

    assert repository.list() == []
