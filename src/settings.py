import os
from dataclasses import dataclass


SENSITIVE_KEY_PARTS = ("secret", "token", "password", "api_key", "authorization")


@dataclass
class ResumeIQSettings:
    app_name: str
    app_env: str
    debug: bool
    log_level: str
    api_base_url: str
    database_url: str
    mlflow_tracking_uri: str
    mlflow_experiment_name: str
    model_registry_path: str
    privacy_mode_default: bool
    save_analysis_default: bool
    streamlit_port: int
    api_port: int
    docker_mode: bool
    external_genai_enabled: bool
    genai_provider: str
    openai_api_key_configured: bool
    anthropic_api_key_configured: bool
    gemini_api_key_configured: bool


def parse_bool(value, default=False) -> bool:
    if value is None:
        return default
    normalized_value = str(value).strip().lower()
    if normalized_value in {"true", "1", "yes", "y", "on"}:
        return True
    if normalized_value in {"false", "0", "no", "n", "off"}:
        return False
    return default


def parse_int(value, default) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def get_settings() -> ResumeIQSettings:
    return ResumeIQSettings(
        app_name=os.getenv("RESUMEIQ_APP_NAME", "ResumeIQ"),
        app_env=os.getenv("RESUMEIQ_APP_ENV", "local"),
        debug=parse_bool(os.getenv("RESUMEIQ_DEBUG"), default=False),
        log_level=os.getenv("RESUMEIQ_LOG_LEVEL", "INFO"),
        api_base_url=os.getenv("RESUMEIQ_API_BASE_URL", "http://127.0.0.1:8000"),
        database_url=os.getenv("RESUMEIQ_DATABASE_URL", "sqlite:///./resumeiq.db"),
        mlflow_tracking_uri=os.getenv("RESUMEIQ_MLFLOW_TRACKING_URI", "file:./mlruns"),
        mlflow_experiment_name=os.getenv(
            "RESUMEIQ_MLFLOW_EXPERIMENT",
            "ResumeIQ Baseline Experiments",
        ),
        model_registry_path=os.getenv(
            "RESUMEIQ_MODEL_REGISTRY_PATH",
            "artifacts/model_registry/model_registry.json",
        ),
        privacy_mode_default=parse_bool(os.getenv("RESUMEIQ_PRIVACY_MODE_DEFAULT"), default=False),
        save_analysis_default=parse_bool(os.getenv("RESUMEIQ_SAVE_ANALYSIS_DEFAULT"), default=False),
        streamlit_port=parse_int(os.getenv("RESUMEIQ_STREAMLIT_PORT"), default=8501),
        api_port=parse_int(os.getenv("RESUMEIQ_API_PORT"), default=8000),
        docker_mode=parse_bool(os.getenv("RESUMEIQ_DOCKER_MODE"), default=False),
        external_genai_enabled=parse_bool(os.getenv("RESUMEIQ_EXTERNAL_GENAI_ENABLED"), default=False),
        genai_provider=os.getenv("RESUMEIQ_GENAI_PROVIDER", "none"),
        openai_api_key_configured=bool(os.getenv("OPENAI_API_KEY")),
        anthropic_api_key_configured=bool(os.getenv("ANTHROPIC_API_KEY")),
        gemini_api_key_configured=bool(os.getenv("GEMINI_API_KEY")),
    )


def settings_to_safe_dict(settings=None) -> dict:
    settings = settings or get_settings()
    safe_settings = {}
    for key, value in vars(settings).items():
        normalized_key = str(key).lower()
        if normalized_key.endswith("_api_key_configured"):
            safe_settings[key] = bool(value)
        elif any(sensitive_part in normalized_key for sensitive_part in SENSITIVE_KEY_PARTS):
            safe_settings[key] = "[redacted]"
        else:
            safe_settings[key] = value
    return safe_settings


def get_runtime_summary(settings=None) -> dict:
    settings = settings or get_settings()
    database_url = settings.database_url or ""
    tracking_uri = settings.mlflow_tracking_uri or ""
    return {
        "app_env": settings.app_env,
        "docker_mode": settings.docker_mode,
        "api_base_url": settings.api_base_url,
        "database_backend": "sqlite" if database_url.startswith("sqlite") else "other",
        "mlflow_mode": "local_file" if tracking_uri.startswith("file") else "remote_or_custom",
        "model_registry_path": settings.model_registry_path,
        "privacy_mode_default": settings.privacy_mode_default,
        "save_analysis_default": settings.save_analysis_default,
        "external_genai": "enabled_with_consent_required" if settings.external_genai_enabled else "disabled",
        "genai_provider": settings.genai_provider,
    }
