import re
from typing import Iterable, List, Optional


GENERIC_PHRASES = [
    "results-driven",
    "detail-oriented",
    "team player",
    "hardworking",
    "self-motivated",
    "fast learner",
    "passionate professional",
    "dynamic professional",
    "proven track record",
    "excellent communication skills",
    "problem-solving skills",
]

WEAK_PHRASES = [
    "responsible for",
    "worked on",
    "helped with",
    "assisted with",
    "participated in",
    "involved in",
    "handled",
    "various tasks",
]

VAGUE_PHRASES = [
    "leveraging data-driven insights",
    "optimize business outcomes",
    "drive business growth",
    "cross-functional collaboration",
    "strategic initiatives",
    "value-added solutions",
    "actionable insights",
]

STRONG_ACTION_VERBS = [
    "built",
    "developed",
    "engineered",
    "automated",
    "optimized",
    "improved",
    "reduced",
    "increased",
    "deployed",
    "implemented",
    "designed",
    "analyzed",
    "created",
    "trained",
    "evaluated",
    "integrated",
    "streamlined",
    "delivered",
]

COMMON_TOOLS_AND_SKILLS = [
    "Python",
    "SQL",
    "Pandas",
    "NumPy",
    "Scikit-Learn",
    "TensorFlow",
    "PyTorch",
    "Docker",
    "Git",
    "GitHub",
    "AWS",
    "Azure",
    "GCP",
    "Tableau",
    "Power BI",
    "Excel",
    "FastAPI",
    "Flask",
    "Streamlit",
    "Spark",
    "Hadoop",
    "NLP",
    "Machine Learning",
]

PLACEHOLDER_METADATA_TERMS = [
    "job title",
    "company name",
    "location",
    "month, year",
    "graduation year",
    "university name",
    "your name",
    "phone number",
    "email address",
    "linkedin url",
    "github/portfolio url",
    "github url",
    "portfolio url",
]

SHORT_METADATA_TERMS = [
    "name",
    "phone",
    "email",
    "linkedin",
    "github",
    "portfolio",
    "location",
    "address",
    "graduation year",
    "month, year",
]


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _find_phrases(sentence: str, phrases: Iterable[str]) -> List[str]:
    normalized = _normalize_text(sentence).lower()
    return [phrase for phrase in phrases if phrase.lower() in normalized]


def _contains_obvious_generic_phrase(sentence: str) -> bool:
    return bool(
        _find_phrases(sentence, GENERIC_PHRASES)
        or _find_phrases(sentence, WEAK_PHRASES)
        or _find_phrases(sentence, VAGUE_PHRASES)
    )


def is_placeholder_or_metadata_line(sentence) -> bool:
    """
    Identify template placeholders and resume header/contact metadata, not prose bullets.
    """
    text = _normalize_text(sentence).strip(" -\t")
    if not text:
        return True

    lowered = text.lower()
    bracketed_values = re.findall(r"\[([^\]]+)\]", text)
    normalized_bracketed = [
        re.sub(r"\s+", " ", value.strip().lower())
        for value in bracketed_values
    ]

    if len(bracketed_values) >= 2:
        remaining = re.sub(r"\[[^\]]+\]", "", text)
        remaining = re.sub(r"[\s|,;/\\:()\-]+", "", remaining)
        if not remaining:
            return True

    if normalized_bracketed and all(
        value in PLACEHOLDER_METADATA_TERMS for value in normalized_bracketed
    ):
        remaining = re.sub(r"\[[^\]]+\]", "", text)
        remaining = re.sub(r"[\s|,;/\\:()\-]+", "", remaining)
        if not remaining:
            return True

    for term in PLACEHOLDER_METADATA_TERMS:
        if re.fullmatch(rf"\[\s*{re.escape(term)}\s*\]", lowered):
            return True

    separator_stripped = re.sub(r"[\s|,;/\\:\[\](){}<>\-_.]+", "", text)
    if not separator_stripped:
        return True

    word_count = len(re.findall(r"\b[a-zA-Z][a-zA-Z/+.-]*\b", text))
    punctuation_count = len(re.findall(r"[\[\]|,;/\\:(){}<>\-_]", text))
    punctuation_ratio = punctuation_count / max(1, len(text))
    if word_count <= 4 and punctuation_ratio >= 0.35 and bracketed_values:
        return True

    if word_count <= 4:
        plain = re.sub(r"[\[\]]", "", lowered).strip(" |,;:/\\-")
        if plain in SHORT_METADATA_TERMS or plain in PLACEHOLDER_METADATA_TERMS:
            return True

        contact_patterns = [
            r"\b[\w.+-]+@[\w.-]+\.\w+\b",
            r"\b(?:https?://|www\.)\S+\b",
            r"\b(?:linkedin|github|portfolio)\b",
            r"\b(?:phone|email|address)\b",
            r"\b(?:\+?\d[\d\s().-]{7,})\b",
        ]
        if any(re.search(pattern, lowered) for pattern in contact_patterns):
            return True

    return False


def split_into_sentences(text: str) -> List[str]:
    """
    Split resume text into readable sentence and bullet-like units.
    """
    if not text or not text.strip():
        return []

    cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
    cleaned = re.sub(r"(?m)^\s*[\u2022\-\*\u25E6\u25AA\u25CF]+\s*", "", cleaned)
    cleaned = re.sub(r"(?m)^\s*\d+[\.)]\s+", "", cleaned)

    candidates = []
    for line in cleaned.split("\n"):
        line = line.strip(" \t:-")
        if not line:
            continue

        parts = re.split(r";+|(?<=[.!?])\s+", line)
        candidates.extend(parts)

    sentences = []
    for candidate in candidates:
        sentence = _normalize_text(candidate).strip(" -\t")
        if not sentence:
            continue

        if is_placeholder_or_metadata_line(sentence):
            continue

        word_count = len(re.findall(r"\b[\w+#.-]+\b", sentence))
        if word_count >= 5 or _contains_obvious_generic_phrase(sentence):
            sentences.append(sentence)

    return sentences


def _has_metric(sentence: str) -> bool:
    patterns = [
        r"\b\d+(?:\.\d+)?\s*%",
        r"\b\d+(?:\.\d+)?\s*(?:k|m|b)?\+?\b",
        r"\b(?:reduced|increased|improved)\s+by\b",
    ]
    return any(re.search(pattern, sentence, flags=re.IGNORECASE) for pattern in patterns)


def _has_action_verb(sentence: str) -> bool:
    return any(
        re.search(rf"\b{re.escape(verb)}\b", sentence, flags=re.IGNORECASE)
        for verb in STRONG_ACTION_VERBS
    )


def _has_tool_or_skill(sentence: str, extracted_skills: Optional[Iterable[str]] = None) -> bool:
    skills = list(COMMON_TOOLS_AND_SKILLS)
    if extracted_skills:
        skills.extend(str(skill) for skill in extracted_skills if str(skill).strip())

    for skill in skills:
        pattern = rf"(?<!\w){re.escape(str(skill).strip())}(?!\w)"
        if re.search(pattern, sentence, flags=re.IGNORECASE):
            return True
    return False


def _risk_level(score: int) -> str:
    if score >= 70:
        return "High"
    if score >= 40:
        return "Moderate"
    return "Low"


def analyze_sentence_quality(sentence, extracted_skills=None):
    generic_phrases = _find_phrases(sentence, GENERIC_PHRASES)
    weak_phrases = _find_phrases(sentence, WEAK_PHRASES)
    vague_phrases = _find_phrases(sentence, VAGUE_PHRASES)
    has_metric = _has_metric(sentence)
    has_tool_or_skill = _has_tool_or_skill(sentence, extracted_skills)
    has_action_verb = _has_action_verb(sentence)

    score = 0
    reasons = []

    if generic_phrases:
        score += min(40, 20 * len(generic_phrases))
        reasons.extend(
            f"Contains generic phrase: {phrase}"
            for phrase in generic_phrases
        )

    if weak_phrases:
        score += min(30, 12 * len(weak_phrases))
        reasons.extend(
            f"Uses weak phrase: {phrase}"
            for phrase in weak_phrases
        )

    if vague_phrases:
        score += min(36, 18 * len(vague_phrases))
        reasons.extend(
            f"Includes vague phrase: {phrase}"
            for phrase in vague_phrases
        )

    if not has_metric:
        score += 15
        reasons.append("No measurable metric or quantified result was found.")

    if not has_tool_or_skill:
        score += 15
        reasons.append("No specific tool, technology, or skill was detected.")

    if not has_action_verb:
        score += 15
        reasons.append("No strong action verb was detected.")

    generic_score = max(0, min(100, score))

    return {
        "sentence": _normalize_text(sentence),
        "generic_score": generic_score,
        "risk_level": _risk_level(generic_score),
        "reasons": reasons,
        "signals": {
            "generic_phrases": generic_phrases,
            "weak_phrases": weak_phrases,
            "vague_phrases": vague_phrases,
            "has_metric": has_metric,
            "has_tool_or_skill": has_tool_or_skill,
            "has_action_verb": has_action_verb,
        },
    }


def detect_ai_like_sentences(resume_text, extracted_skills=None, max_results=10):
    sentences = [
        sentence for sentence in split_into_sentences(resume_text or "")
        if not is_placeholder_or_metadata_line(sentence)
    ]
    analyzed = [
        analyze_sentence_quality(sentence, extracted_skills=extracted_skills)
        for sentence in sentences
    ]
    flagged = [
        item for item in analyzed
        if item["risk_level"] in {"Moderate", "High"}
    ]
    flagged.sort(key=lambda item: item["generic_score"], reverse=True)

    limited_flagged = flagged[:max(0, int(max_results or 0))]
    high_risk_count = sum(1 for item in flagged if item["risk_level"] == "High")
    moderate_risk_count = sum(1 for item in flagged if item["risk_level"] == "Moderate")

    return {
        "flagged_sentences": limited_flagged,
        "total_sentences_analyzed": len(sentences),
        "high_risk_count": high_risk_count,
        "moderate_risk_count": moderate_risk_count,
        "summary": generate_sentence_quality_summary(flagged, len(sentences)),
    }


def generate_sentence_quality_summary(flagged_sentences, total_sentences):
    if not flagged_sentences:
        return "Your resume language looks specific, natural, and recruiter-friendly."

    count = len(flagged_sentences)
    return (
        f"The system found {count} sentences that may sound generic, vague, or AI-like. "
        "Review these lines to make them more specific, measurable, and achievement-focused."
    )
