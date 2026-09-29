"""FastAPI application entry point: uvicorn app.main:app --reload"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.dependencies import get_repository
from app.api.errors import classification_failed_handler
from app.api.requests_router import router as requests_router
from app.classifier.errors import ClassificationFailedError
from app.core.config import get_settings

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Resolve through dependency_overrides so tests initialize their own temporary database.
    repository_provider = app.dependency_overrides.get(get_repository, get_repository)
    repository_provider().initialize()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Pitz Pulse",
        description="Triage inteligente de solicitudes internas.",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.include_router(requests_router)
    app.add_exception_handler(ClassificationFailedError, classification_failed_handler)
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/", include_in_schema=False)
    def web_page() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/health", tags=["health"])
    def health() -> dict:
        return {"status": "ok", "llm_provider": get_settings().llm_provider}

    return app


app = create_app()
