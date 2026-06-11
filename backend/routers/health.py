from pathlib import Path

from fastapi import APIRouter

from src.settings import get_runtime_summary

try:
    from experiment_tracking.mlflow_tracker import is_mlflow_available
except Exception:
    is_mlflow_available = None

try:
    from sqlalchemy import inspect, text
    from database.db import engine
except Exception:
    inspect = None
    text = None
    engine = None


router = APIRouter()


@router.get("/health")
def health_check() -> dict:
    return {
        "status": "ok",
        "service": "ResumeIQ API",
    }


@router.get("/ready")
def readiness_check() -> dict:
    runtime_summary = get_runtime_summary()
    checks = {
        "api": "ok",
        "config": "loaded",
        "app_env": runtime_summary.get("app_env"),
        "docker_mode": runtime_summary.get("docker_mode"),
        "local_analysis_modules": "available",
        "database": "unavailable",
        "logging": "enabled",
        "monitoring": "local_foundation",
        "model_registry": "not_initialized",
        "mlflow": "optional_not_installed",
        "rag_copilot": "unavailable",
        "external_genai": runtime_summary.get("external_genai", "disabled"),
        "genai_provider": runtime_summary.get("genai_provider", "none"),
    }

    try:
        import src.ats_scorer  # noqa: F401
        import src.jd_matcher  # noqa: F401
        import src.prediction_service  # noqa: F401
    except Exception as exc:
        checks["local_analysis_modules"] = "warning"
        checks["warning"] = f"Local analysis modules could not be fully imported: {exc}"

    try:
        import src.rag_copilot  # noqa: F401
        checks["rag_copilot"] = "available"
    except Exception:
        checks["rag_copilot"] = "unavailable"

    try:
        if engine is None or inspect is None or text is None:
            raise RuntimeError("Database support is unavailable.")
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        inspector = inspect(engine)
        checks["database"] = "available" if inspector.has_table("analysis_runs") else "not_initialized"
    except Exception:
        checks["database"] = "unavailable"

    try:
        registry_path = Path(runtime_summary.get("model_registry_path", "artifacts/model_registry/model_registry.json"))
        checks["model_registry"] = "available" if registry_path.exists() else "not_initialized"
    except Exception:
        checks["model_registry"] = "not_initialized"

    try:
        checks["mlflow"] = "available" if is_mlflow_available and is_mlflow_available() else "optional_not_installed"
    except Exception:
        checks["mlflow"] = "optional_not_installed"

    return {
        "status": "ready",
        "checks": checks,
    }
