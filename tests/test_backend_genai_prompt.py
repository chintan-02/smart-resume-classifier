import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_prompt_preview_resume_bullet_success(client):
    response = client.post(
        "/genai/prompt-preview",
        json={
            "task_type": "resume_bullet_rewrite",
            "original_bullet": "Built a Streamlit resume analysis app using Python.",
            "resume_evidence": ["Python, Streamlit, FastAPI project experience."],
            "job_description_evidence": ["Role asks for Python and FastAPI."],
            "privacy_mode": True,
            "consent_given": False,
        },
    )
    data = response.json()

    assert response.status_code == 200
    assert data["status"] == "success"
    assert data["source"] == "fastapi_prompt_preview"
    assert data["prompt_preview"]
    assert data["allowed_for_external_use"] is False
    assert "does not call external GenAI providers" in data["disclaimer"]


def test_prompt_preview_blocks_without_external_enabled(client):
    response = client.post(
        "/genai/prompt-preview",
        json={
            "task_type": "resume_bullet_rewrite",
            "original_bullet": "Built a dashboard.",
            "resume_evidence": ["Python dashboard project."],
            "consent_given": True,
        },
    )
    data = response.json()

    assert response.status_code == 200
    assert data["allowed_for_external_use"] is False
    assert "local-only mode" in data["blocked_reason"]


def test_prompt_preview_privacy_redaction(client):
    response = client.post(
        "/genai/prompt-preview",
        json={
            "task_type": "resume_bullet_rewrite",
            "original_bullet": "Built a Streamlit resume analysis app.",
            "resume_evidence": [
                "Arjun Mehra email arjun@example.com phone (403) 555-0192 Python project experience."
            ],
            "privacy_mode": True,
            "candidate_name": "Arjun Mehra",
            "consent_given": False,
        },
    )
    data = response.json()
    prompt_text = str(data.get("prompt_preview", {}))

    assert response.status_code == 200
    assert "arjun@example.com" not in prompt_text
    assert "(403) 555-0192" not in prompt_text
    assert "Arjun Mehra" not in prompt_text
    assert "[email]" in prompt_text
    assert "[phone]" in prompt_text
    assert "[candidate_name]" in prompt_text


def test_prompt_preview_unknown_task(client):
    response = client.post(
        "/genai/prompt-preview",
        json={
            "task_type": "unknown_task",
            "resume_evidence": ["Python project evidence."],
        },
    )
    data = response.json()

    assert response.status_code == 200
    assert data["prompt_preview"]["allowed_for_external_use"] is False
    assert "Unsupported prompt task type" in data["prompt_preview"]["blocked_reason"]


def test_prompt_preview_validation_short_task(client):
    response = client.post(
        "/genai/prompt-preview",
        json={
            "task_type": "x",
            "resume_evidence": ["Python project evidence."],
        },
    )

    assert response.status_code == 422


def test_ready_includes_genai_prompt_builder(client):
    response = client.get("/ready")
    checks = response.json().get("checks", {})

    assert response.status_code == 200
    assert checks.get("genai_prompt_builder") == "available"
