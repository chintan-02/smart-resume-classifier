from src.genai_planning import check_genai_consent, redact_for_external_genai


TASK_DEFINITIONS = [
    (
        "resume_bullet_rewrite",
        "Resume bullet rewrite",
        "Prepare a safe prompt to improve one resume bullet without inventing details.",
    ),
    (
        "cover_letter",
        "Cover letter",
        "Prepare a safe prompt for a tailored cover letter from provided evidence.",
    ),
    (
        "recruiter_email",
        "Recruiter email",
        "Prepare a concise recruiter outreach email prompt from provided evidence.",
    ),
    (
        "linkedin_message",
        "LinkedIn message",
        "Prepare a short professional LinkedIn message prompt from provided evidence.",
    ),
    (
        "interview_questions",
        "Interview questions",
        "Prepare interview-practice question instructions from resume and role evidence.",
    ),
    (
        "rag_answer_generation",
        "RAG answer generation",
        "Prepare a grounded answer-generation prompt from retrieved evidence snippets.",
    ),
    (
        "candidate_summary",
        "Candidate summary",
        "Prepare a recruiter-review summary prompt from provided evidence.",
    ),
    (
        "resume_gap_explanation",
        "Resume gap explanation",
        "Prepare a prompt to explain resume/job-description gaps using only evidence.",
    ),
]


def get_prompt_task_types() -> list[dict]:
    return [
        {
            "task_key": task_key,
            "task_name": task_name,
            "description": description,
            "status": "prompt_template_ready",
            "external_generation_status": "disabled",
            "requires_consent": True,
            "requires_pii_redaction": True,
        }
        for task_key, task_name, description in TASK_DEFINITIONS
    ]


def build_system_safety_instructions(task_type: str | None = None) -> str:
    task_note = f" Task type: {task_type}." if task_type else ""
    return (
        "Use only the provided resume, job-description, and evidence snippets."
        " Do not invent experience, skills, metrics, companies, education, or certifications."
        " Do not make hiring decisions or rank candidates as hire/reject."
        " Do not infer protected attributes."
        " Keep the tone professional and truthful."
        " If evidence is insufficient, say what information is missing."
        " Output must require human review."
        f"{task_note}"
    )


def _clean_list(values: list[str] | None) -> list[str]:
    return [str(value).strip() for value in (values or []) if str(value or "").strip()]


def _redact_list(values: list[str], candidate_name: str | None = None) -> list[str]:
    return [redact_for_external_genai(value, candidate_name=candidate_name) for value in values]


def build_context_block(
    resume_evidence: list[str] | None = None,
    job_description_evidence: list[str] | None = None,
    user_goal: str | None = None,
    privacy_mode: bool = True,
    candidate_name: str | None = None,
) -> dict:
    resume_items = _clean_list(resume_evidence)
    jd_items = _clean_list(job_description_evidence)
    redaction_applied = bool(privacy_mode)
    if privacy_mode:
        resume_items = _redact_list(resume_items, candidate_name=candidate_name)
        jd_items = _redact_list(jd_items, candidate_name=candidate_name)
    return {
        "resume_evidence": resume_items,
        "job_description_evidence": jd_items,
        "user_goal": str(user_goal or "").strip(),
        "privacy_mode": bool(privacy_mode),
        "redaction_applied": redaction_applied,
    }


def _base_prompt_object(
    task_type: str,
    consent_given: bool,
    external_enabled: bool,
    user_prompt: str,
    safety_notes: list[str] | None = None,
) -> dict:
    consent_check = check_genai_consent(consent_given=consent_given, external_enabled=external_enabled)
    allowed = bool(consent_check.get("allowed"))
    return {
        "allowed_for_external_use": allowed,
        "blocked_reason": None if allowed else consent_check.get("reason"),
        "local_preview_only": not allowed,
        "task_type": task_type,
        "system_instructions": build_system_safety_instructions(task_type),
        "user_prompt": user_prompt,
        "safety_notes": safety_notes or get_prompt_builder_safety_notes(),
        "requires_human_review": True,
    }


def _format_evidence_section(title: str, evidence: list[str] | None) -> str:
    items = _clean_list(evidence)
    if not items:
        return f"{title}:\n- Not provided."
    return f"{title}:\n" + "\n".join(f"- {item}" for item in items)


def build_resume_bullet_rewrite_prompt(
    original_bullet: str,
    target_role: str | None = None,
    evidence: list[str] | None = None,
    consent_given: bool = False,
    external_enabled: bool = False,
    privacy_mode: bool = True,
    candidate_name: str | None = None,
) -> dict:
    context = build_context_block(
        resume_evidence=evidence,
        user_goal=target_role,
        privacy_mode=privacy_mode,
        candidate_name=candidate_name,
    )
    user_prompt = (
        "Prepare a rewritten resume bullet preview.\n"
        "Preserve truthfulness and keep the original meaning.\n"
        "Do not add metrics unless they are provided in the evidence.\n"
        "Improve clarity using an action-context-result structure.\n"
        f"Target role: {target_role or 'Not provided'}\n"
        f"Original bullet: {redact_for_external_genai(original_bullet, candidate_name=candidate_name)}\n"
        f"{_format_evidence_section('Resume evidence', context['resume_evidence'])}"
    )
    return _base_prompt_object(
        "resume_bullet_rewrite",
        consent_given,
        external_enabled,
        user_prompt,
    )


def build_cover_letter_prompt(
    resume_evidence,
    job_description_evidence,
    company_name=None,
    role_title=None,
    consent_given=False,
    external_enabled=False,
    privacy_mode=True,
    candidate_name=None,
) -> dict:
    context = build_context_block(resume_evidence, job_description_evidence, privacy_mode=privacy_mode, candidate_name=candidate_name)
    user_prompt = (
        "Draft a tailored cover letter preview using only provided evidence.\n"
        "Do not invent company research or claim experience not present in the evidence.\n"
        "Use a Canadian professional tone.\n"
        f"Company: {company_name or 'Not provided'}\n"
        f"Role title: {role_title or 'Not provided'}\n"
        f"{_format_evidence_section('Resume evidence', context['resume_evidence'])}\n"
        f"{_format_evidence_section('Job-description evidence', context['job_description_evidence'])}"
    )
    return _base_prompt_object("cover_letter", consent_given, external_enabled, user_prompt)


def build_recruiter_email_prompt(
    resume_evidence,
    job_description_evidence=None,
    recruiter_name=None,
    role_title=None,
    consent_given=False,
    external_enabled=False,
    privacy_mode=True,
    candidate_name=None,
) -> dict:
    context = build_context_block(resume_evidence, job_description_evidence, privacy_mode=privacy_mode, candidate_name=candidate_name)
    user_prompt = (
        "Draft a concise, professional recruiter outreach email preview.\n"
        "Use evidence only, with no exaggeration and no fabricated achievements or fake claims.\n"
        f"Recruiter name: {recruiter_name or 'Not provided'}\n"
        f"Role title: {role_title or 'Not provided'}\n"
        f"{_format_evidence_section('Resume evidence', context['resume_evidence'])}\n"
        f"{_format_evidence_section('Job-description evidence', context['job_description_evidence'])}"
    )
    return _base_prompt_object("recruiter_email", consent_given, external_enabled, user_prompt)


def build_linkedin_message_prompt(
    resume_evidence,
    job_description_evidence=None,
    recipient_name=None,
    role_title=None,
    consent_given=False,
    external_enabled=False,
    privacy_mode=True,
    candidate_name=None,
) -> dict:
    context = build_context_block(resume_evidence, job_description_evidence, privacy_mode=privacy_mode, candidate_name=candidate_name)
    user_prompt = (
        "Draft a short, conversational, professional LinkedIn message preview.\n"
        "Avoid a desperate tone and do not make fake claims.\n"
        f"Recipient name: {recipient_name or 'Not provided'}\n"
        f"Role title: {role_title or 'Not provided'}\n"
        f"{_format_evidence_section('Resume evidence', context['resume_evidence'])}\n"
        f"{_format_evidence_section('Job-description evidence', context['job_description_evidence'])}"
    )
    return _base_prompt_object("linkedin_message", consent_given, external_enabled, user_prompt)


def build_interview_questions_prompt(
    resume_evidence,
    job_description_evidence=None,
    target_role=None,
    consent_given=False,
    external_enabled=False,
    privacy_mode=True,
    candidate_name=None,
) -> dict:
    context = build_context_block(resume_evidence, job_description_evidence, privacy_mode=privacy_mode, candidate_name=candidate_name)
    user_prompt = (
        "Prepare interview practice questions based on the provided resume and job-description evidence.\n"
        "Include technical and behavioral categories in the planned output.\n"
        f"Target role: {target_role or 'Not provided'}\n"
        f"{_format_evidence_section('Resume evidence', context['resume_evidence'])}\n"
        f"{_format_evidence_section('Job-description evidence', context['job_description_evidence'])}"
    )
    return _base_prompt_object("interview_questions", consent_given, external_enabled, user_prompt)


def build_rag_answer_generation_prompt(
    query: str,
    retrieved_evidence: list[dict],
    consent_given=False,
    external_enabled=False,
    privacy_mode=True,
    candidate_name=None,
) -> dict:
    evidence_lines = []
    for item in retrieved_evidence or []:
        if not isinstance(item, dict):
            continue
        source = item.get("source", "unknown")
        chunk_id = item.get("chunk_id", "unknown_chunk")
        text = str(item.get("text", "")).strip()
        if privacy_mode and source == "resume":
            text = redact_for_external_genai(text, candidate_name=candidate_name)
        if text:
            evidence_lines.append(f"[{source} | {chunk_id}] {text}")
    user_prompt = (
        f"Recruiter question: {query}\n"
        "Answer only from the evidence below. Cite evidence labels and chunk IDs.\n"
        "Say when evidence is insufficient. Do not make a hiring decision.\n"
        f"{_format_evidence_section('Retrieved evidence', evidence_lines)}"
    )
    return _base_prompt_object("rag_answer_generation", consent_given, external_enabled, user_prompt)


def build_candidate_summary_prompt(
    resume_evidence,
    job_description_evidence=None,
    consent_given=False,
    external_enabled=False,
    privacy_mode=True,
    candidate_name=None,
) -> dict:
    context = build_context_block(resume_evidence, job_description_evidence, privacy_mode=privacy_mode, candidate_name=candidate_name)
    user_prompt = (
        "Prepare a recruiter-review candidate summary using only provided evidence.\n"
        "Use cautious wording and avoid hiring decision language.\n"
        f"{_format_evidence_section('Resume evidence', context['resume_evidence'])}\n"
        f"{_format_evidence_section('Job-description evidence', context['job_description_evidence'])}"
    )
    return _base_prompt_object("candidate_summary", consent_given, external_enabled, user_prompt)


def build_resume_gap_explanation_prompt(
    resume_evidence,
    job_description_evidence,
    consent_given=False,
    external_enabled=False,
    privacy_mode=True,
    candidate_name=None,
) -> dict:
    context = build_context_block(resume_evidence, job_description_evidence, privacy_mode=privacy_mode, candidate_name=candidate_name)
    user_prompt = (
        "Explain possible resume/job-description gaps using only provided evidence.\n"
        "If a requirement is not evidenced, say it may need manual verification.\n"
        f"{_format_evidence_section('Resume evidence', context['resume_evidence'])}\n"
        f"{_format_evidence_section('Job-description evidence', context['job_description_evidence'])}"
    )
    return _base_prompt_object("resume_gap_explanation", consent_given, external_enabled, user_prompt)


def build_prompt_preview(task_type: str, **kwargs) -> dict:
    builders = {
        "resume_bullet_rewrite": build_resume_bullet_rewrite_prompt,
        "cover_letter": build_cover_letter_prompt,
        "recruiter_email": build_recruiter_email_prompt,
        "linkedin_message": build_linkedin_message_prompt,
        "interview_questions": build_interview_questions_prompt,
        "rag_answer_generation": build_rag_answer_generation_prompt,
        "candidate_summary": build_candidate_summary_prompt,
        "resume_gap_explanation": build_resume_gap_explanation_prompt,
    }
    builder = builders.get(task_type)
    if builder is None:
        return {
            "allowed_for_external_use": False,
            "blocked_reason": f"Unsupported prompt task type: {task_type}",
            "local_preview_only": True,
            "task_type": task_type,
            "system_instructions": build_system_safety_instructions(task_type),
            "user_prompt": "",
            "safety_notes": get_prompt_builder_safety_notes(),
            "requires_human_review": True,
        }
    return builder(**kwargs)


def get_prompt_builder_safety_notes() -> list[str]:
    return [
        "Prompt builder does not call external AI.",
        "External generation is disabled by default.",
        "Explicit consent is required before external use.",
        "PII should be redacted before external use.",
        "Generated content must be reviewed by a human.",
    ]
