from json import JSONDecodeError
from typing import Any

import requests

from src.settings import get_settings


DEFAULT_API_BASE_URL = "http://127.0.0.1:8000"
API_SERVICE_NAME = "ResumeIQ API"


def get_api_base_url() -> str:
    return get_settings().api_base_url.rstrip("/")


def _offline_response(message: str) -> dict:
    return {
        "available": False,
        "status": "offline",
        "service": API_SERVICE_NAME,
        "message": message,
    }


def _safe_json(response: requests.Response) -> dict[str, Any]:
    try:
        data = response.json()
    except (JSONDecodeError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def check_api_health(base_url: str | None = None, timeout: float = 2.0) -> dict:
    api_url = (base_url or get_api_base_url()).rstrip("/")

    try:
        response = requests.get(f"{api_url}/health", timeout=timeout)
        if response.status_code != 200:
            return _offline_response("Backend API is offline. Streamlit will use local analysis.")
        data = _safe_json(response)
    except requests.RequestException:
        return _offline_response("Backend API is offline. Streamlit will use local analysis.")

    return {
        "available": True,
        "status": data.get("status", "ok"),
        "service": data.get("service", API_SERVICE_NAME),
        "message": "Backend API is available.",
    }


def check_api_ready(base_url: str | None = None, timeout: float = 2.0) -> dict:
    api_url = (base_url or get_api_base_url()).rstrip("/")

    try:
        response = requests.get(f"{api_url}/ready", timeout=timeout)
        if response.status_code != 200:
            return {
                **_offline_response("Backend API readiness check failed. Streamlit will use local analysis."),
                "checks": {},
            }
        data = _safe_json(response)
    except requests.RequestException:
        return {
            **_offline_response("Backend API is offline. Streamlit will use local analysis."),
            "checks": {},
        }

    return {
        "available": True,
        "status": data.get("status", "ready"),
        "checks": data.get("checks", {}) if isinstance(data.get("checks"), dict) else {},
        "message": "Backend API is ready.",
    }


def analyze_resume_via_api(
    resume_text: str,
    job_description: str | None = None,
    privacy_mode: bool = False,
    base_url: str | None = None,
    timeout: float = 10.0,
) -> dict:
    api_url = (base_url or get_api_base_url()).rstrip("/")
    payload = {
        "resume_text": resume_text,
        "job_description": job_description,
        "privacy_mode": privacy_mode,
    }

    try:
        response = requests.post(f"{api_url}/analyze-resume", json=payload, timeout=timeout)
        if response.status_code != 200:
            return {
                "success": False,
                "source": "api",
                "data": None,
                "message": "Backend analysis failed or is unavailable. Local analysis can be used.",
            }
        data = _safe_json(response)
        if not data:
            return {
                "success": False,
                "source": "api",
                "data": None,
                "message": "Backend analysis failed or is unavailable. Local analysis can be used.",
            }
    except requests.RequestException:
        return {
            "success": False,
            "source": "api",
            "data": None,
            "message": "Backend analysis failed or is unavailable. Local analysis can be used.",
        }

    return {
        "success": True,
        "source": "api",
        "data": data,
        "message": "Backend analysis completed.",
    }


def ask_copilot_via_api(
    query: str,
    resume_text: str,
    job_description: str | None = None,
    privacy_mode: bool = False,
    candidate_name: str | None = None,
    top_k: int = 5,
    base_url: str | None = None,
    timeout: float = 10.0,
) -> dict:
    api_url = (base_url or get_api_base_url()).rstrip("/")
    payload = {
        "query": query,
        "resume_text": resume_text,
        "job_description": job_description,
        "privacy_mode": privacy_mode,
        "candidate_name": candidate_name,
        "top_k": top_k,
    }

    try:
        response = requests.post(f"{api_url}/copilot/ask", json=payload, timeout=timeout)
        if response.status_code != 200:
            return {
                "success": False,
                "source": "api",
                "data": None,
                "message": "Backend copilot retrieval failed or is unavailable. Local copilot can be used.",
            }
        data = _safe_json(response)
        if not data:
            return {
                "success": False,
                "source": "api",
                "data": None,
                "message": "Backend copilot retrieval failed or is unavailable. Local copilot can be used.",
            }
    except requests.RequestException:
        return {
            "success": False,
            "source": "api",
            "data": None,
            "message": "Backend copilot retrieval failed or is unavailable. Local copilot can be used.",
        }

    return {
        "success": True,
        "source": "api",
        "data": data,
        "message": "Backend copilot retrieval completed.",
    }


def build_genai_prompt_preview_via_api(
    task_type: str,
    resume_evidence: list[str] | None = None,
    job_description_evidence: list[str] | None = None,
    user_goal: str | None = None,
    original_bullet: str | None = None,
    target_role: str | None = None,
    company_name: str | None = None,
    role_title: str | None = None,
    recruiter_name: str | None = None,
    recipient_name: str | None = None,
    query: str | None = None,
    retrieved_evidence: list[dict] | None = None,
    privacy_mode: bool = True,
    candidate_name: str | None = None,
    consent_given: bool = False,
    base_url: str | None = None,
    timeout: float = 10.0,
) -> dict:
    api_url = (base_url or get_api_base_url()).rstrip("/")
    payload = {
        "task_type": task_type,
        "resume_evidence": resume_evidence,
        "job_description_evidence": job_description_evidence,
        "user_goal": user_goal,
        "original_bullet": original_bullet,
        "target_role": target_role,
        "company_name": company_name,
        "role_title": role_title,
        "recruiter_name": recruiter_name,
        "recipient_name": recipient_name,
        "query": query,
        "retrieved_evidence": retrieved_evidence,
        "privacy_mode": privacy_mode,
        "candidate_name": candidate_name,
        "consent_given": consent_given,
    }

    try:
        response = requests.post(f"{api_url}/genai/prompt-preview", json=payload, timeout=timeout)
        if response.status_code != 200:
            return {
                "success": False,
                "source": "api",
                "data": None,
                "message": "Backend prompt preview failed or is unavailable. Local prompt builder can be used.",
            }
        data = _safe_json(response)
        if not data:
            return {
                "success": False,
                "source": "api",
                "data": None,
                "message": "Backend prompt preview failed or is unavailable. Local prompt builder can be used.",
            }
    except requests.RequestException:
        return {
            "success": False,
            "source": "api",
            "data": None,
            "message": "Backend prompt preview failed or is unavailable. Local prompt builder can be used.",
        }

    return {
        "success": True,
        "source": "api",
        "data": data,
        "message": "Backend prompt preview completed.",
    }
