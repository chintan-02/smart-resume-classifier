from src.genai_prompt_builder import (
    build_context_block,
    build_cover_letter_prompt,
    build_prompt_preview,
    build_rag_answer_generation_prompt,
    build_recruiter_email_prompt,
    build_resume_bullet_rewrite_prompt,
    build_system_safety_instructions,
    get_prompt_builder_safety_notes,
    get_prompt_task_types,
)


def test_get_prompt_task_types_returns_expected_task_keys():
    task_keys = {task["task_key"] for task in get_prompt_task_types()}

    assert {
        "resume_bullet_rewrite",
        "cover_letter",
        "recruiter_email",
        "linkedin_message",
        "interview_questions",
        "rag_answer_generation",
        "candidate_summary",
        "resume_gap_explanation",
    }.issubset(task_keys)


def test_system_safety_instructions_include_do_not_invent_and_human_review():
    instructions = build_system_safety_instructions("cover_letter").lower()

    assert "do not invent" in instructions
    assert "human review" in instructions
    assert "do not make hiring decisions" in instructions


def test_resume_bullet_prompt_returns_local_preview_when_external_disabled():
    prompt = build_resume_bullet_rewrite_prompt(
        original_bullet="Built a resume classifier with Python.",
        target_role="AI Engineer",
        evidence=["Python project experience"],
        consent_given=True,
        external_enabled=False,
    )

    assert prompt["allowed_for_external_use"] is False
    assert prompt["local_preview_only"] is True
    assert "local-only mode" in prompt["blocked_reason"]
    assert "do not add metrics unless they are provided" in prompt["user_prompt"].lower()


def test_consent_check_blocks_external_use_when_consent_false():
    prompt = build_resume_bullet_rewrite_prompt(
        original_bullet="Built a dashboard.",
        consent_given=False,
        external_enabled=True,
    )

    assert prompt["allowed_for_external_use"] is False
    assert "Explicit consent is required" in prompt["blocked_reason"]


def test_context_block_redacts_email_phone_and_name_when_privacy_mode_true():
    context = build_context_block(
        resume_evidence=["Jane Doe jane@example.com 555-123-4567 built Python projects."],
        candidate_name="Jane Doe",
        privacy_mode=True,
    )
    evidence_text = " ".join(context["resume_evidence"])

    assert "Jane Doe" not in evidence_text
    assert "jane@example.com" not in evidence_text
    assert "555-123-4567" not in evidence_text
    assert "[candidate_name]" in evidence_text
    assert "[email]" in evidence_text
    assert "[phone]" in evidence_text
    assert context["redaction_applied"] is True


def test_cover_letter_prompt_says_use_only_provided_evidence():
    prompt = build_cover_letter_prompt(
        resume_evidence=["Python and FastAPI project experience."],
        job_description_evidence=["Role needs Python and API development."],
        company_name="ExampleCo",
        role_title="Software Developer",
    )

    assert "using only provided evidence" in prompt["user_prompt"].lower()
    assert "do not invent company research" in prompt["user_prompt"].lower()


def test_recruiter_email_prompt_does_not_include_fake_claims():
    prompt = build_recruiter_email_prompt(
        resume_evidence=["SQL and analytics project experience."],
        role_title="Data Analyst",
    )

    assert "no fabricated achievements" in prompt["user_prompt"].lower()
    assert "fake claims" in prompt["user_prompt"].lower()


def test_rag_answer_prompt_includes_chunk_ids_and_no_hiring_decision_language():
    prompt = build_rag_answer_generation_prompt(
        query="Which skills match?",
        retrieved_evidence=[
            {"source": "resume", "chunk_id": "resume_1", "text": "Python SQL"},
            {"source": "job_description", "chunk_id": "job_description_1", "text": "Need Python"},
        ],
    )

    assert "resume_1" in prompt["user_prompt"]
    assert "job_description_1" in prompt["user_prompt"]
    assert "Do not make a hiring decision" in prompt["user_prompt"]


def test_dispatcher_handles_unknown_task_safely():
    prompt = build_prompt_preview("unknown_task")

    assert prompt["allowed_for_external_use"] is False
    assert prompt["local_preview_only"] is True
    assert "Unsupported prompt task type" in prompt["blocked_reason"]


def test_safety_notes_mention_no_external_ai_call():
    notes = " ".join(get_prompt_builder_safety_notes()).lower()

    assert "does not call external ai" in notes
    assert "explicit consent" in notes
