import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from model_registry.model_card import build_baseline_model_card
from model_registry.registry import (
    DEFAULT_REGISTRY_PATH,
    build_baseline_model_record,
    load_model_registry,
    register_model_version,
    save_model_registry,
)


MODEL_CARD_PATH = BASE_DIR / "artifacts" / "model_registry" / "model_card_baseline.json"
METADATA_CANDIDATES = [
    BASE_DIR / "artifacts" / "model_metrics.json",
    BASE_DIR / "artifacts" / "evaluation_metrics.json",
    BASE_DIR / "models" / "model_metrics.json",
    BASE_DIR / "evaluation_metrics.json",
    BASE_DIR / "artifacts" / "metrics.json",
]


def _load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def load_existing_metadata() -> dict:
    for path in METADATA_CANDIDATES:
        if path.exists():
            data = _load_json(path)
            if data:
                metrics = data.get("metrics", data)
                classes = data.get("classes") or list((data.get("report") or {}).keys())
                classes = [
                    class_name
                    for class_name in classes
                    if class_name not in {"accuracy", "macro avg", "weighted avg"}
                ]
                return {
                    "model_version": "baseline-v1",
                    "metrics": {
                        "accuracy": metrics.get("accuracy"),
                        "precision_macro": metrics.get("precision_macro"),
                        "recall_macro": metrics.get("recall_macro"),
                        "f1_macro": metrics.get("f1_macro"),
                        "precision_weighted": metrics.get("precision_weighted"),
                        "recall_weighted": metrics.get("recall_weighted"),
                        "f1_weighted": metrics.get("f1_weighted"),
                    },
                    "dataset_info": {
                        "class_count": len(classes) if classes else None,
                        "train_test_split_strategy": "stratified train_test_split with test_size=0.2 and random_state=42",
                        "dataset_source": "data/resume_dataset.csv",
                    },
                    "training_data_summary": "Baseline dataset from local data/resume_dataset.csv. Full resume text is not stored in registry metadata.",
                }
    return {
        "model_version": "baseline-v1",
        "metrics": {"accuracy": None},
        "dataset_info": {},
        "training_data_summary": "Not fully documented yet",
    }


def main() -> None:
    metadata = load_existing_metadata()
    model_record = build_baseline_model_record(metadata)
    registry_path = BASE_DIR / DEFAULT_REGISTRY_PATH
    registry = load_model_registry(registry_path)
    registry["models"] = [
        record
        for record in registry.get("models", [])
        if record.get("model_version") != model_record["model_version"]
    ]
    save_model_registry(registry, path=registry_path)
    register_model_version(model_record, path=registry_path)

    model_card = build_baseline_model_card({**metadata, "evaluation_risks": model_record.get("evaluation_risks", [])})
    MODEL_CARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    MODEL_CARD_PATH.write_text(json.dumps(model_card, indent=2, default=str), encoding="utf-8")

    print("Baseline model registered successfully.")


if __name__ == "__main__":
    main()
