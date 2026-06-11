import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from experiment_tracking.mlflow_tracker import log_baseline_experiment


REGISTRY_PATH = BASE_DIR / "artifacts" / "model_registry" / "model_registry.json"


def _load_latest_registry_record() -> dict:
    if not REGISTRY_PATH.exists():
        return {}

    try:
        registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}

    models = registry.get("models", [])
    if not isinstance(models, list) or not models:
        return {}
    latest_record = models[-1]
    return latest_record if isinstance(latest_record, dict) else {}


def main() -> None:
    latest_record = _load_latest_registry_record()
    metrics = latest_record.get("metrics", {}) if isinstance(latest_record.get("metrics"), dict) else {}
    params = {
        "model_name": latest_record.get("model_name", "ResumeIQ Baseline Resume Classifier"),
        "model_version": latest_record.get("model_version", "baseline-v1"),
        "model_type": latest_record.get("model_type", "TF-IDF + Logistic Regression"),
        "evaluation_status": latest_record.get("status", "not_registered"),
    }

    result = log_baseline_experiment(metrics=metrics, params=params)
    if result.get("success"):
        print("Baseline MLflow experiment logged successfully.")
    else:
        print("MLflow is unavailable. Install mlflow to enable tracking.")


if __name__ == "__main__":
    main()
