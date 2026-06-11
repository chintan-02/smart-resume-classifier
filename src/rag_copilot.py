import re

from src.privacy_tools import mask_pii


COPILOT_DISCLAIMER = (
    "This copilot retrieves evidence from the uploaded resume/JD. It does not make hiring decisions."
)
CONTACT_QUERY_TERMS = ("contact", "email", "phone", "linkedin", "github", "profile")


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _is_contact_query(query: str) -> bool:
    clean_query = normalize_text(query).lower()
    return any(term in clean_query for term in CONTACT_QUERY_TERMS)


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 80, source: str = "resume") -> list[dict]:
    clean_text = normalize_text(text)
    if not clean_text:
        return []

    chunk_size = max(int(chunk_size or 500), 100)
    overlap = max(min(int(overlap or 0), chunk_size - 1), 0)
    step = chunk_size - overlap
    chunks = []
    start = 0

    while start < len(clean_text):
        end = min(start + chunk_size, len(clean_text))
        chunk = clean_text[start:end].strip()
        if chunk:
            chunk_number = len(chunks) + 1
            chunks.append(
                {
                    "chunk_id": f"{source}_{chunk_number}",
                    "source": source,
                    "text": chunk,
                    "char_start": start,
                    "char_end": end,
                }
            )
        if end >= len(clean_text):
            break
        start += step

    return chunks


def build_copilot_corpus(
    resume_text: str,
    job_description: str | None = None,
    privacy_mode: bool = False,
    candidate_name: str | None = None,
) -> list[dict]:
    corpus = chunk_text(resume_text, source="resume")
    for chunk in corpus:
        chunk["display_text"] = (
            mask_pii(chunk.get("text", ""), candidate_name=candidate_name)
            if privacy_mode
            else chunk.get("text", "")
        )

    if normalize_text(job_description):
        jd_chunks = chunk_text(job_description or "", source="job_description")
        for chunk in jd_chunks:
            chunk["display_text"] = chunk.get("text", "")
        corpus.extend(jd_chunks)

    return corpus


def retrieve_relevant_chunks(query: str, corpus: list[dict], top_k: int = 5) -> list[dict]:
    clean_query = normalize_text(query)
    valid_chunks = [
        chunk
        for chunk in (corpus or [])
        if isinstance(chunk, dict) and normalize_text(chunk.get("text", ""))
    ]
    if not clean_query or not valid_chunks:
        return []

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        documents = [chunk["text"] for chunk in valid_chunks]
        vectorizer = TfidfVectorizer(stop_words="english")
        matrix = vectorizer.fit_transform([clean_query] + documents)
        similarities = cosine_similarity(matrix[0:1], matrix[1:]).flatten()
    except Exception:
        return []

    result_limit = max(int(top_k or 5), 1)
    priority_indexes = []
    if _is_contact_query(clean_query):
        priority_indexes = [
            index
            for index, chunk in enumerate(valid_chunks)
            if chunk.get("source") == "resume" and str(chunk.get("chunk_id", "")).startswith(("resume_1", "resume_2"))
        ][:2]

    ranked_indexes = list(priority_indexes)
    ranked_indexes.extend(
        index
        for index in similarities.argsort()[::-1]
        if index not in priority_indexes
    )
    ranked_indexes = ranked_indexes[:result_limit]

    results = []
    for rank, index in enumerate(ranked_indexes, start=1):
        score = float(similarities[index])
        if score <= 0 and index not in priority_indexes:
            continue
        chunk = valid_chunks[index]
        results.append(
            {
                "rank": rank,
                "source": chunk.get("source", "resume"),
                "chunk_id": chunk.get("chunk_id", f"chunk_{rank}"),
                "score": round(score, 4),
                "text": chunk.get("display_text", chunk.get("text", "")),
            }
        )

    return results


def classify_recruiter_question(query: str) -> str:
    clean_query = normalize_text(query).lower()
    if not clean_query:
        return "unknown"

    if any(term in clean_query for term in ("match", "job description", "jd", "requirement", "requirements")):
        return "job_match"
    if any(term in clean_query for term in ("skill", "skills", "tools", "technologies", "tech stack")):
        return "skills"
    if any(term in clean_query for term in ("project", "projects", "portfolio")):
        return "projects"
    if any(term in clean_query for term in ("experience", "work history", "background", "employment")):
        return "experience"
    if any(term in clean_query for term in ("education", "degree", "university", "college", "certification")):
        return "education"
    if any(term in clean_query for term in ("gap", "missing", "risk", "risks", "weakness", "verify", "concern")):
        return "risks"
    if any(term in clean_query for term in ("summarize", "summary", "overview", "review")):
        return "summary"
    return "unknown"


def _format_source_label(source: str) -> str:
    return "job description" if source == "job_description" else "resume"


def build_retrieval_answer(query: str, retrieved_chunks: list[dict], question_type: str | None = None) -> dict:
    question_type = question_type or classify_recruiter_question(query)
    evidence = [
        chunk
        for chunk in (retrieved_chunks or [])
        if isinstance(chunk, dict) and normalize_text(chunk.get("text", ""))
    ]
    limitations = [
        "This is retrieval-only evidence search, not LLM reasoning.",
        "The answer is limited to the uploaded resume and job description text.",
        "This should be reviewed by a human before making any workflow decision.",
    ]

    if not evidence:
        return {
            "answer": "I could not find strong evidence in the uploaded resume/JD for this question.",
            "question_type": question_type,
            "evidence": [],
            "limitations": limitations,
            "disclaimer": COPILOT_DISCLAIMER,
        }

    source_labels = sorted({_format_source_label(chunk.get("source", "")) for chunk in evidence})
    answer_prefixes = {
        "skills": "The available resume evidence suggests these skill-related snippets are relevant.",
        "experience": "The available resume evidence suggests these experience-related snippets are relevant.",
        "projects": "The available resume evidence suggests these project-related snippets are relevant.",
        "education": "The available resume evidence suggests these education-related snippets are relevant.",
        "job_match": "Based on the provided resume and job description evidence, these snippets may help compare fit.",
        "risks": "The retrieved evidence can help a recruiter review possible gaps or verification points.",
        "summary": "The available resume evidence can support a recruiter summary, but it should be reviewed by a human.",
        "unknown": "The retrieved snippets below are the closest local evidence for the question.",
    }
    answer = (
        f"{answer_prefixes.get(question_type, answer_prefixes['unknown'])} "
        f"Evidence came from: {', '.join(source_labels)}. "
        "Review the snippets directly rather than treating this as a final conclusion."
    )

    return {
        "answer": answer,
        "question_type": question_type,
        "evidence": evidence,
        "limitations": limitations,
        "disclaimer": COPILOT_DISCLAIMER,
    }


def ask_recruiter_copilot(
    query: str,
    resume_text: str,
    job_description: str | None = None,
    privacy_mode: bool = False,
    candidate_name: str | None = None,
    top_k: int = 5,
) -> dict:
    corpus = build_copilot_corpus(
        resume_text=resume_text,
        job_description=job_description,
        privacy_mode=privacy_mode,
        candidate_name=candidate_name,
    )
    retrieved_chunks = retrieve_relevant_chunks(query, corpus, top_k=top_k)
    question_type = classify_recruiter_question(query)
    return build_retrieval_answer(query, retrieved_chunks, question_type=question_type)


def get_sample_copilot_questions() -> list[str]:
    return [
        "Summarize this candidate for recruiter review.",
        "Which skills in the resume match the job description?",
        "What important job requirements appear missing?",
        "Which projects or experience are most relevant?",
        "What should a recruiter verify manually?",
        "What evidence supports the predicted role?",
    ]


def get_copilot_safety_notes() -> list[str]:
    return [
        "The copilot uses local retrieval from the current resume and job description only.",
        "It does not use external AI in this foundation step.",
        "It does not make hiring decisions.",
        "It may miss information if the resume is poorly formatted.",
        "Privacy-safe mode masks common identifiers in resume evidence.",
    ]
