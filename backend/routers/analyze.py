from time import perf_counter

from fastapi import APIRouter, HTTPException, Request

from backend.schemas.resume_schema import ResumeAnalysisRequest, ResumeAnalysisResponse
from backend.services.analysis_service import analyze_resume_text
from src.monitoring import format_latency_ms, get_logger, log_event

try:
    from database.db import get_db_session
    from database.repositories import create_analysis_run, create_api_request_log
except Exception:
    get_db_session = None
    create_analysis_run = None
    create_api_request_log = None


router = APIRouter()
logger = get_logger(__name__)


def _save_analysis_run(result: dict, privacy_mode: bool) -> None:
    if get_db_session is None or create_analysis_run is None:
        logger.warning("Database logging is unavailable for analysis summary saves.")
        return
    try:
        with get_db_session() as session:
            priority_actions = result.get("priority_actions", [])
            create_analysis_run(
                session,
                {
                    "source": "fastapi",
                    "predicted_role": result.get("predicted_role"),
                    "model_confidence": result.get("model_confidence"),
                    "ats_score": result.get("ats_score"),
                    "jd_match_score": result.get("jd_match_score"),
                    "privacy_mode": privacy_mode,
                    "recommendation": priority_actions[0] if priority_actions else None,
                    "notes": "Saved from FastAPI /analyze-resume endpoint",
                },
            )
    except Exception:
        logger.warning("Database logging failed for FastAPI analysis summary.")


def _save_api_request_log(status_code: int, success: bool, message: str, latency_ms: float | None) -> None:
    if get_db_session is None or create_api_request_log is None:
        logger.warning("Database logging is unavailable for API request logs.")
        return
    try:
        with get_db_session() as session:
            create_api_request_log(
                session,
                {
                    "endpoint": "/analyze-resume",
                    "method": "POST",
                    "status_code": status_code,
                    "latency_ms": latency_ms,
                    "success": success,
                    "message": message,
                },
            )
    except Exception:
        logger.warning("Database logging failed for FastAPI request metadata.")


def _save_successful_analysis(result: dict, privacy_mode: bool, latency_ms: float | None) -> None:
    _save_analysis_run(result, privacy_mode)
    _save_api_request_log(
        status_code=200,
        success=True,
        message="Resume analysis completed",
        latency_ms=latency_ms,
    )


def _save_failed_api_request(latency_ms: float | None) -> None:
    _save_api_request_log(
        status_code=500,
        success=False,
        message="Resume analysis failed safely",
        latency_ms=latency_ms,
    )


@router.post("/analyze-resume", response_model=ResumeAnalysisResponse)
def analyze_resume(request: ResumeAnalysisRequest, http_request: Request) -> ResumeAnalysisResponse:
    start_time = perf_counter()
    request_id = getattr(http_request.state, "request_id", None)
    try:
        result = analyze_resume_text(
            resume_text=request.resume_text,
            job_description=request.job_description,
            privacy_mode=request.privacy_mode,
        )
        latency_ms = format_latency_ms(perf_counter() - start_time)
        _save_successful_analysis(result, request.privacy_mode, latency_ms)
        log_event(
            logger,
            "analysis_request_completed",
            "Resume analysis request completed.",
            {
                "request_id": request_id,
                "endpoint": "/analyze-resume",
                "status_code": 200,
                "latency_ms": latency_ms,
                "predicted_role": result.get("predicted_role"),
                "model_confidence": result.get("model_confidence"),
                "ats_score": result.get("ats_score"),
                "jd_match_score": result.get("jd_match_score"),
                "privacy_mode": request.privacy_mode,
                "success": True,
            },
        )
        return ResumeAnalysisResponse(**result)
    except Exception as exc:
        latency_ms = format_latency_ms(perf_counter() - start_time)
        _save_failed_api_request(latency_ms)
        log_event(
            logger,
            "analysis_request_failed",
            "Resume analysis failed safely in /analyze-resume.",
            {
                "request_id": request_id,
                "endpoint": "/analyze-resume",
                "status_code": 500,
                "latency_ms": latency_ms,
                "privacy_mode": request.privacy_mode,
                "success": False,
            },
            level="warning",
        )
        raise HTTPException(
            status_code=500,
            detail="Resume analysis failed safely. Check backend logs for details.",
        ) from exc
