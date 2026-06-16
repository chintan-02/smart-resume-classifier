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
    assert data.get("app_stage")
    assert data.get("deployment_env")
    assert data.get("git_commit")
    assert "build_label" not in data
    assert "secret" not in str(data).lower()
    assert "api_key" not in str(data).lower()
    assert "password" not in str(data).lower()


def test_ready_reports_version_info(client):
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json().get("checks", {}).get("version_info") == "available"
