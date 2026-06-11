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


def test_job_match_query_returns_resume_and_job_description_evidence_when_available():
    result = ask_recruiter_copilot(
        query="Which skills match the job description?",
        resume_text=(
            "Candidate has Python, SQL, machine learning, FastAPI, Docker, Streamlit, "
            "pandas, scikit-learn, and data analysis project experience."
        ),
        job_description=(
            "We are hiring for Python, SQL, machine learning, Docker, FastAPI, "
            "and deployment skills."
        ),
        top_k=5,
    )
    sources = {item["source"] for item in result["evidence"]}

    assert result["question_type"] == "job_match"
    assert "resume" in sources
    assert "job_description" in sources
    assert len(result["evidence"]) <= 5


def test_job_match_balanced_evidence_keeps_privacy_masking_for_resume_only():
    result = ask_recruiter_copilot(
        query="Which skills match the job description?",
        resume_text=(
            "Jane Doe Data Scientist jane@example.com has Python, SQL, machine learning, "
            "FastAPI, Docker, and Streamlit project experience."
        ),
        job_description="Contact hiring@example.com. We need Python, SQL, Docker, and FastAPI.",
        privacy_mode=True,
        candidate_name="Jane Doe",
        top_k=5,
    )
    resume_evidence = " ".join(item["text"] for item in result["evidence"] if item["source"] == "resume")
    jd_evidence = " ".join(item["text"] for item in result["evidence"] if item["source"] == "job_description")

    assert "Jane Doe" not in resume_evidence
    assert "jane@example.com" not in resume_evidence
    assert "[candidate_name]" in resume_evidence
    assert "[email]" in resume_evidence
    assert "hiring@example.com" in jd_evidence


def test_retrieve_relevant_chunks_prioritizes_first_resume_chunks_for_contact_query():
    corpus = [
        {
            "chunk_id": "resume_1",
            "source": "resume",
            "text": "Candidate header with contact details.",
            "display_text": "Candidate header with contact details.",
        },
        {
            "chunk_id": "resume_2",
            "source": "resume",
            "text": "Additional profile links and contact context.",
            "display_text": "Additional profile links and contact context.",
        },
        {
            "chunk_id": "resume_3",
            "source": "resume",
            "text": "Deep project section with repeated Python Python Python.",
            "display_text": "Deep project section with repeated Python Python Python.",
        },
    ]

    results = retrieve_relevant_chunks("email phone linkedin github profile Python", corpus, top_k=3)

    assert [result["chunk_id"] for result in results[:2]] == ["resume_1", "resume_2"]


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


def test_privacy_mode_masks_email_in_resume_evidence():
    corpus = build_copilot_corpus(
        resume_text="Jane Doe Data Scientist jane@example.com Python SQL",
        job_description="Job requires Python.",
        privacy_mode=True,
        candidate_name="Jane Doe",
    )
    resume_text = " ".join(chunk["display_text"] for chunk in corpus if chunk["source"] == "resume")

    assert "jane@example.com" not in resume_text
    assert "[email]" in resume_text


def test_privacy_mode_masks_phone_in_resume_evidence():
    corpus = build_copilot_corpus(
        resume_text="Jane Doe Data Scientist 555-123-4567 Python SQL",
        job_description="Job requires Python.",
        privacy_mode=True,
        candidate_name="Jane Doe",
    )
    resume_text = " ".join(chunk["display_text"] for chunk in corpus if chunk["source"] == "resume")

    assert "555-123-4567" not in resume_text
    assert "[phone]" in resume_text


def test_privacy_mode_masks_linkedin_and_github_in_resume_evidence():
    corpus = build_copilot_corpus(
        resume_text=(
            "Jane Doe Data Scientist https://www.linkedin.com/in/jane-doe "
            "https://github.com/janedoe Python SQL"
        ),
        job_description="Job requires Python.",
        privacy_mode=True,
        candidate_name="Jane Doe",
    )
    resume_text = " ".join(chunk["display_text"] for chunk in corpus if chunk["source"] == "resume")

    assert "linkedin.com/in/jane-doe" not in resume_text
    assert "github.com/janedoe" not in resume_text
    assert "[linkedin]" in resume_text
    assert "[github]" in resume_text


def test_privacy_mode_masks_candidate_name_when_provided():
    corpus = build_copilot_corpus(
        resume_text="Jane Doe Data Scientist with Python and SQL experience.",
        job_description="Job requires Python.",
        privacy_mode=True,
        candidate_name="Jane Doe",
    )
    resume_text = " ".join(chunk["display_text"] for chunk in corpus if chunk["source"] == "resume")

    assert "Jane Doe" not in resume_text
    assert "[candidate_name]" in resume_text


def test_privacy_mode_does_not_mask_job_description_chunks():
    corpus = build_copilot_corpus(
        resume_text="Jane Doe Data Scientist jane@example.com Python SQL",
        job_description="Contact hiring@example.com for a Python role in Calgary, AB.",
        privacy_mode=True,
        candidate_name="Jane Doe",
    )
    jd_text = " ".join(chunk["display_text"] for chunk in corpus if chunk["source"] == "job_description")

    assert "hiring@example.com" in jd_text
    assert "Calgary, AB" in jd_text
    assert "[email]" not in jd_text


def test_ask_recruiter_copilot_returns_masked_resume_evidence_when_privacy_mode_enabled():
    result = ask_recruiter_copilot(
        query="Data Scientist Python SQL recruiter evidence.",
        resume_text=(
            "Jane Doe Data Scientist jane@example.com 555-123-4567 "
            "https://linkedin.com/in/jane-doe https://github.com/janedoe Python SQL"
        ),
        job_description="Need Python and SQL.",
        privacy_mode=True,
        candidate_name="Jane Doe",
        top_k=3,
    )
    evidence_text = " ".join(item["text"] for item in result["evidence"] if item["source"] == "resume")

    assert "Jane Doe" not in evidence_text
    assert "jane@example.com" not in evidence_text
    assert "555-123-4567" not in evidence_text
    assert "linkedin.com/in/jane-doe" not in evidence_text
    assert "github.com/janedoe" not in evidence_text
    assert "[candidate_name]" in evidence_text
    assert "[email]" in evidence_text


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
