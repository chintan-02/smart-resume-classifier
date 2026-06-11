import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from backend.main import app
from backend.routers import analyze


def _fake_analysis_response(*args, **kwargs):
    return {
        "status": "success",
        "predicted_role": "Data Scientist",
        "model_confidence": 88.0,
        "ats_score": 76.0,
        "jd_match_score": 0.62,
        "matched_skills": ["python", "sql"],
        "missing_skills": ["statistics"],
        "priority_actions": ["Review combined signals before making decisions."],
        "privacy_mode": kwargs.get("privacy_mode", False),
        "disclaimer": "ResumeIQ is a decision-support tool. This API response is not a hiring decision.",
    }


def test_root_endpoint():
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "ResumeIQ API" in response.json().get("app", "")


def test_health_endpoint():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json().get("status") == "ok"


def test_ready_endpoint():
    client = TestClient(app)

    response = client.get("/ready")

    assert response.status_code == 200
    assert "checks" in response.json()


def test_analyze_resume_endpoint_valid_body(monkeypatch):
    monkeypatch.setattr(analyze, "analyze_resume_text", _fake_analysis_response)
    monkeypatch.setattr(analyze, "_save_successful_analysis", lambda *args, **kwargs: None)
    client = TestClient(app)

    response = client.post(
        "/analyze-resume",
        json={
            "resume_text": "Python developer with SQL, machine learning, FastAPI, analytics, and deployment experience.",
            "job_description": "Need a data scientist with Python, SQL, statistics, and deployment skills.",
            "privacy_mode": False,
        },
    )

    data = response.json()
    assert response.status_code == 200
    assert data.get("status") == "success"
    assert "disclaimer" in data
    assert "Traceback" not in str(data)


def test_analyze_resume_endpoint_rejects_short_resume_text():
    client = TestClient(app)

    response = client.post(
        "/analyze-resume",
        json={
            "resume_text": "Too short",
            "job_description": "Need Python and SQL skills.",
            "privacy_mode": False,
        },
    )

    assert response.status_code == 422
