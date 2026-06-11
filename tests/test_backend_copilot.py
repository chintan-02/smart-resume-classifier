import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from backend.main import app
from backend.routers import copilot


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def disable_copilot_db_logging(monkeypatch):
    monkeypatch.setattr(copilot, "_save_api_request_log", lambda *args, **kwargs: None)


def test_copilot_ask_success(client, disable_copilot_db_logging):
    response = client.post(
        "/copilot/ask",
        json={
            "query": "Which skills match the job description?",
            "resume_text": (
                "Candidate has Python, SQL, machine learning, FastAPI, Docker, "
                "and Streamlit project experience."
            ),
            "job_description": "Looking for Python, SQL, machine learning, Docker, and FastAPI.",
            "privacy_mode": False,
        },
    )
    data = response.json()

    assert response.status_code == 200
    assert data["status"] == "success"
    assert data["answer"]
    assert isinstance(data["evidence"], list)
    assert data["disclaimer"]
    assert data["source"] == "fastapi_local_retrieval"
    assert {"resume", "job_description"}.issubset({item["source"] for item in data["evidence"]})


def test_copilot_ask_privacy_masking(client, disable_copilot_db_logging):
    response = client.post(
        "/copilot/ask",
        json={
            "query": "What is the candidate contact information?",
            "resume_text": (
                "Jane Doe Data Scientist jane@example.com 555-123-4567 "
                "https://linkedin.com/in/jane-doe https://github.com/janedoe "
                "Python SQL FastAPI Docker project experience."
            ),
            "job_description": "Looking for Python and FastAPI.",
            "privacy_mode": True,
            "candidate_name": "Jane Doe",
        },
    )
    data = response.json()
    evidence_text = " ".join(item["text"] for item in data.get("evidence", []))

    assert response.status_code == 200
    assert "jane@example.com" not in evidence_text
    assert "555-123-4567" not in evidence_text
    assert "Jane Doe" not in evidence_text
    assert "[email]" in evidence_text
    assert "[phone]" in evidence_text
    assert "[candidate_name]" in evidence_text


def test_copilot_ask_validation_short_resume(client, disable_copilot_db_logging):
    response = client.post(
        "/copilot/ask",
        json={
            "query": "Which skills match?",
            "resume_text": "Too short",
            "job_description": "Looking for Python.",
            "privacy_mode": False,
        },
    )

    assert response.status_code == 422


def test_copilot_ask_no_external_ai_claim(client, disable_copilot_db_logging):
    response = client.post(
        "/copilot/ask",
        json={
            "query": "Summarize this candidate for recruiter review.",
            "resume_text": "Python developer with SQL, FastAPI, Docker, and Streamlit project experience.",
            "job_description": "Looking for Python, SQL, Docker, and FastAPI.",
            "privacy_mode": False,
        },
    )
    data = response.json()
    combined_safety_text = " ".join(data.get("limitations", []) + [data.get("disclaimer", "")]).lower()

    assert response.status_code == 200
    assert "retrieval-only" in combined_safety_text
    assert "does not make hiring decisions" in combined_safety_text
