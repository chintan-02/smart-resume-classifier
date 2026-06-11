from src.privacy_tools import mask_pii
from src.settings import get_settings, parse_bool


def get_supported_future_genai_features() -> list[dict]:
    features = [
        (
            "resume_bullet_rewrite",
            "Resume bullet rewrite suggestions",
            "Rewrite resume bullets using provided resume evidence while preserving truthfulness.",
            "medium",
        ),
        (
            "cover_letter",
            "Tailored cover letter draft",
            "Draft a cover letter from provided resume and job-description evidence.",
            "high",
        ),
        (
            "recruiter_email",
            "Recruiter outreach email",
            "Draft a professional recruiter outreach email from user-approved context.",
            "high",
        ),
        (
            "linkedin_message",
            "LinkedIn cold message",
            "Draft a concise LinkedIn message from user-approved context.",
            "high",
        ),
        (
            "interview_questions",
            "Interview question preparation",
            "Generate interview preparation questions from the target role and provided evidence.",
            "medium",
        ),
        (
            "rag_answer_generation",
            "RAG recruiter copilot answer generation",
            "Generate cautious explanations from retrieved resume and job-description evidence.",
            "high",
        ),
        (
            "candidate_summary",
            "Candidate summary for recruiter review",
            "Summarize provided resume evidence for human recruiter review.",
            "high",
        ),
        (
            "resume_gap_explanation",
            "Resume gap explanation",
            "Explain potential resume/job-description gaps using only provided evidence.",
            "medium",
        ),
    ]
    return [
        {
            "feature_key": feature_key,
            "feature_name": feature_name,
            "description": description,
            "status": "planned",
            "requires_external_provider": True,
            "requires_user_consent": True,
            "pii_risk_level": pii_risk_level,
            "safe_default": "disabled",
        }
        for feature_key, feature_name, description, pii_risk_level in features
    ]


def get_genai_provider_placeholders() -> list[dict]:
    return [
        {
            "provider_key": "openai",
            "provider_name": "OpenAI",
            "status": "external_planned",
            "notes": "Future optional provider. No API calls are implemented.",
        },
        {
            "provider_key": "anthropic",
            "provider_name": "Anthropic Claude",
            "status": "external_planned",
            "notes": "Future optional provider. No API calls are implemented.",
        },
        {
            "provider_key": "gemini",
            "provider_name": "Google Gemini",
            "status": "external_planned",
            "notes": "Future optional provider. No API calls are implemented.",
        },
        {
            "provider_key": "local_llm",
            "provider_name": "Local LLM",
            "status": "local_planned",
            "notes": "Future optional local model path. No model runtime is connected.",
        },
    ]


def get_genai_safety_policy() -> dict:
    return {
        "external_ai_enabled": False,
        "default_mode": "local_only",
        "requires_explicit_consent": True,
        "never_send_without_consent": [
            "full resume text",
            "full job description",
            "email",
            "phone",
            "address",
            "LinkedIn/GitHub profile URLs",
            "candidate name",
        ],
        "allowed_current_behavior": [
            "local resume parsing",
            "local scoring",
            "local TF-IDF retrieval",
            "privacy-safe display masking",
        ],
        "future_requirements": [
            "user consent checkbox",
            "PII masking before external calls",
            "provider configuration through environment variables",
            "safe fallback when provider unavailable",
            "clear generated-content disclaimer",
        ],
    }


def is_external_genai_enabled() -> bool:
    return parse_bool(get_settings().external_genai_enabled, default=False)


def check_genai_consent(consent_given: bool, external_enabled: bool | None = None) -> dict:
    external_enabled = is_external_genai_enabled() if external_enabled is None else bool(external_enabled)
    if not external_enabled:
        return {
            "allowed": False,
            "reason": "External GenAI providers are disabled. ResumeIQ is running in local-only mode.",
            "mode": "local_only",
        }
    if not consent_given:
        return {
            "allowed": False,
            "reason": (
                "Explicit consent is required before sending resume or job-description content "
                "to an external GenAI provider."
            ),
            "mode": "local_only",
        }
    return {
        "allowed": True,
        "reason": "External GenAI is enabled and explicit consent has been provided.",
        "mode": "external_allowed",
    }


def redact_for_external_genai(text: str, candidate_name: str | None = None) -> str:
    return mask_pii(text, candidate_name=candidate_name)


def get_future_prompt_templates() -> dict:
    safety_reminder = (
        "Use only the provided evidence. Do not invent experience, tools, companies, dates, or outcomes. "
        "Preserve truthfulness, avoid hiring decision language, and require human review."
    )
    return {
        "resume_bullet_rewrite": (
            f"{safety_reminder}\nRewrite the selected resume bullet using stronger action, context, and impact."
        ),
        "cover_letter": (
            f"{safety_reminder}\nDraft a concise cover letter using only the provided resume and job-description evidence."
        ),
        "recruiter_email": (
            f"{safety_reminder}\nDraft a professional recruiter outreach email from the provided evidence."
        ),
        "linkedin_message": (
            f"{safety_reminder}\nDraft a short LinkedIn cold message using only the provided evidence."
        ),
        "interview_questions": (
            f"{safety_reminder}\nCreate interview preparation questions grounded in the provided role and resume evidence."
        ),
        "rag_answer_generation": (
            f"{safety_reminder}\nAnswer the recruiter question using only retrieved evidence snippets."
        ),
    }


def build_genai_readiness_summary() -> dict:
    settings = get_settings()
    external_enabled = is_external_genai_enabled()
    policy = get_genai_safety_policy()
    return {
        "external_genai_enabled": external_enabled,
        "current_mode": "local_only",
        "planned_features_count": len(get_supported_future_genai_features()),
        "providers_planned": [provider["provider_name"] for provider in get_genai_provider_placeholders()],
        "consent_required": True,
        "privacy_guardrails": policy["future_requirements"],
        "next_steps": [
            "Add explicit user consent controls before any external provider call.",
            "Mask PII before external GenAI use.",
            "Read provider choice and configured-key status from safe settings.",
            "Keep local fallback available when provider calls are unavailable.",
        ],
        "provider": settings.genai_provider,
    }
