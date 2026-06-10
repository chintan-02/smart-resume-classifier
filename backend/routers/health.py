from fastapi import APIRouter


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
    }

    try:
        import src.ats_scorer  # noqa: F401
        import src.jd_matcher  # noqa: F401
        import src.prediction_service  # noqa: F401
    except Exception as exc:
        checks["local_analysis_modules"] = "warning"
        checks["warning"] = f"Local analysis modules could not be fully imported: {exc}"

    return {
        "status": "ready",
        "checks": checks,
    }
