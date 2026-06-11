from experiment_tracking import mlflow_tracker


def test_safe_log_params_redacts_sensitive_keys():
    params = mlflow_tracker.safe_log_params(
        {
            "model_name": "baseline",
            "resume_text": "private resume",
            "candidate_email": "person@example.com",
            "github_url": "https://github.com/example",
            "api_key": "secret",
        }
    )

    assert params["model_name"] == "baseline"
    assert params["resume_text"] == "[REDACTED]"
    assert params["candidate_email"] == "[REDACTED]"
    assert params["github_url"] == "[REDACTED]"
    assert params["api_key"] == "[REDACTED]"


def test_safe_log_metrics_keeps_only_numeric_values():
    metrics = mlflow_tracker.safe_log_metrics(
        {
            "accuracy": 0.91,
            "f1": 1,
            "notes": "good",
            "missing": None,
            "flag": True,
        }
    )

    assert metrics == {"accuracy": 0.91, "f1": 1.0}


def test_get_tracking_uri_uses_default_and_env_override(monkeypatch):
    monkeypatch.delenv("RESUMEIQ_MLFLOW_TRACKING_URI", raising=False)
    assert mlflow_tracker.get_tracking_uri() == "file:./mlruns"

    monkeypatch.setenv("RESUMEIQ_MLFLOW_TRACKING_URI", "file:/tmp/resumeiq-mlruns")
    assert mlflow_tracker.get_tracking_uri() == "file:/tmp/resumeiq-mlruns"


def test_build_experiment_tracking_summary_contains_privacy_notes(monkeypatch):
    monkeypatch.setattr(mlflow_tracker, "is_mlflow_available", lambda: False)

    summary = mlflow_tracker.build_experiment_tracking_summary()

    assert summary["tracking_tool"] == "MLflow"
    assert summary["available"] is False
    assert "Full resume text is not logged." in summary["privacy_notes"]
    assert "Full job descriptions are not logged." in summary["privacy_notes"]
    assert "Raw PII is redacted from parameters." in summary["privacy_notes"]


def test_log_baseline_experiment_handles_unavailable_mlflow(monkeypatch):
    monkeypatch.setattr(mlflow_tracker, "is_mlflow_available", lambda: False)

    result = mlflow_tracker.log_baseline_experiment(
        metrics={"accuracy": 1.0},
        params={"model_name": "ResumeIQ Baseline Resume Classifier"},
    )

    assert result["success"] is False
    assert result["available"] is False
    assert result["message"] == "MLflow is not installed or unavailable."
