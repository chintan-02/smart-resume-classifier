from time import perf_counter

from fastapi import APIRouter, HTTPException, Request

from backend.schemas.genai_prompt_schema import PromptPreviewRequest, PromptPreviewResponse
from src.genai_planning import is_external_genai_enabled
from src.genai_prompt_builder import build_prompt_preview
from src.monitoring import format_latency_ms, get_logger, log_event


PROMPT_PREVIEW_DISCLAIMER = "This endpoint builds a prompt preview only. It does not call external GenAI providers."

router = APIRouter(prefix="/genai", tags=["genai"])
logger = get_logger(__name__)


def _build_prompt_kwargs(request: PromptPreviewRequest, external_enabled: bool) -> dict:
    base_kwargs = {
        "consent_given": request.consent_given,
        "external_enabled": external_enabled,
    }
    if request.task_type == "resume_bullet_rewrite":
        return {
            **base_kwargs,
            "original_bullet": request.original_bullet or "",
            "target_role": request.target_role or request.user_goal,
            "evidence": request.resume_evidence,
            "privacy_mode": request.privacy_mode,
            "candidate_name": request.candidate_name,
        }
    if request.task_type == "cover_letter":
        return {
            **base_kwargs,
            "resume_evidence": request.resume_evidence,
            "job_description_evidence": request.job_description_evidence,
            "company_name": request.company_name,
            "role_title": request.role_title,
            "privacy_mode": request.privacy_mode,
            "candidate_name": request.candidate_name,
        }
    if request.task_type == "recruiter_email":
        return {
            **base_kwargs,
            "resume_evidence": request.resume_evidence,
            "job_description_evidence": request.job_description_evidence,
            "recruiter_name": request.recruiter_name,
            "role_title": request.role_title,
            "privacy_mode": request.privacy_mode,
            "candidate_name": request.candidate_name,
        }
    if request.task_type == "linkedin_message":
        return {
            **base_kwargs,
            "resume_evidence": request.resume_evidence,
            "job_description_evidence": request.job_description_evidence,
            "recipient_name": request.recipient_name,
            "role_title": request.role_title,
            "privacy_mode": request.privacy_mode,
            "candidate_name": request.candidate_name,
        }
    if request.task_type == "interview_questions":
        return {
            **base_kwargs,
            "resume_evidence": request.resume_evidence,
            "job_description_evidence": request.job_description_evidence,
            "target_role": request.target_role or request.user_goal,
            "privacy_mode": request.privacy_mode,
            "candidate_name": request.candidate_name,
        }
    if request.task_type == "rag_answer_generation":
        return {
            **base_kwargs,
            "query": request.query or "",
            "retrieved_evidence": request.retrieved_evidence or [],
            "privacy_mode": request.privacy_mode,
            "candidate_name": request.candidate_name,
        }
    if request.task_type == "candidate_summary":
        return {
            **base_kwargs,
            "resume_evidence": request.resume_evidence,
            "job_description_evidence": request.job_description_evidence,
            "privacy_mode": request.privacy_mode,
            "candidate_name": request.candidate_name,
        }
    if request.task_type == "resume_gap_explanation":
        return {
            **base_kwargs,
            "resume_evidence": request.resume_evidence,
            "job_description_evidence": request.job_description_evidence,
            "privacy_mode": request.privacy_mode,
            "candidate_name": request.candidate_name,
        }
    return base_kwargs


@router.post("/prompt-preview", response_model=PromptPreviewResponse)
def build_prompt_preview_endpoint(
    request: PromptPreviewRequest,
    http_request: Request,
) -> PromptPreviewResponse:
    start_time = perf_counter()
    request_id = getattr(http_request.state, "request_id", None)
    external_enabled = is_external_genai_enabled()
    try:
        prompt_preview = build_prompt_preview(
            request.task_type,
            **_build_prompt_kwargs(request, external_enabled),
        )
        latency_ms = format_latency_ms(perf_counter() - start_time)
        allowed = bool(prompt_preview.get("allowed_for_external_use", False))
        log_event(
            logger,
            "genai_prompt_preview_completed",
            "GenAI prompt preview request completed.",
            {
                "request_id": request_id,
                "endpoint": "/genai/prompt-preview",
                "method": "POST",
                "task_type": request.task_type,
                "privacy_mode": request.privacy_mode,
                "consent_given": request.consent_given,
                "allowed_for_external_use": allowed,
                "status_code": 200,
                "latency_ms": latency_ms,
                "success": True,
            },
        )
        return PromptPreviewResponse(
            status="success",
            task_type=request.task_type,
            prompt_preview=prompt_preview,
            external_generation_enabled=external_enabled,
            allowed_for_external_use=allowed,
            blocked_reason=prompt_preview.get("blocked_reason"),
            disclaimer=PROMPT_PREVIEW_DISCLAIMER,
        )
    except Exception as exc:
        latency_ms = format_latency_ms(perf_counter() - start_time)
        log_event(
            logger,
            "genai_prompt_preview_failed",
            "Prompt preview failed safely in /genai/prompt-preview.",
            {
                "request_id": request_id,
                "endpoint": "/genai/prompt-preview",
                "method": "POST",
                "task_type": request.task_type,
                "privacy_mode": request.privacy_mode,
                "consent_given": request.consent_given,
                "status_code": 500,
                "latency_ms": latency_ms,
                "success": False,
            },
            level="warning",
        )
        raise HTTPException(
            status_code=500,
            detail="Prompt preview failed safely. Check backend logs for details.",
        ) from exc
