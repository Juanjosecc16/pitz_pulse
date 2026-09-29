"""Translates classification failures into HTTP responses."""

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.classifier.errors import ClassificationFailedError, LLMTimeoutError, LLMUnavailableError

TEMPORARY_FAILURES = (LLMTimeoutError, LLMUnavailableError)


def status_code_for(error: ClassificationFailedError) -> int:
    """503 when the provider is temporarily unreachable (retry later); 502 for any other upstream failure."""
    if isinstance(error.__cause__, TEMPORARY_FAILURES):
        return status.HTTP_503_SERVICE_UNAVAILABLE
    return status.HTTP_502_BAD_GATEWAY


async def classification_failed_handler(_: Request, error: ClassificationFailedError) -> JSONResponse:
    return JSONResponse(
        status_code=status_code_for(error),
        content={"detail": f"No se pudo clasificar la solicitud: {error}"},
    )
