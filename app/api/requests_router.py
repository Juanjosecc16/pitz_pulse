"""HTTP endpoints for internal requests."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import get_request_service
from app.domain.enums import Category, Priority
from app.domain.models import RequestInput, StoredRequest
from app.services.request_service import RequestService

router = APIRouter(prefix="/solicitudes", tags=["solicitudes"])

ServiceDependency = Annotated[RequestService, Depends(get_request_service)]


@router.post("", status_code=status.HTTP_201_CREATED, response_model=StoredRequest)
def create_request(request_input: RequestInput, service: ServiceDependency) -> StoredRequest:
    """Classify a new internal request and store it."""
    return service.submit(request_input)


@router.get("", response_model=list[StoredRequest])
def list_requests(
    service: ServiceDependency,
    category: Annotated[Category | None, Query(alias="categoria")] = None,
    priority: Annotated[Priority | None, Query(alias="prioridad")] = None,
) -> list[StoredRequest]:
    """List stored requests, newest first. Filters use the same values as the JSON output."""
    return service.list(category=category, priority=priority)
