from fastapi import APIRouter, HTTPException

from backend.schemas.resume_schema import ResumeAnalysisRequest, ResumeAnalysisResponse
from backend.services.analysis_service import analyze_resume_text


router = APIRouter()


@router.post("/analyze-resume", response_model=ResumeAnalysisResponse)
def analyze_resume(request: ResumeAnalysisRequest) -> ResumeAnalysisResponse:
    try:
        result = analyze_resume_text(
            resume_text=request.resume_text,
            job_description=request.job_description,
            privacy_mode=request.privacy_mode,
        )
        return ResumeAnalysisResponse(**result)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Resume analysis failed safely. Check backend logs for details.",
        ) from exc
