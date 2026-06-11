import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from src.settings import get_settings


SENSITIVE_KEY_PARTS = (
    "resume_text",
    "job_description",
    "email",
    "phone",
    "linkedin",
    "github",
    "name",
    "address",
    "token",
    "secret",
    "password",
    "api_key",
    "authorization",
)

SAFE_KEYS = {
    "endpoint",
    "method",
    "path",
    "status_code",
    "latency_ms",
    "request_id",
    "source",
    "predicted_role",
    "model_confidence",
    "ats_score",
    "jd_match_score",
    "privacy_mode",
    "success",
}


def get_logger(name: str = "resumeiq") -> logging.Logger:
    logger = logging.getLogger(name)
    level_name = get_settings().log_level.upper()
    level = getattr(logging, level_name, logging.INFO)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
        logger.addHandler(handler)

    logger.propagate = False
    return logger


def generate_request_id(prefix: str = "req") -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    short_id = uuid.uuid4().hex[:6]
    return f"{prefix}_{timestamp}_{short_id}"


def _safe_value(value: Any):
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, (list, tuple, set)):
        return [str(item) for item in value[:10]]
    if isinstance(value, dict):
        return safe_log_metadata(value)
    return str(value)


def safe_log_metadata(metadata: dict | None) -> dict:
    if not isinstance(metadata, dict):
        return {}

    safe_metadata = {}
    for key, value in metadata.items():
        key_text = str(key)
        normalized_key = key_text.lower()
        if any(sensitive_part in normalized_key for sensitive_part in SENSITIVE_KEY_PARTS):
            safe_metadata[key_text] = "[redacted]"
        elif key_text in SAFE_KEYS:
            safe_metadata[key_text] = _safe_value(value)
        else:
            safe_metadata[key_text] = _safe_value(value)
    return safe_metadata


def log_event(
    logger,
    event_type: str,
    message: str,
    metadata: dict | None = None,
    level: str = "info",
) -> None:
    try:
        safe_metadata = safe_log_metadata(metadata)
        payload = {
            "event_type": event_type,
            "message": message,
            "metadata": safe_metadata,
        }
        log_message = json.dumps(payload, default=str, sort_keys=True)
    except Exception:
        log_message = f"event_type={event_type} message={message} metadata=[unavailable]"

    log_method = getattr(logger, str(level).lower(), logger.info)
    log_method(log_message)


def build_monitoring_summary(api_status=None, db_status=None, test_status=None) -> dict:
    return {
        "api_status": api_status or "unknown",
        "database_status": db_status or "unknown",
        "test_status": test_status or "unknown",
        "monitoring_level": "local_foundation",
        "notes": [
            "Local structured logging is enabled.",
            "Sensitive resume and job-description content is not logged.",
            "External observability tools are not connected yet.",
        ],
    }


def get_monitoring_checklist() -> list[dict]:
    return [
        {"item": "Safe structured logging", "status": "Implemented"},
        {"item": "Request IDs", "status": "Implemented"},
        {"item": "API request latency logging", "status": "Implemented"},
        {"item": "Database request metadata logs", "status": "Implemented"},
        {"item": "PII-safe logging", "status": "Implemented"},
        {"item": "External monitoring integration", "status": "Planned future"},
        {"item": "Production alerting", "status": "Planned future"},
    ]


def format_latency_ms(seconds: float | None) -> float | None:
    if seconds is None:
        return None
    try:
        return round(float(seconds) * 1000, 2)
    except (TypeError, ValueError):
        return None
