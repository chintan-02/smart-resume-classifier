import os
from json import JSONDecodeError
from typing import Any

import requests


DEFAULT_API_BASE_URL = "http://127.0.0.1:8000"
API_SERVICE_NAME = "ResumeIQ API"


def get_api_base_url() -> str:
    return os.getenv("RESUMEIQ_API_BASE_URL", DEFAULT_API_BASE_URL).rstrip("/")


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
