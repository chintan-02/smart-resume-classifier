import json

from model_registry.evaluation import (
    calculate_basic_classification_metrics,
    detect_evaluation_risks,
    get_metric_label,
)
from model_registry.model_card import build_baseline_model_card
from model_registry.registry import (
    build_baseline_model_record,
    get_latest_model_record,
    register_model_version,
)


def test_metric_label_handles_common_ranges():
    assert get_metric_label(0.9) == "Strong"
    assert get_metric_label(0.7) == "Moderate"
    assert get_metric_label(0.4) == "Needs review"
    assert get_metric_label(None) == "Unavailable"


def test_basic_classification_metrics_include_accuracy_and_macro_scores():
    metrics = calculate_basic_classification_metrics(
        ["Data Analyst", "Backend Developer", "Data Analyst"],
        ["Data Analyst", "Backend Developer", "Backend Developer"],
    )

    assert metrics["accuracy"] == 2 / 3
    assert "precision_macro" in metrics
    assert "recall_macro" in metrics
    assert "f1_macro" in metrics


def test_high_validation_accuracy_is_flagged_as_a_risk():
    risks = detect_evaluation_risks(
        {"accuracy": 1.0},
        {
            "class_count": 11,
            "train_test_split_strategy": "stratified split",
            "dataset_source": "local csv",
        },
    )

    assert any("Very high validation accuracy" in risk for risk in risks)


def test_baseline_record_marks_very_high_accuracy_as_needs_review():
    record = build_baseline_model_record(
        {
            "metrics": {"accuracy": 1.0},
            "dataset_info": {
                "class_count": 11,
                "train_test_split_strategy": "stratified split",
                "dataset_source": "local csv",
            },
        }
    )

    assert record["model_version"] == "baseline-v1"
    assert record["status"] == "needs_review"
    assert record["model_type"] == "TF-IDF + Logistic Regression"


def test_registry_round_trip_uses_local_json(tmp_path):
    registry_path = tmp_path / "model_registry.json"
    record = build_baseline_model_record({"metrics": {"accuracy": 0.82}})

    register_model_version(record, path=registry_path)
    latest = get_latest_model_record(path=registry_path)

    assert latest["model_version"] == "baseline-v1"
    assert latest["metrics"]["accuracy"] == 0.82


def test_model_card_documents_boundaries_without_raw_text_fields():
    model_card = build_baseline_model_card({"metrics": {"accuracy": 1.0}})
    serialized = json.dumps(model_card)

    assert "Final hiring decisions" in serialized
    assert "resume_text" not in serialized
    assert "job_description" not in serialized
    assert "raw_pii" not in serialized
