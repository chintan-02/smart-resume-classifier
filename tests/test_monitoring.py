from src.monitoring import (
    build_monitoring_summary,
    format_latency_ms,
    generate_request_id,
    safe_log_metadata,
)


def test_generate_request_id_uses_prefix():
    request_id = generate_request_id("test")

    assert isinstance(request_id, str)
    assert request_id.startswith("test_")


def test_safe_log_metadata_redacts_sensitive_keys():
    metadata = {
        "resume_text": "full resume content",
        "job_description": "full job description",
        "email": "candidate@example.com",
        "api_key": "secret",
        "authorization": "Bearer token",
    }

    safe_metadata = safe_log_metadata(metadata)

    assert all(value == "[redacted]" for value in safe_metadata.values())


def test_safe_log_metadata_keeps_safe_score_fields():
    metadata = {
        "predicted_role": "Data Scientist",
        "model_confidence": 91.5,
        "ats_score": 82,
        "jd_match_score": 0.67,
        "privacy_mode": True,
        "success": True,
    }

    safe_metadata = safe_log_metadata(metadata)

    assert safe_metadata["predicted_role"] == "Data Scientist"
    assert safe_metadata["model_confidence"] == 91.5
    assert safe_metadata["ats_score"] == 82
    assert safe_metadata["jd_match_score"] == 0.67
    assert safe_metadata["privacy_mode"] is True
    assert safe_metadata["success"] is True


def test_format_latency_ms_converts_seconds_to_ms():
    assert format_latency_ms(0.12345) == 123.45
    assert format_latency_ms(None) is None


def test_build_monitoring_summary_returns_expected_keys():
    summary = build_monitoring_summary(api_status="ok", db_status="available", test_status="passing")

    assert summary["api_status"] == "ok"
    assert summary["database_status"] == "available"
    assert summary["test_status"] == "passing"
    assert summary["monitoring_level"] == "local_foundation"
    assert summary["notes"]
