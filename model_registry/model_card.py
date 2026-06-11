from model_registry.evaluation import detect_evaluation_risks


def build_baseline_model_card(metadata: dict | None = None) -> dict:
    metadata = metadata if isinstance(metadata, dict) else {}
    metrics = metadata.get("metrics", {}) if isinstance(metadata.get("metrics"), dict) else {}
    dataset_info = metadata.get("dataset_info", {}) if isinstance(metadata.get("dataset_info"), dict) else {}
    risks = metadata.get("evaluation_risks") or detect_evaluation_risks(metrics, dataset_info)

    return {
        "model_name": "ResumeIQ Baseline Resume Classifier",
        "model_version": metadata.get("model_version", "baseline-v1"),
        "model_type": "TF-IDF + Logistic Regression",
        "task": "Resume role classification",
        "intended_use": "Decision-support signal for resume intelligence workflows.",
        "not_intended_use": [
            "Final hiring decisions",
            "Automated rejection",
            "Protected attribute inference",
            "Legal or compliance decisions",
        ],
        "training_data_summary": metadata.get("training_data_summary", "Not fully documented yet"),
        "evaluation_summary": {
            "metrics": metrics,
            "caveats": risks,
        },
        "known_limitations": [
            "May show low confidence on real resumes",
            "May be sensitive to resume wording and formatting",
            "Validation accuracy should be investigated if unusually high",
            "Does not replace human review",
        ],
        "privacy_notes": [
            "Full resume text should not be stored in model registry metadata",
            "PII should be masked in display/export workflows",
        ],
        "responsible_ai_notes": [
            "Does not score protected attributes",
            "Use combined fit signals and human review",
        ],
    }


def get_model_card_sections(model_card: dict) -> list[dict]:
    model_card = model_card if isinstance(model_card, dict) else {}
    return [
        {
            "title": "Overview",
            "content": {
                "model_name": model_card.get("model_name"),
                "model_version": model_card.get("model_version"),
                "model_type": model_card.get("model_type"),
                "task": model_card.get("task"),
            },
        },
        {"title": "Intended Use", "content": model_card.get("intended_use")},
        {"title": "Not Intended Use", "content": model_card.get("not_intended_use", [])},
        {"title": "Evaluation", "content": model_card.get("evaluation_summary", {})},
        {"title": "Limitations", "content": model_card.get("known_limitations", [])},
        {
            "title": "Privacy & Responsible AI",
            "content": {
                "privacy_notes": model_card.get("privacy_notes", []),
                "responsible_ai_notes": model_card.get("responsible_ai_notes", []),
            },
        },
    ]
