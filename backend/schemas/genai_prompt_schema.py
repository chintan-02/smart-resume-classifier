from pydantic import BaseModel, Field, field_validator


class PromptPreviewRequest(BaseModel):
    task_type: str = Field(..., min_length=3)
    resume_evidence: list[str] | None = None
    job_description_evidence: list[str] | None = None
    user_goal: str | None = None
    original_bullet: str | None = Field(default=None, max_length=2000)
    target_role: str | None = None
    company_name: str | None = None
    role_title: str | None = None
    recruiter_name: str | None = None
    recipient_name: str | None = None
    query: str | None = None
    retrieved_evidence: list[dict] | None = None
    privacy_mode: bool = True
    candidate_name: str | None = None
    consent_given: bool = False

    @field_validator("resume_evidence", "job_description_evidence")
    @classmethod
    def evidence_list_has_reasonable_size(cls, value):
        if value is not None and len(value) > 20:
            raise ValueError("Evidence lists can contain at most 20 items.")
        return value


class PromptPreviewResponse(BaseModel):
    status: str
    task_type: str
    prompt_preview: dict
    external_generation_enabled: bool
    allowed_for_external_use: bool
    blocked_reason: str | None = None
    disclaimer: str
    source: str = "fastapi_prompt_preview"
