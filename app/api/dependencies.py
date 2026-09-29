"""FastAPI dependencies. Tests replace them through app.dependency_overrides."""

from functools import lru_cache

from app.classifier.factory import create_classifier_service
from app.core.config import get_settings
from app.repository.base import RequestRepository
from app.repository.sqlite_repository import SQLiteRequestRepository
from app.services.request_service import RequestService


@lru_cache
def get_repository() -> RequestRepository:
    return SQLiteRequestRepository(get_settings().database_file)


@lru_cache
def get_request_service() -> RequestService:
    return RequestService(classifier=create_classifier_service(), repository=get_repository())
