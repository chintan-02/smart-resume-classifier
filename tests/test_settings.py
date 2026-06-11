from pathlib import Path

from src.settings import (
    ResumeIQSettings,
    get_runtime_summary,
    get_settings,
    parse_bool,
    parse_int,
    settings_to_safe_dict,
)


def test_parse_bool_handles_true_and_false_values():
    for value in ["true", "1", "yes", "y", "on", "TRUE"]:
        assert parse_bool(value) is True

    for value in ["false", "0", "no", "n", "off", "FALSE"]:
        assert parse_bool(value, default=True) is False

    assert parse_bool(None, default=True) is True
    assert parse_bool("unexpected", default=False) is False


def test_parse_int_handles_valid_and_invalid_values():
    assert parse_int("8502", default=8501) == 8502
    assert parse_int("not-a-port", default=8501) == 8501
    assert parse_int(None, default=8000) == 8000


def test_get_settings_returns_safe_defaults(monkeypatch):
    for env_name in [
        "RESUMEIQ_APP_NAME",
        "RESUMEIQ_APP_ENV",
        "RESUMEIQ_DEBUG",
        "RESUMEIQ_LOG_LEVEL",
        "RESUMEIQ_API_BASE_URL",
        "RESUMEIQ_DATABASE_URL",
        "RESUMEIQ_MLFLOW_TRACKING_URI",
        "RESUMEIQ_MLFLOW_EXPERIMENT",
        "RESUMEIQ_MODEL_REGISTRY_PATH",
        "RESUMEIQ_PRIVACY_MODE_DEFAULT",
        "RESUMEIQ_SAVE_ANALYSIS_DEFAULT",
        "RESUMEIQ_STREAMLIT_PORT",
        "RESUMEIQ_API_PORT",
        "RESUMEIQ_DOCKER_MODE",
        "RESUMEIQ_EXTERNAL_GENAI_ENABLED",
        "RESUMEIQ_GENAI_PROVIDER",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GEMINI_API_KEY",
    ]:
        monkeypatch.delenv(env_name, raising=False)

    settings = get_settings()

    assert settings.app_name == "ResumeIQ"
    assert settings.app_env == "local"
    assert settings.debug is False
    assert settings.api_base_url == "http://127.0.0.1:8000"
    assert settings.database_url == "sqlite:///./resumeiq.db"
    assert settings.streamlit_port == 8501
    assert settings.api_port == 8000
    assert settings.external_genai_enabled is False
    assert settings.genai_provider == "none"
    assert settings.openai_api_key_configured is False


def test_get_settings_respects_env_override(monkeypatch):
    monkeypatch.setenv("RESUMEIQ_APP_ENV", "ci")
    monkeypatch.setenv("RESUMEIQ_DEBUG", "true")
    monkeypatch.setenv("RESUMEIQ_API_BASE_URL", "http://api:8000")
    monkeypatch.setenv("RESUMEIQ_STREAMLIT_PORT", "8502")
    monkeypatch.setenv("RESUMEIQ_DOCKER_MODE", "yes")
    monkeypatch.setenv("RESUMEIQ_EXTERNAL_GENAI_ENABLED", "true")
    monkeypatch.setenv("RESUMEIQ_GENAI_PROVIDER", "openai")

    settings = get_settings()

    assert settings.app_env == "ci"
    assert settings.debug is True
    assert settings.api_base_url == "http://api:8000"
    assert settings.streamlit_port == 8502
    assert settings.docker_mode is True
    assert settings.external_genai_enabled is True
    assert settings.genai_provider == "openai"


def test_settings_to_safe_dict_redacts_secret_like_keys_if_present():
    settings = ResumeIQSettings(
        app_name="ResumeIQ",
        app_env="local",
        debug=False,
        log_level="INFO",
        api_base_url="http://127.0.0.1:8000",
        database_url="sqlite:///./resumeiq.db",
        mlflow_tracking_uri="file:./mlruns",
        mlflow_experiment_name="ResumeIQ Baseline Experiments",
        model_registry_path="artifacts/model_registry/model_registry.json",
        privacy_mode_default=False,
        save_analysis_default=False,
        streamlit_port=8501,
        api_port=8000,
        docker_mode=False,
        external_genai_enabled=False,
        genai_provider="none",
        openai_api_key_configured=False,
        anthropic_api_key_configured=False,
        gemini_api_key_configured=False,
    )
    settings.future_api_key = "do-not-show"
    settings.future_password = "do-not-show"

    safe_settings = settings_to_safe_dict(settings)

    assert safe_settings["app_name"] == "ResumeIQ"
    assert safe_settings["future_api_key"] == "[redacted]"
    assert safe_settings["future_password"] == "[redacted]"


def test_settings_to_safe_dict_exposes_only_key_configured_status(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "real-key-value")

    safe_settings = settings_to_safe_dict(get_settings())

    assert safe_settings["openai_api_key_configured"] is True
    assert "real-key-value" not in str(safe_settings)


def test_get_runtime_summary_returns_sqlite_database_backend():
    settings = ResumeIQSettings(
        app_name="ResumeIQ",
        app_env="local",
        debug=False,
        log_level="INFO",
        api_base_url="http://127.0.0.1:8000",
        database_url="sqlite:///./resumeiq.db",
        mlflow_tracking_uri="file:./mlruns",
        mlflow_experiment_name="ResumeIQ Baseline Experiments",
        model_registry_path="artifacts/model_registry/model_registry.json",
        privacy_mode_default=False,
        save_analysis_default=False,
        streamlit_port=8501,
        api_port=8000,
        docker_mode=False,
        external_genai_enabled=False,
        genai_provider="none",
        openai_api_key_configured=False,
        anthropic_api_key_configured=False,
        gemini_api_key_configured=False,
    )

    summary = get_runtime_summary(settings)

    assert summary["database_backend"] == "sqlite"
    assert summary["mlflow_mode"] == "local_file"
    assert summary["model_registry_path"] == "artifacts/model_registry/model_registry.json"
    assert summary["external_genai"] == "disabled"
    assert summary["genai_provider"] == "none"


def test_env_example_exists_and_has_no_fake_real_secrets():
    env_example = Path(".env.example")

    assert env_example.exists()
    lines = env_example.read_text(encoding="utf-8").splitlines()
    active_lines = [line.strip().lower() for line in lines if line.strip() and not line.strip().startswith("#")]
    active_content = "\n".join(active_lines)
    assert "api_key=" not in active_content
    assert "password=" not in active_content
    assert "secret=" not in active_content
    content = "\n".join(lines).lower()
    assert "sk-" not in content
