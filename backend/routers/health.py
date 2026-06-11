from fastapi import APIRouter

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
    checks = {
        "api": "ok",
        "local_analysis_modules": "available",
        "database": "unavailable",
    }

    try:
        import src.ats_scorer  # noqa: F401
        import src.jd_matcher  # noqa: F401
        import src.prediction_service  # noqa: F401
    except Exception as exc:
        checks["local_analysis_modules"] = "warning"
        checks["warning"] = f"Local analysis modules could not be fully imported: {exc}"

    try:
        if engine is None or inspect is None or text is None:
            raise RuntimeError("Database support is unavailable.")
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        inspector = inspect(engine)
        checks["database"] = "available" if inspector.has_table("analysis_runs") else "not_initialized"
    except Exception:
        checks["database"] = "unavailable"

    return {
        "status": "ready",
        "checks": checks,
    }
