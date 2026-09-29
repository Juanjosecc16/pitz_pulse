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


@pytest.mark.parametrize(
    "asset",
    [
        "/static/styles.css",
        "/static/js/main.js",
        "/static/js/api.js",
        "/static/js/labels.js",
        "/static/js/render.js",
        "/static/js/form-view.js",
        "/static/js/list-view.js",
        "/static/js/tabs.js",
    ],
)
def test_serves_static_assets(client, asset):
    assert client.get(asset).status_code == 200
