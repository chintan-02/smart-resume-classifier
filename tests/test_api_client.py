import requests

from src.api_client import analyze_resume_via_api, ask_copilot_via_api, check_api_health, get_api_base_url


def test_get_api_base_url_default(monkeypatch):
    monkeypatch.delenv("RESUMEIQ_API_BASE_URL", raising=False)

    assert get_api_base_url() == "http://127.0.0.1:8000"


def test_get_api_base_url_respects_env_override(monkeypatch):
    monkeypatch.setenv("RESUMEIQ_API_BASE_URL", "http://localhost:9000/")

    assert get_api_base_url() == "http://localhost:9000"


def test_check_api_health_handles_unavailable_backend(monkeypatch):
    def fake_get(*args, **kwargs):
        raise requests.ConnectionError("offline")

    monkeypatch.setattr("src.api_client.requests.get", fake_get)

    result = check_api_health(timeout=0.01)

    assert result.get("available") is False
    assert result.get("status") == "offline"


def test_analyze_resume_via_api_handles_failed_request(monkeypatch):
    def fake_post(*args, **kwargs):
        raise requests.ConnectionError("offline")

    monkeypatch.setattr("src.api_client.requests.post", fake_post)

    result = analyze_resume_via_api(
        resume_text="Python developer with SQL and machine learning project experience.",
        job_description="Need Python and SQL.",
        timeout=0.01,
    )

    assert result.get("success") is False
    assert result.get("data") is None


def test_ask_copilot_via_api_handles_successful_response(monkeypatch):
    class FakeResponse:
        status_code = 200

        def json(self):
            return {
                "status": "success",
                "answer": "Evidence found.",
                "question_type": "skills",
                "evidence": [],
                "limitations": [],
                "disclaimer": "This copilot retrieves evidence from the uploaded resume/JD.",
                "privacy_mode": False,
                "source": "fastapi_local_retrieval",
            }

    def fake_post(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr("src.api_client.requests.post", fake_post)

    result = ask_copilot_via_api(
        query="Which skills match?",
        resume_text="Python developer with SQL and FastAPI project experience.",
        job_description="Need Python and SQL.",
    )

    assert result["success"] is True
    assert result["source"] == "api"
    assert result["data"]["source"] == "fastapi_local_retrieval"


def test_ask_copilot_via_api_handles_failed_request(monkeypatch):
    def fake_post(*args, **kwargs):
        raise requests.ConnectionError("offline")

    monkeypatch.setattr("src.api_client.requests.post", fake_post)

    result = ask_copilot_via_api(
        query="Which skills match?",
        resume_text="Python developer with SQL and FastAPI project experience.",
    )

    assert result["success"] is False
    assert result["data"] is None
    assert "Local copilot can be used" in result["message"]
