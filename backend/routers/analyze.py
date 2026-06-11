from time import perf_counter

from fastapi import APIRouter, HTTPException

from backend.schemas.resume_schema import ResumeAnalysisRequest, ResumeAnalysisResponse
from backend.services.analysis_service import analyze_resume_text
from database.db import get_db_session
from database.repositories import create_analysis_run, create_api_request_log


router = APIRouter()


def _save_successful_analysis(result: dict, privacy_mode: bool, latency_ms: float) -> None:
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
            create_api_request_log(
                session,
                {
                    "endpoint": "/analyze-resume",
                    "method": "POST",
                    "status_code": 200,
                    "latency_ms": latency_ms,
                    "success": True,
                    "message": "Resume analysis completed",
                },
            )
    except Exception:
        pass


def _save_failed_api_request(latency_ms: float) -> None:
    try:
        with get_db_session() as session:
            create_api_request_log(
                session,
                {
                    "endpoint": "/analyze-resume",
                    "method": "POST",
                    "status_code": 500,
                    "latency_ms": latency_ms,
                    "success": False,
                    "message": "Resume analysis failed safely.",
                },
            )
    except Exception:
        pass


@router.post("/analyze-resume", response_model=ResumeAnalysisResponse)
def analyze_resume(request: ResumeAnalysisRequest) -> ResumeAnalysisResponse:
    start_time = perf_counter()
    try:
        result = analyze_resume_text(
            resume_text=request.resume_text,
            job_description=request.job_description,
            privacy_mode=request.privacy_mode,
        )
        latency_ms = (perf_counter() - start_time) * 1000
        _save_successful_analysis(result, request.privacy_mode, latency_ms)
        return ResumeAnalysisResponse(**result)
    except Exception as exc:
        latency_ms = (perf_counter() - start_time) * 1000
        _save_failed_api_request(latency_ms)
        raise HTTPException(
            status_code=500,
            detail="Resume analysis failed safely. Check backend logs for details.",
        ) from exc
