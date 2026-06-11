from time import perf_counter

from fastapi import APIRouter, HTTPException, Request

from backend.schemas.copilot_schema import CopilotRequest, CopilotResponse
from src.monitoring import format_latency_ms, get_logger, log_event
from src.rag_copilot import ask_recruiter_copilot

try:
    from database.db import get_db_session
    from database.repositories import create_api_request_log
except Exception:
    get_db_session = None
    create_api_request_log = None


router = APIRouter(prefix="/copilot", tags=["copilot"])
logger = get_logger(__name__)


def _save_api_request_log(status_code: int, success: bool, message: str, latency_ms: float | None) -> None:
    if get_db_session is None or create_api_request_log is None:
        logger.warning("Database logging is unavailable for copilot API request logs.")
        return
    try:
        with get_db_session() as session:
            create_api_request_log(
                session,
                {
                    "endpoint": "/copilot/ask",
                    "method": "POST",
                    "status_code": status_code,
                    "latency_ms": latency_ms,
                    "success": success,
                    "message": message,
                },
            )
    except Exception:
        logger.warning("Database logging failed for copilot API request metadata.")


@router.post("/ask", response_model=CopilotResponse)
def ask_copilot(request: CopilotRequest, http_request: Request) -> CopilotResponse:
    start_time = perf_counter()
    request_id = getattr(http_request.state, "request_id", None)
    try:
        result = ask_recruiter_copilot(
            query=request.query,
            resume_text=request.resume_text,
            job_description=request.job_description,
            privacy_mode=request.privacy_mode,
            candidate_name=request.candidate_name,
            top_k=request.top_k,
        )
        latency_ms = format_latency_ms(perf_counter() - start_time)
        evidence = result.get("evidence", []) if isinstance(result.get("evidence"), list) else []
        question_type = result.get("question_type", "unknown")
        _save_api_request_log(
            status_code=200,
            success=True,
            message="Copilot retrieval completed",
            latency_ms=latency_ms,
        )
        log_event(
            logger,
            "copilot_request_completed",
            "Copilot retrieval request completed.",
            {
                "request_id": request_id,
                "endpoint": "/copilot/ask",
                "method": "POST",
                "status_code": 200,
                "question_type": question_type,
                "evidence_count": len(evidence),
                "privacy_mode": request.privacy_mode,
                "latency_ms": latency_ms,
                "success": True,
            },
        )
        return CopilotResponse(
            status="success",
            answer=result.get("answer", ""),
            question_type=question_type,
            evidence=evidence,
            limitations=result.get("limitations", []),
            disclaimer=result.get("disclaimer", ""),
            privacy_mode=request.privacy_mode,
        )
    except Exception as exc:
        latency_ms = format_latency_ms(perf_counter() - start_time)
        _save_api_request_log(
            status_code=500,
            success=False,
            message="Copilot retrieval failed safely",
            latency_ms=latency_ms,
        )
        log_event(
            logger,
            "copilot_request_failed",
            "Copilot retrieval failed safely in /copilot/ask.",
            {
                "request_id": request_id,
                "endpoint": "/copilot/ask",
                "method": "POST",
                "status_code": 500,
                "privacy_mode": request.privacy_mode,
                "latency_ms": latency_ms,
                "success": False,
            },
            level="warning",
        )
        raise HTTPException(
            status_code=500,
            detail="Copilot retrieval failed safely. Check backend logs for details.",
        ) from exc
