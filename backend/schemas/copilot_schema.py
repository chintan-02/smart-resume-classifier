from pydantic import BaseModel, Field


class CopilotRequest(BaseModel):
    query: str = Field(..., min_length=3)
    resume_text: str = Field(..., min_length=20)
    job_description: str | None = None
    privacy_mode: bool = False
    candidate_name: str | None = None
    top_k: int = Field(default=5, ge=1, le=10)


class CopilotEvidenceItem(BaseModel):
    rank: int
    source: str
    chunk_id: str
    score: float | None = None
    text: str


class CopilotResponse(BaseModel):
    status: str
    answer: str
    question_type: str
    evidence: list[CopilotEvidenceItem]
    limitations: list[str]
    disclaimer: str
    privacy_mode: bool
    source: str = "fastapi_local_retrieval"


class CopilotErrorResponse(BaseModel):
    status: str
    message: str
    details: str | None = None
