import importlib
import os
from numbers import Number
from typing import Any


DEFAULT_TRACKING_URI = "file:./mlruns"
DEFAULT_EXPERIMENT_NAME = "ResumeIQ Baseline Experiments"
SENSITIVE_PARAM_PARTS = {
    "resume_text",
    "job_description",
    "email",
    "phone",
    "name",
    "address",
    "token",
    "secret",
    "password",
    "api_key",
    "authorization",
    "linkedin",
    "github",
}
REDACTED_VALUE = "[REDACTED]"
SAFE_NAME_KEYS = {"model_name", "experiment_name"}


def _load_mlflow():
    return importlib.import_module("mlflow")


def is_mlflow_available() -> bool:
    try:
        _load_mlflow()
    except Exception:
        return False
    return True


def get_tracking_uri() -> str:
    return os.getenv("RESUMEIQ_MLFLOW_TRACKING_URI", DEFAULT_TRACKING_URI)


def get_experiment_name() -> str:
    return os.getenv("RESUMEIQ_MLFLOW_EXPERIMENT", DEFAULT_EXPERIMENT_NAME)


def setup_mlflow() -> dict:
    if not is_mlflow_available():
        return {
            "available": False,
            "message": "MLflow is not installed or unavailable.",
        }

    mlflow = _load_mlflow()
    tracking_uri = get_tracking_uri()
    experiment_name = get_experiment_name()
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)
    return {
        "available": True,
        "tracking_uri": tracking_uri,
        "experiment_name": experiment_name,
        "message": "MLflow local tracking is ready.",
    }


def _is_sensitive_key(key: str) -> bool:
    normalized_key = str(key).lower()
    if normalized_key in SAFE_NAME_KEYS:
        return False
    return any(part in normalized_key for part in SENSITIVE_PARAM_PARTS)


def safe_log_params(params: dict | None) -> dict:
    safe_params = {}
    for key, value in (params or {}).items():
        if _is_sensitive_key(key):
            safe_params[key] = REDACTED_VALUE
        elif value is None:
            safe_params[key] = ""
        else:
            safe_params[key] = str(value)
    return safe_params


def safe_log_metrics(metrics: dict | None) -> dict:
    safe_metrics = {}
    for key, value in (metrics or {}).items():
        if isinstance(value, bool) or value is None:
            continue
        if isinstance(value, Number):
            safe_metrics[key] = float(value)
    return safe_metrics


def _safe_log_tags(tags: dict[str, Any]) -> dict[str, str]:
    return {str(key): str(value) for key, value in safe_log_params(tags).items()}


def log_baseline_experiment(
    metrics: dict | None = None,
    params: dict | None = None,
    tags: dict | None = None,
    run_name: str = "baseline_resume_classifier",
) -> dict:
    setup_result = setup_mlflow()
    if not setup_result.get("available"):
        return {
            "success": False,
            "available": False,
            "message": "MLflow is not installed or unavailable.",
        }

    mlflow = _load_mlflow()
    safe_params = safe_log_params(params)
    safe_metrics = safe_log_metrics(metrics)
    safe_tags = _safe_log_tags(
        {
            "project": "ResumeIQ",
            "model_type": "TF-IDF + Logistic Regression",
            "tracking_scope": "local_foundation",
            "pii_policy": "no_resume_text_or_raw_pii",
            **(tags or {}),
        }
    )

    with mlflow.start_run(run_name=run_name) as run:
        if safe_params:
            mlflow.log_params(safe_params)
        for metric_name, metric_value in safe_metrics.items():
            mlflow.log_metric(metric_name, metric_value)
        if safe_tags:
            mlflow.set_tags(safe_tags)

        run_id = run.info.run_id

    return {
        "success": True,
        "run_id": run_id,
        "tracking_uri": setup_result.get("tracking_uri"),
        "message": "Baseline experiment logged successfully.",
    }


def build_experiment_tracking_summary() -> dict:
    available = is_mlflow_available()
    return {
        "tracking_tool": "MLflow",
        "mode": "local file-based tracking",
        "tracking_uri": get_tracking_uri(),
        "experiment_name": get_experiment_name(),
        "available": available,
        "privacy_notes": [
            "Full resume text is not logged.",
            "Full job descriptions are not logged.",
            "Raw PII is redacted from parameters.",
        ],
        "future_plan": [
            "Track future model comparison experiments.",
            "Track cross-validation metrics.",
            "Track model artifacts after registry governance is finalized.",
            "Optional remote MLflow tracking can be added later.",
        ],
    }
