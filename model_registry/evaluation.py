from typing import Any


def normalize_metric(value) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def get_metric_label(value) -> str:
    metric = normalize_metric(value)
    if metric is None:
        return "Unavailable"
    if metric >= 0.85:
        return "Strong"
    if metric >= 0.65:
        return "Moderate"
    return "Needs review"


def calculate_basic_classification_metrics(y_true, y_pred) -> dict:
    try:
        from sklearn.metrics import accuracy_score, precision_recall_fscore_support

        precision_macro, recall_macro, f1_macro, _ = precision_recall_fscore_support(
            y_true,
            y_pred,
            average="macro",
            zero_division=0,
        )
        precision_weighted, recall_weighted, f1_weighted, _ = precision_recall_fscore_support(
            y_true,
            y_pred,
            average="weighted",
            zero_division=0,
        )
        return {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "precision_macro": float(precision_macro),
            "recall_macro": float(recall_macro),
            "f1_macro": float(f1_macro),
            "precision_weighted": float(precision_weighted),
            "recall_weighted": float(recall_weighted),
            "f1_weighted": float(f1_weighted),
        }
    except Exception:
        return {
            "accuracy": None,
            "precision_macro": None,
            "recall_macro": None,
            "f1_macro": None,
            "precision_weighted": None,
            "recall_weighted": None,
            "f1_weighted": None,
        }


def build_confusion_matrix_summary(y_true, y_pred, labels=None) -> dict:
    try:
        from sklearn.metrics import confusion_matrix

        if labels is None:
            labels = sorted({*list(y_true), *list(y_pred)})
        matrix = confusion_matrix(y_true, y_pred, labels=labels)
        return {
            "labels": [str(label) for label in labels],
            "matrix": matrix.tolist(),
            "notes": ["Rows are true labels. Columns are predicted labels."],
        }
    except Exception:
        return {
            "labels": [str(label) for label in labels] if labels else [],
            "matrix": [],
            "notes": ["Confusion matrix could not be calculated safely."],
        }


def _get_dataset_value(dataset_info: dict[str, Any], key: str):
    return dataset_info.get(key) if isinstance(dataset_info, dict) else None


def detect_evaluation_risks(metrics: dict, dataset_info: dict | None = None) -> list[str]:
    metrics = metrics if isinstance(metrics, dict) else {}
    dataset_info = dataset_info if isinstance(dataset_info, dict) else {}
    risks = []

    accuracy = normalize_metric(metrics.get("accuracy"))
    if accuracy is not None and accuracy >= 0.98:
        risks.append(
            "Very high validation accuracy may indicate an easy dataset, small validation split, overfitting, or data leakage. Review evaluation setup."
        )

    validation_size = _get_dataset_value(dataset_info, "validation_size")
    try:
        validation_size = int(validation_size) if validation_size is not None else None
    except (TypeError, ValueError):
        validation_size = None
    if validation_size is not None and validation_size < 50:
        risks.append("Validation set is small; reported metrics may be unstable.")

    class_count = _get_dataset_value(dataset_info, "class_count")
    if not class_count:
        risks.append("Class distribution should be reviewed.")

    if not _get_dataset_value(dataset_info, "train_test_split_strategy"):
        risks.append("Train/test split strategy is not documented.")

    if not _get_dataset_value(dataset_info, "dataset_source"):
        risks.append("Dataset source is not documented.")

    return risks
