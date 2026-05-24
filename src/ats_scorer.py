import re
from collections import Counter
from typing import Iterable, Optional


ATS_DISCLAIMER = (
    "This score estimates ATS compatibility based on resume structure, keyword relevance, "
    "skills, and job-description alignment. It is not an official score from any specific ATS platform."
)

STOP_WORDS = {
    "a",
    "about",
    "above",
    "after",
    "again",
    "against",
    "all",
    "also",
    "am",
    "an",
    "and",
    "any",
    "are",
    "as",
    "at",
    "be",
    "because",
    "been",
    "being",
    "below",
    "between",
    "both",
    "but",
    "by",
    "can",
    "could",
    "did",
    "do",
    "does",
    "doing",
    "down",
    "during",
    "each",
    "few",
    "for",
    "from",
    "further",
    "had",
    "has",
    "have",
    "having",
    "he",
    "her",
    "here",
    "hers",
    "herself",
    "him",
    "himself",
    "his",
    "how",
    "i",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "itself",
    "just",
    "me",
    "more",
    "most",
    "my",
    "myself",
    "nor",
    "not",
    "now",
    "of",
    "off",
    "on",
    "once",
    "only",
    "or",
    "other",
    "our",
    "ours",
    "ourselves",
    "out",
    "over",
    "own",
    "same",
    "she",
    "should",
    "so",
    "some",
    "such",
    "than",
    "that",
    "the",
    "their",
    "theirs",
    "them",
    "themselves",
    "then",
    "there",
    "these",
    "they",
    "this",
    "those",
    "through",
    "to",
    "too",
    "under",
    "until",
    "up",
    "very",
    "was",
    "we",
    "were",
    "what",
    "when",
    "where",
    "which",
    "while",
    "who",
    "whom",
    "why",
    "will",
    "with",
    "you",
    "your",
    "yours",
    "yourself",
    "yourselves",
}

IMPACT_VERBS = {
    "improved",
    "increased",
    "reduced",
    "automated",
    "optimized",
    "developed",
    "built",
    "engineered",
    "delivered",
    "saved",
    "accelerated",
    "streamlined",
}

PLACEHOLDER_PATTERNS = (
    r"\byour name\b",
    r"\bcompany name\b",
    r"\bjob title\b",
    r"\bemail address\b",
    r"\bphone number\b",
    r"\blinkedin url\b",
    r"\bgithub/portfolio url\b",
    r"\badd measurable result\b",
    r"\bplaceholder\b",
    r"\[[^\]]+\]",
)


def _clamp_score(value: float) -> int:
    return int(round(max(0, min(100, value))))


def _lower_set(items: Optional[Iterable[str]]) -> set[str]:
    return {str(item).strip().lower() for item in (items or []) if str(item).strip()}


def calculate_ats_score(
    resume_text,
    job_description,
    resume_skills=None,
    jd_skills=None,
    matched_skills=None,
    missing_skills=None,
    parser_result=None,
    existing_match_score=None,
):
    skill_match = calculate_skill_match_score(resume_skills, jd_skills, matched_skills)
    keyword_coverage = calculate_keyword_coverage(resume_text, job_description)
    section_quality = calculate_section_quality(parser_result)
    achievement_score = calculate_achievement_score(resume_text)
    formatting_score = calculate_formatting_score(resume_text, parser_result)

    if existing_match_score is None:
        jd_alignment = _clamp_score((skill_match + keyword_coverage) / 2)
    else:
        match_value = float(existing_match_score or 0)
        jd_alignment = _clamp_score(match_value * 100 if match_value <= 1 else match_value)

    breakdown = {
        "skill_match": skill_match,
        "keyword_coverage": keyword_coverage,
        "section_quality": section_quality,
        "achievement_score": achievement_score,
        "formatting_score": formatting_score,
        "jd_alignment": jd_alignment,
    }

    ats_score = _clamp_score(
        (skill_match * 0.25)
        + (keyword_coverage * 0.20)
        + (section_quality * 0.20)
        + (achievement_score * 0.15)
        + (formatting_score * 0.10)
        + (jd_alignment * 0.10)
    )
    feedback = generate_ats_feedback(ats_score, breakdown, missing_skills)

    return {
        "ats_score": ats_score,
        "grade": feedback["grade"],
        "breakdown": breakdown,
        "strengths": feedback["strengths"],
        "improvements": feedback["improvements"],
        "feedback": feedback["feedback"],
        "disclaimer": ATS_DISCLAIMER,
    }


def calculate_skill_match_score(resume_skills, jd_skills, matched_skills):
    jd_skill_set = _lower_set(jd_skills)
    if not jd_skill_set:
        return 0

    matched_skill_set = _lower_set(matched_skills)
    if not matched_skill_set:
        matched_skill_set = _lower_set(resume_skills) & jd_skill_set

    return _clamp_score((len(matched_skill_set) / len(jd_skill_set)) * 100)


def calculate_keyword_coverage(resume_text, job_description):
    resume = (resume_text or "").lower()
    jd = (job_description or "").lower()
    if not resume.strip() or not jd.strip():
        return 0

    words = re.findall(r"\b[a-z][a-z0-9+#./-]{2,}\b", jd)
    keywords = [
        word.strip(".-/")
        for word in words
        if len(word.strip(".-/")) >= 3 and word not in STOP_WORDS
    ]
    if not keywords:
        return 0

    keyword_counts = Counter(keywords)
    meaningful_keywords = set(keyword_counts)
    matched = sum(1 for keyword in meaningful_keywords if re.search(rf"(?<!\w){re.escape(keyword)}(?!\w)", resume))
    return _clamp_score((matched / len(meaningful_keywords)) * 100)


def calculate_section_quality(parser_result):
    sections = (parser_result or {}).get("sections") or {}
    if not sections:
        return 0

    section_weights = {
        "summary": 15,
        "skills": 20,
        "experience": 25,
        "projects": 20,
        "education": 15,
        "certifications": 5,
    }
    score = 0
    for section, weight in section_weights.items():
        if str(sections.get(section, "")).strip():
            score += weight
    return _clamp_score(score)


def calculate_achievement_score(resume_text):
    text = resume_text or ""
    if not text.strip():
        return 0

    percentage_count = len(re.findall(r"\b\d+(?:\.\d+)?\s*%", text))
    metric_count = len(re.findall(r"\b\d+(?:\.\d+)?\s*(?:\+|k\+?|m\+?)\b", text, flags=re.IGNORECASE))
    larger_number_count = len(re.findall(r"\b\d{2,}(?:,\d{3})*\b", text))
    verb_count = len(re.findall(rf"\b({'|'.join(sorted(IMPACT_VERBS))})\b", text, flags=re.IGNORECASE))

    score = 0
    score += min(percentage_count, 4) * 12
    score += min(metric_count, 4) * 10
    score += min(larger_number_count, 4) * 6
    score += min(verb_count, 8) * 6

    if (percentage_count or metric_count or larger_number_count) and verb_count:
        score += 10

    return _clamp_score(score)


def calculate_formatting_score(resume_text, parser_result=None):
    text = resume_text or ""
    if not text.strip():
        return 0

    score = 20
    word_count = len(re.findall(r"\b\w+\b", text))
    line_count = len([line for line in text.splitlines() if line.strip()])
    bullet_count = len(re.findall(r"(?m)^\s*(?:[-*•]|\d+[.)])\s+", text))
    heading_count = len(
        re.findall(
            r"(?im)^\s*(summary|career profile|skills|technical skills|experience|professional experience|projects|education|certifications)\s*:?\s*$",
            text,
        )
    )
    placeholder_count = sum(len(re.findall(pattern, text, flags=re.IGNORECASE)) for pattern in PLACEHOLDER_PATTERNS)

    if 250 <= word_count <= 1200:
        score += 25
    elif 120 <= word_count < 250 or 1200 < word_count <= 1600:
        score += 15
    elif word_count >= 60:
        score += 8

    if line_count >= 8:
        score += 15
    elif line_count >= 4:
        score += 8

    if bullet_count >= 4:
        score += 15
    elif bullet_count >= 1:
        score += 8

    if heading_count >= 4:
        score += 20
    elif heading_count >= 2:
        score += 12
    elif heading_count >= 1:
        score += 6

    if placeholder_count >= 5:
        score -= 25
    elif placeholder_count >= 1:
        score -= 10

    template_detection = (parser_result or {}).get("template_detection") or {}
    severity = template_detection.get("severity")
    if severity == "strong":
        score -= 35
    elif severity == "partial":
        score -= 15

    return _clamp_score(score)


def generate_ats_feedback(ats_score, breakdown, missing_skills=None):
    if ats_score >= 85:
        grade = "Excellent"
        feedback = (
            "This resume looks highly compatible with the target role. It has strong structure, "
            "solid keyword alignment, and enough evidence for a recruiter or screening workflow to understand the fit quickly."
        )
    elif ats_score >= 70:
        grade = "Good"
        feedback = (
            "This resume has good ATS compatibility and should be readable for most screening workflows. "
            "A few targeted keyword, skill, or achievement updates could make the alignment stronger."
        )
    elif ats_score >= 50:
        grade = "Moderate"
        feedback = (
            "This resume has a reasonable foundation, but it may need clearer role alignment. "
            "Improving missing skills, section completeness, and measurable results can help it perform better."
        )
    else:
        grade = "Needs Improvement"
        feedback = (
            "This resume may struggle to communicate fit for the target role. "
            "Focus on completing core sections, adding relevant keywords, and replacing generic wording with measurable achievements."
        )

    strengths = []
    improvements = []

    if breakdown.get("skill_match", 0) >= 70:
        strengths.append("Strong overlap between resume skills and job-description skills.")
    else:
        improvements.append("Add more relevant skills from the job description where they truthfully apply.")

    if breakdown.get("keyword_coverage", 0) >= 70:
        strengths.append("Good keyword coverage from the target job description.")
    else:
        improvements.append("Mirror important job-description keywords naturally in summary, skills, and experience sections.")

    if breakdown.get("section_quality", 0) >= 75:
        strengths.append("Core resume sections are present and easy to identify.")
    else:
        improvements.append("Include clear sections for summary, skills, experience, projects, and education.")

    if breakdown.get("achievement_score", 0) >= 60:
        strengths.append("Resume includes measurable impact signals and action-oriented language.")
    else:
        improvements.append("Add quantified achievements, such as percentages, counts, savings, speedups, or scale.")

    if breakdown.get("formatting_score", 0) >= 75:
        strengths.append("Formatting appears readable, structured, and parser-friendly.")
    else:
        improvements.append("Use clear headings, bullet points, line breaks, and remove placeholder text.")

    missing = [skill for skill in (missing_skills or []) if skill]
    if missing:
        improvements.append("Prioritize missing target skills: " + ", ".join(missing[:8]) + ".")

    return {
        "grade": grade,
        "strengths": strengths[:5],
        "improvements": improvements[:6],
        "feedback": feedback,
    }
