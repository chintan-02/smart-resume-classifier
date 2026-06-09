import re
from functools import lru_cache

import numpy as np


SEMANTIC_DISCLAIMER = (
    "Semantic matching is a meaning-based estimate using local sentence embeddings. "
    "It is not an official ATS score, hiring decision, or guarantee of job success."
)
SEMANTIC_OPTIONAL_DISCLAIMER = "Semantic matching is optional and depends on local embedding model dependencies."
SEMANTIC_MODEL_UNAVAILABLE_MESSAGE = (
    "Semantic matching is unavailable because the local embedding model could not be loaded. "
    "Keyword-based JD matching is still available."
)


def _unavailable_result(message: str) -> dict:
    return {
        "available": False,
        "semantic_score": None,
        "similarity_label": "Unavailable",
        "message": message,
        "resume_chunk_count": 0,
        "jd_chunk_count": 0,
        "top_matching_pairs": [],
        "weak_jd_chunks": [],
        "disclaimer": SEMANTIC_OPTIONAL_DISCLAIMER,
    }


def clean_text_for_semantic_matching(text: str) -> str:
    cleaned = str(text or "").strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def mask_pii_for_display(text: str) -> str:
    display_text = str(text or "")
    display_text = re.sub(r"\b[\w.+-]+@[\w.-]+\.\w+\b", "[email]", display_text)
    display_text = re.sub(r"https?://(?:www\.)?linkedin\.com/[^\s,)>\]]+|www\.linkedin\.com/[^\s,)>\]]+", "[linkedin]", display_text, flags=re.IGNORECASE)
    display_text = re.sub(r"https?://(?:www\.)?github\.com/[^\s,)>\]]+|www\.github\.com/[^\s,)>\]]+", "[github]", display_text, flags=re.IGNORECASE)
    display_text = re.sub(
        r"(?:(?:\+?1[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4})",
        "[phone]",
        display_text,
    )
    return clean_text_for_semantic_matching(display_text)


def truncate_text(text: str, max_chars: int = 500) -> str:
    cleaned = clean_text_for_semantic_matching(text)
    max_chars = max(4, int(max_chars or 500))
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[: max_chars - 3].rstrip() + "..."


def _split_long_text_by_words(text: str, max_words: int) -> list[str]:
    words = text.split()
    chunks = []
    for start in range(0, len(words), max_words):
        chunk = " ".join(words[start : start + max_words]).strip()
        if len(chunk.split()) >= 5:
            chunks.append(chunk)
    return chunks


def split_text_into_chunks(text: str, max_words: int = 120) -> list[str]:
    cleaned = clean_text_for_semantic_matching(text)
    if not cleaned:
        return []

    max_words = max(20, int(max_words or 120))
    paragraphs = [
        paragraph.strip()
        for paragraph in re.split(r"(?:\n\s*){2,}", str(text or ""))
        if paragraph and paragraph.strip()
    ]
    if not paragraphs:
        paragraphs = [cleaned]

    chunks = []
    for paragraph in paragraphs:
        paragraph = clean_text_for_semantic_matching(paragraph)
        word_count = len(paragraph.split())
        if word_count < 5:
            continue
        if word_count <= max_words:
            chunks.append(paragraph)
            continue

        sentences = [
            clean_text_for_semantic_matching(sentence)
            for sentence in re.split(r"(?<=[.!?])\s+", paragraph)
            if len(sentence.split()) >= 5
        ]
        current = []
        current_count = 0
        for sentence in sentences:
            sentence_count = len(sentence.split())
            if sentence_count > max_words:
                if current:
                    chunks.append(" ".join(current))
                    current = []
                    current_count = 0
                chunks.extend(_split_long_text_by_words(sentence, max_words))
                continue

            if current_count + sentence_count > max_words and current:
                chunks.append(" ".join(current))
                current = [sentence]
                current_count = sentence_count
            else:
                current.append(sentence)
                current_count += sentence_count

        if current:
            chunks.append(" ".join(current))
        elif not sentences:
            chunks.extend(_split_long_text_by_words(paragraph, max_words))

    return chunks


@lru_cache(maxsize=1)
def load_embedding_model():
    try:
        from sentence_transformers import SentenceTransformer
    except (ImportError, ModuleNotFoundError, RuntimeError, Exception):
        return None

    try:
        return SentenceTransformer("all-MiniLM-L6-v2")
    except (ImportError, ModuleNotFoundError, RuntimeError, Exception):
        return None


def cosine_similarity_score(vector_a, vector_b) -> float:
    try:
        a = np.asarray(vector_a, dtype=float)
        b = np.asarray(vector_b, dtype=float)
        denominator = np.linalg.norm(a) * np.linalg.norm(b)
        if denominator == 0:
            return 0.0
        score = float(np.dot(a, b) / denominator)
        return max(0.0, min(1.0, score))
    except Exception:
        return 0.0


def _similarity_label(score: float) -> str:
    if score >= 75:
        return "Strong"
    if score >= 60:
        return "Good"
    if score >= 40:
        return "Partial"
    return "Weak"


def calculate_semantic_similarity(resume_text: str, jd_text: str) -> dict:
    model = load_embedding_model()
    if model is None:
        return _unavailable_result(SEMANTIC_MODEL_UNAVAILABLE_MESSAGE)

    resume_chunks = split_text_into_chunks(resume_text)
    jd_chunks = split_text_into_chunks(jd_text)
    if not resume_chunks or not jd_chunks:
        return _unavailable_result("Add both a readable resume and job description to calculate semantic matching.")

    try:
        resume_embeddings = model.encode(resume_chunks)
        jd_embeddings = model.encode(jd_chunks)
    except (ImportError, ModuleNotFoundError, RuntimeError, Exception):
        return _unavailable_result(SEMANTIC_MODEL_UNAVAILABLE_MESSAGE)

    best_matches = []
    for jd_index, jd_embedding in enumerate(jd_embeddings):
        similarities = [
            cosine_similarity_score(jd_embedding, resume_embedding)
            for resume_embedding in resume_embeddings
        ]
        best_resume_index = int(np.argmax(similarities))
        best_similarity = float(similarities[best_resume_index])
        best_matches.append(
            {
                "resume_chunk": resume_chunks[best_resume_index],
                "jd_chunk": jd_chunks[jd_index],
                "similarity": best_similarity,
            }
        )

    average_best_similarity = sum(item["similarity"] for item in best_matches) / max(1, len(best_matches))
    semantic_score = round(average_best_similarity * 100, 2)
    top_matching_pairs = sorted(best_matches, key=lambda item: item["similarity"], reverse=True)[:3]
    weak_jd_chunks = [
        {
            "jd_chunk": truncate_text(item["jd_chunk"]),
            "best_similarity": round(item["similarity"], 2),
            "recommendation": "Consider adding truthful resume evidence for this requirement if relevant.",
        }
        for item in best_matches
        if item["similarity"] < 0.45
    ][:5]

    return {
        "available": True,
        "semantic_score": semantic_score,
        "similarity_label": _similarity_label(semantic_score),
        "message": "Semantic alignment compares the meaning of resume content against the job description.",
        "resume_chunk_count": len(resume_chunks),
        "jd_chunk_count": len(jd_chunks),
        "top_matching_pairs": [
            {
                "resume_chunk": truncate_text(mask_pii_for_display(item["resume_chunk"])),
                "jd_chunk": truncate_text(mask_pii_for_display(item["jd_chunk"])),
                "similarity": round(item["similarity"], 2),
            }
            for item in top_matching_pairs
        ],
        "weak_jd_chunks": weak_jd_chunks,
        "disclaimer": SEMANTIC_DISCLAIMER,
    }


def get_semantic_summary_cards(result: dict) -> list[dict]:
    result = result if isinstance(result, dict) else {}
    score = result.get("semantic_score")
    score_value = "N/A" if score is None else f"{score}%"
    return [
        {
            "title": "Semantic Match",
            "value": score_value,
            "helper_text": "Meaning-based JD/resume alignment.",
        },
        {
            "title": "JD Requirements Checked",
            "value": str(result.get("jd_chunk_count", 0)),
            "helper_text": "Job description chunks compared.",
        },
        {
            "title": "Weak Areas",
            "value": str(len(result.get("weak_jd_chunks", []) or [])),
            "helper_text": "JD areas with lower semantic coverage.",
        },
    ]


def build_semantic_match_result(resume_text: str, jd_text: str) -> dict:
    if not clean_text_for_semantic_matching(resume_text) or not clean_text_for_semantic_matching(jd_text):
        return _unavailable_result("Add both a resume and job description to calculate semantic matching.")
    try:
        return calculate_semantic_similarity(resume_text, jd_text)
    except (ImportError, ModuleNotFoundError, RuntimeError, Exception):
        return _unavailable_result(SEMANTIC_MODEL_UNAVAILABLE_MESSAGE)
