import json
from datetime import datetime, timezone
from pathlib import Path

from model_registry.evaluation import detect_evaluation_risks, normalize_metric
from src.settings import get_settings


DEFAULT_REGISTRY_PATH = get_settings().model_registry_path


def ensure_registry_dir(path=DEFAULT_REGISTRY_PATH) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def load_model_registry(path=DEFAULT_REGISTRY_PATH) -> dict:
    registry_path = Path(path)
    if not registry_path.exists():
        return {
            "registry_version": "0.1",
            "models": [],
        }
    try:
        data = json.loads(registry_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("Registry JSON must be an object.")
        data.setdefault("registry_version", "0.1")
        data.setdefault("models", [])
        return data
    except Exception:
        return {
            "registry_version": "0.1",
            "models": [],
        }


def save_model_registry(registry: dict, path=DEFAULT_REGISTRY_PATH) -> None:
    ensure_registry_dir(path)
    Path(path).write_text(json.dumps(registry, indent=2, default=str), encoding="utf-8")


def register_model_version(model_record: dict, path=DEFAULT_REGISTRY_PATH) -> dict:
    registry = load_model_registry(path)
    registry["models"].append(model_record if isinstance(model_record, dict) else {})
    save_model_registry(registry, path)
    return registry


def get_latest_model_record(path=DEFAULT_REGISTRY_PATH) -> dict | None:
    registry = load_model_registry(path)
    models = registry.get("models", [])
    return models[-1] if models else None


def build_baseline_model_record(metadata: dict | None = None) -> dict:
    metadata = metadata if isinstance(metadata, dict) else {}
    metrics = metadata.get("metrics", {}) if isinstance(metadata.get("metrics"), dict) else {}
    dataset_info = metadata.get("dataset_info", {}) if isinstance(metadata.get("dataset_info"), dict) else {}
    accuracy = normalize_metric(metrics.get("accuracy"))
    evaluation_risks = detect_evaluation_risks(metrics, dataset_info)

    return {
        "model_name": "ResumeIQ Baseline Resume Classifier",
        "model_version": metadata.get("model_version", "baseline-v1"),
        "model_type": "TF-IDF + Logistic Regression",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "artifact_reference": "local artifacts / current classifier pipeline",
        "metrics": metrics,
        "evaluation_risks": evaluation_risks,
        "status": "needs_review" if accuracy is not None and accuracy >= 0.98 else "active_baseline",
        "notes": [
            "Baseline model for portfolio demonstration",
            "Validation accuracy should be reviewed before production use",
        ],
    }
