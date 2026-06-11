import pytest
from sqlalchemy import create_engine

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from backend.main import app
from backend.routers import analyze
from backend.routers import health


class _FakeDbSession:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False


def _fake_analysis_response(*args, **kwargs):
    job_description = kwargs.get("job_description") or ""
    priority_actions = ["Review combined signals before making decisions."]
    ats_score = 76.0
    jd_match_score = 0.62
    if not job_description.strip():
        ats_score = None
        jd_match_score = None
        priority_actions.append("Add a job description to calculate job-match signals.")

    return {
        "status": "success",
        "predicted_role": "Data Scientist",
        "model_confidence": 88.0,
        "ats_score": ats_score,
        "jd_match_score": jd_match_score,
        "matched_skills": ["python", "sql"],
        "missing_skills": ["statistics"],
        "priority_actions": priority_actions,
        "privacy_mode": kwargs.get("privacy_mode", False),
        "disclaimer": "ResumeIQ is a decision-support tool. This API response is not a hiring decision.",
    }


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def disable_backend_db_writes(monkeypatch):
    monkeypatch.setattr(analyze, "_save_successful_analysis", lambda *args, **kwargs: None)
    monkeypatch.setattr(analyze, "_save_failed_api_request", lambda *args, **kwargs: None)


@pytest.fixture
def temp_ready_database(monkeypatch, tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'backend_ready_test.db'}")
    monkeypatch.setattr(health, "engine", engine)
    return engine


def test_root_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json().get("app") == "ResumeIQ API"
    assert response.json().get("status") == "running"


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json().get("status") == "ok"
    assert response.json().get("service") == "ResumeIQ API"
    assert response.headers.get("x-request-id")
    assert response.headers.get("x-process-time-ms") is not None


def test_ready_endpoint(client, temp_ready_database):
    response = client.get("/ready")
    data = response.json()
    checks = data.get("checks", {})

    assert response.status_code == 200
    assert "checks" in data
    assert "api" in checks
    assert checks.get("database") in {"available", "not_initialized", "unavailable"}
    assert checks.get("logging") == "enabled"
    assert checks.get("monitoring") == "local_foundation"
    assert checks.get("rag_copilot") == "available"


def test_analyze_resume_success(monkeypatch, client, disable_backend_db_writes):
    resume_text = "Python developer with SQL, machine learning, FastAPI, Streamlit, and analytics project experience."
    job_description = "We need a data scientist with Python, SQL, statistics, machine learning, and deployment skills."
    monkeypatch.setattr(analyze, "analyze_resume_text", _fake_analysis_response)

    response = client.post(
        "/analyze-resume",
        json={
            "resume_text": resume_text,
            "job_description": job_description,
            "privacy_mode": False,
        },
    )

    data = response.json()
    assert response.status_code == 200
    assert "status" in data
    assert "disclaimer" in data
    assert isinstance(data.get("priority_actions"), list)
    assert "resume_text" not in data
    assert "job_description" not in data
    assert resume_text not in str(data)
    assert job_description not in str(data)
    assert "Traceback" not in str(data)


def test_analyze_resume_validation_error(client):
    response = client.post(
        "/analyze-resume",
        json={
            "resume_text": "Too short",
            "job_description": "Need Python and SQL skills.",
            "privacy_mode": False,
        },
    )

    assert response.status_code == 422


def test_analyze_resume_no_jd(monkeypatch, client, disable_backend_db_writes):
    monkeypatch.setattr(analyze, "analyze_resume_text", _fake_analysis_response)

    response = client.post(
        "/analyze-resume",
        json={
            "resume_text": "Python developer with SQL, machine learning, FastAPI, Streamlit, and analytics project experience.",
            "privacy_mode": False,
        },
    )

    data = response.json()
    assert response.status_code == 200
    assert data.get("ats_score") is None
    assert any(
        "job description" in action.lower() or "review combined signals" in action.lower()
        for action in data.get("priority_actions", [])
    )


def test_analyze_resume_internal_error_hides_traceback(monkeypatch, client, disable_backend_db_writes):
    def failing_analysis(*args, **kwargs):
        raise RuntimeError("private internal error")

    monkeypatch.setattr(analyze, "analyze_resume_text", failing_analysis)

    response = client.post(
        "/analyze-resume",
        json={
            "resume_text": "Python developer with SQL, machine learning, FastAPI, Streamlit, and analytics project experience.",
            "job_description": "Need Python and SQL skills.",
            "privacy_mode": False,
        },
    )

    response_text = response.text
    assert response.status_code == 500
    assert "Traceback" not in response_text
    assert "private internal error" not in response_text


def test_successful_logging_attempts_request_log_if_analysis_save_fails(monkeypatch):
    request_logs = []

    def failing_analysis_save(*args, **kwargs):
        raise RuntimeError("database insert failed")

    def fake_request_log(session, data):
        request_logs.append(data)

    monkeypatch.setattr(analyze, "get_db_session", lambda: _FakeDbSession())
    monkeypatch.setattr(analyze, "create_analysis_run", failing_analysis_save)
    monkeypatch.setattr(analyze, "create_api_request_log", fake_request_log)

    analyze._save_successful_analysis(_fake_analysis_response(), privacy_mode=False, latency_ms=12.5)

    assert request_logs
    assert request_logs[0]["endpoint"] == "/analyze-resume"
    assert request_logs[0]["status_code"] == 200
    assert request_logs[0]["latency_ms"] == 12.5
