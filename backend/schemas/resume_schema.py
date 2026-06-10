from pydantic import BaseModel, Field


class ResumeAnalysisRequest(BaseModel):
    resume_text: str = Field(..., min_length=20)
    job_description: str | None = None
    privacy_mode: bool = False


class ResumeAnalysisResponse(BaseModel):
    status: str
    predicted_role: str | None
    model_confidence: float | None
    ats_score: float | None
    jd_match_score: float | None
    matched_skills: list[str]
    missing_skills: list[str]
    priority_actions: list[str]
    privacy_mode: bool
    disclaimer: str


class ErrorResponse(BaseModel):
    status: str
    message: str
    details: str | None = None
