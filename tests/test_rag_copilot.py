from src.rag_copilot import (
    ask_recruiter_copilot,
    build_copilot_corpus,
    build_retrieval_answer,
    chunk_text,
    classify_recruiter_question,
    retrieve_relevant_chunks,
)


def test_chunk_text_returns_chunks_with_source_and_text_metadata():
    chunks = chunk_text("Python developer with SQL and machine learning experience.", chunk_size=20, overlap=5)

    assert chunks
    assert chunks[0]["source"] == "resume"
    assert chunks[0]["chunk_id"] == "resume_1"
    assert chunks[0]["text"]
    assert "char_start" in chunks[0]
    assert "char_end" in chunks[0]


def test_build_copilot_corpus_includes_resume_and_jd_chunks():
    corpus = build_copilot_corpus(
        resume_text="Resume has Python and FastAPI experience.",
        job_description="Job requires Python and API deployment.",
    )
    sources = {chunk["source"] for chunk in corpus}

    assert "resume" in sources
    assert "job_description" in sources


def test_retrieve_relevant_chunks_returns_skill_chunk_for_query():
    corpus = build_copilot_corpus(
        resume_text=(
            "Built dashboards with Tableau. "
            "Developed machine learning pipelines using Python, pandas, scikit-learn, and SQL."
        ),
        job_description="Need Python, SQL, and machine learning experience.",
    )

    results = retrieve_relevant_chunks("Python SQL machine learning skills", corpus, top_k=2)

    assert results
    assert results[0]["score"] > 0
    assert "Python" in results[0]["text"] or "SQL" in results[0]["text"]


def test_classify_recruiter_question_categories():
    assert classify_recruiter_question("What skills does this candidate have?") == "skills"
    assert classify_recruiter_question("What skills match this JD?") == "job_match"
    assert classify_recruiter_question("Which projects are relevant?") == "projects"
    assert classify_recruiter_question("What are the main gaps?") == "risks"
    assert classify_recruiter_question("Summarize this candidate") == "summary"


def test_build_retrieval_answer_does_not_invent_when_evidence_empty():
    result = build_retrieval_answer("Does the resume mention Kubernetes?", [], question_type="skills")

    assert "could not find strong evidence" in result["answer"]
    assert result["evidence"] == []
    assert "does not make hiring decisions" in result["disclaimer"]


def test_privacy_mode_masks_email_phone_and_name_in_resume_evidence():
    corpus = build_copilot_corpus(
        resume_text="Jane Doe Data Scientist jane@example.com 555-123-4567 Python SQL",
        job_description="Job requires Python.",
        privacy_mode=True,
        candidate_name="Jane Doe",
    )
    resume_text = " ".join(chunk["text"] for chunk in corpus if chunk["source"] == "resume")

    assert "jane@example.com" not in resume_text
    assert "555-123-4567" not in resume_text
    assert "Jane Doe" not in resume_text
    assert "[email]" in resume_text
    assert "[phone]" in resume_text


def test_ask_recruiter_copilot_returns_answer_evidence_limitations_and_disclaimer():
    result = ask_recruiter_copilot(
        query="Which skills match the job description?",
        resume_text="Python developer with SQL, FastAPI, and machine learning projects.",
        job_description="Looking for Python, SQL, and API experience.",
    )

    assert result["answer"]
    assert result["question_type"] == "job_match"
    assert isinstance(result["evidence"], list)
    assert result["limitations"]
    assert "does not make hiring decisions" in result["disclaimer"]
