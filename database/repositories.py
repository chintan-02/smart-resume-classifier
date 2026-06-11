import json
from typing import Any

from database.models import (
    AnalysisRun,
    ApiRequestLog,
    AuditLog,
    BatchRankingRun,
    CandidateReviewRecord,
)


def safe_commit(session) -> bool:
    try:
        session.commit()
        return True
    except Exception:
        session.rollback()
        return False


def _create_record(session, model_class, data: dict):
    record = model_class(**(data or {}))
    session.add(record)
    if not safe_commit(session):
        raise RuntimeError(f"Could not save {model_class.__name__} record.")
    session.refresh(record)
    return record


def _safe_number(value: Any):
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_int(value: Any, default: int | None = None):
    if value is None or value == "":
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def create_analysis_run(session, data: dict) -> AnalysisRun:
    data = data or {}
    safe_data = {
        "source": data.get("source", "unknown"),
        "resume_filename": data.get("resume_filename"),
        "predicted_role": data.get("predicted_role"),
        "model_confidence": _safe_number(data.get("model_confidence")),
        "ats_score": _safe_number(data.get("ats_score")),
        "jd_match_score": _safe_number(data.get("jd_match_score")),
        "semantic_score": _safe_number(data.get("semantic_score")),
        "overall_fit_score": _safe_number(data.get("overall_fit_score")),
        "fit_label": data.get("fit_label"),
        "recommendation": data.get("recommendation"),
        "privacy_mode": bool(data.get("privacy_mode", False)),
        "notes": data.get("notes"),
    }
    return _create_record(session, AnalysisRun, safe_data)


def create_batch_ranking_run(session, data: dict) -> BatchRankingRun:
    data = data or {}
    safe_data = {
        "job_description_hash": data.get("job_description_hash"),
        "total_resumes": _safe_int(data.get("total_resumes"), 0),
        "average_fit_score": _safe_number(data.get("average_fit_score")),
        "recommended_count": _safe_int(data.get("recommended_count"), 0),
        "privacy_mode": bool(data.get("privacy_mode", False)),
        "notes": data.get("notes"),
    }
    return _create_record(session, BatchRankingRun, safe_data)


def create_candidate_review_record(session, data: dict) -> CandidateReviewRecord:
    data = data or {}
    safe_data = {
        "batch_run_id": data.get("batch_run_id"),
        "candidate_label": data.get("candidate_label"),
        "resume_filename": data.get("resume_filename"),
        "rank": _safe_int(data.get("rank")),
        "overall_fit_score": _safe_number(data.get("overall_fit_score")),
        "fit_label": data.get("fit_label"),
        "recommendation": data.get("recommendation"),
        "manual_review_status": data.get("manual_review_status"),
        "recruiter_note": data.get("recruiter_note"),
        "priority_actions": data.get("priority_actions"),
    }
    return _create_record(session, CandidateReviewRecord, safe_data)


def create_audit_log(
    session,
    event_type: str,
    message: str,
    event_source: str | None = None,
    metadata: dict | None = None,
) -> AuditLog:
    metadata_json = json.dumps(metadata or {}, sort_keys=True) if metadata is not None else None
    safe_data = {
        "event_type": event_type,
        "event_source": event_source,
        "message": message,
        "metadata_json": metadata_json,
    }
    return _create_record(session, AuditLog, safe_data)


def create_api_request_log(session, data: dict) -> ApiRequestLog:
    data = data or {}
    safe_data = {
        "endpoint": data.get("endpoint", "unknown"),
        "method": data.get("method", "unknown"),
        "status_code": _safe_int(data.get("status_code")),
        "latency_ms": _safe_number(data.get("latency_ms")),
        "success": bool(data.get("success", True)),
        "message": data.get("message"),
    }
    return _create_record(session, ApiRequestLog, safe_data)


def list_recent_analysis_runs(session, limit: int = 20) -> list[AnalysisRun]:
    return (
        session.query(AnalysisRun)
        .order_by(AnalysisRun.created_at.desc())
        .limit(max(int(limit), 0))
        .all()
    )


def list_recent_batch_runs(session, limit: int = 20) -> list[BatchRankingRun]:
    return (
        session.query(BatchRankingRun)
        .order_by(BatchRankingRun.created_at.desc())
        .limit(max(int(limit), 0))
        .all()
    )
