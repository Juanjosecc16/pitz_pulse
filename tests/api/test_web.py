import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


def test_root_serves_the_web_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert 'id="request-form"' in response.text


@pytest.mark.parametrize("asset", ["/static/app.js", "/static/styles.css"])
def test_serves_static_assets(client, asset):
    assert client.get(asset).status_code == 200
