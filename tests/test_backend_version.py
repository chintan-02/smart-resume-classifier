import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_version_endpoint(client):
    response = client.get("/version")
    data = response.json()

    assert response.status_code == 200
    assert data.get("app_name") == "ResumeIQ"
    assert data.get("app_version")


def test_ready_reports_version_info(client):
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json().get("checks", {}).get("version_info") == "available"
