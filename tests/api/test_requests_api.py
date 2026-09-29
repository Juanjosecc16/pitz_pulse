import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_repository, get_request_service
from app.classifier.base import LLMClient
from app.classifier.errors import InvalidLLMResponseError, LLMProviderError, LLMTimeoutError
from app.classifier.mock_client import MockLLMClient
from app.classifier.service import ClassifierService
from app.main import create_app
from app.repository.sqlite_repository import SQLiteRequestRepository
from app.services.request_service import RequestService
from tests.fakes import ScriptedLLMClient

BUG_MESSAGE = {"message": "Hola, le sale error 500 al cargar el Excel.", "source_area": "Comercial MX"}
DATA_MESSAGE = {"message": "Oi pessoal, preciso de uma planilha com as vendas.", "source_area": "Financeiro BR"}


def build_client(tmp_path, llm_client: LLMClient) -> TestClient:
    repository = SQLiteRequestRepository(tmp_path / "api.db")
    service = RequestService(ClassifierService(llm_client, max_retries=0), repository)
    app = create_app()
    app.dependency_overrides[get_repository] = lambda: repository
    app.dependency_overrides[get_request_service] = lambda: service
    return TestClient(app)


@pytest.fixture
def client(tmp_path):
    with build_client(tmp_path, MockLLMClient()) as test_client:
        yield test_client


def test_health(client):
    assert client.get("/health").json()["status"] == "ok"


def test_post_classifies_and_returns_stored_request(client):
    response = client.post("/solicitudes", json=BUG_MESSAGE)

    assert response.status_code == 201
    body = response.json()
    assert body["id"].startswith("REQ-")
    assert body["categoria"] == "bug"
    assert body["prioridad"] == "alta"
    assert body["message"] == BUG_MESSAGE["message"]
    assert "created_at" in body


def test_posted_requests_are_listed_newest_first(client):
    first = client.post("/solicitudes", json=BUG_MESSAGE).json()
    second = client.post("/solicitudes", json=DATA_MESSAGE).json()

    listed_ids = [request["id"] for request in client.get("/solicitudes").json()]

    assert listed_ids == [second["id"], first["id"]]


@pytest.mark.parametrize(
    ("query", "expected_categories"),
    [
        ("?categoria=bug", ["bug"]),
        ("?prioridad=media", ["datos"]),
        ("?categoria=datos&prioridad=media", ["datos"]),
        ("?categoria=acceso", []),
    ],
)
def test_filters_by_category_and_priority(client, query, expected_categories):
    client.post("/solicitudes", json=BUG_MESSAGE)
    client.post("/solicitudes", json=DATA_MESSAGE)

    response = client.get(f"/solicitudes{query}")

    assert [request["categoria"] for request in response.json()] == expected_categories


@pytest.mark.parametrize("query", ["?categoria=incidente", "?prioridad=urgente"])
def test_rejects_unknown_filter_values(client, query):
    assert client.get(f"/solicitudes{query}").status_code == 422


@pytest.mark.parametrize("payload", [{}, {"message": ""}, {"message": "   "}, {"source_area": "Soporte"}])
def test_rejects_invalid_payload(client, payload):
    assert client.post("/solicitudes", json=payload).status_code == 422


@pytest.mark.parametrize(
    ("llm_error", "expected_status"),
    [
        (LLMTimeoutError("timeout"), 503),
        (InvalidLLMResponseError("bad json"), 502),
        (LLMProviderError("invalid api key"), 502),
    ],
)
def test_llm_failures_map_to_gateway_errors_and_store_nothing(tmp_path, llm_error, expected_status):
    with build_client(tmp_path, ScriptedLLMClient(llm_error)) as client:
        response = client.post("/solicitudes", json=BUG_MESSAGE)

        assert response.status_code == expected_status
        assert "No se pudo clasificar" in response.json()["detail"]
        assert client.get("/solicitudes").json() == []
