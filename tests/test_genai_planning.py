from src.genai_planning import (
    check_genai_consent,
    get_future_prompt_templates,
    get_supported_future_genai_features,
    is_external_genai_enabled,
    redact_for_external_genai,
)


def test_external_genai_disabled_by_default(monkeypatch):
    monkeypatch.delenv("RESUMEIQ_EXTERNAL_GENAI_ENABLED", raising=False)

    assert is_external_genai_enabled() is False


def test_check_genai_consent_blocks_when_external_disabled():
    result = check_genai_consent(consent_given=True, external_enabled=False)

    assert result["allowed"] is False
    assert result["mode"] == "local_only"
    assert "local-only mode" in result["reason"]


def test_check_genai_consent_blocks_when_consent_missing():
    result = check_genai_consent(consent_given=False, external_enabled=True)

    assert result["allowed"] is False
    assert result["mode"] == "local_only"
    assert "Explicit consent is required" in result["reason"]


def test_check_genai_consent_allows_only_when_external_enabled_and_consent_true():
    result = check_genai_consent(consent_given=True, external_enabled=True)

    assert result["allowed"] is True
    assert result["mode"] == "external_allowed"


def test_redact_for_external_genai_masks_email_phone_and_name():
    redacted = redact_for_external_genai(
        "Jane Doe Data Scientist jane@example.com 555-123-4567 Python SQL",
        candidate_name="Jane Doe",
    )

    assert "Jane Doe" not in redacted
    assert "jane@example.com" not in redacted
    assert "555-123-4567" not in redacted
    assert "[candidate_name]" in redacted
    assert "[email]" in redacted
    assert "[phone]" in redacted


def test_supported_future_genai_features_are_planned_and_require_consent():
    features = get_supported_future_genai_features()

    assert features
    assert all(feature["status"] == "planned" for feature in features)
    assert all(feature["requires_user_consent"] is True for feature in features)
    assert all(feature["safe_default"] == "disabled" for feature in features)


def test_future_prompt_templates_include_truthfulness_and_human_review_reminders():
    templates = get_future_prompt_templates()
    combined_text = " ".join(templates.values()).lower()

    assert "do not invent" in combined_text
    assert "truthfulness" in combined_text
    assert "human review" in combined_text
