from typing import List

from src.preprocessing import clean_text
from src.skill_extractor import extract_skills, skill_gap_analysis


def jaccard_similarity(a: List[str], b: List[str]) -> float:
    sa, sb = set([x.lower() for x in a]), set([x.lower() for x in b])
    if not sa and not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def calculate_match_score(resume_text: str, job_description: str, skills_list: List[str]) -> float:
    jd_clean = clean_text(job_description) if (job_description or "").strip() else ""
    if not jd_clean:
        return 0.0

    resume_skills = extract_skills(resume_text, skills_list)
    jd_skills = extract_skills(jd_clean, skills_list)
    return jaccard_similarity(resume_skills, jd_skills) if jd_skills else 0.0


def get_match_feedback(match_score: float) -> str:
    if match_score >= 0.65:
        return "This candidate shows strong alignment with the target role."
    if match_score >= 0.35:
        return "This candidate shows moderate alignment and may need some skill improvement."
    return "This candidate shows limited direct alignment with the target job description."


def analyze_job_description_match(resume_text: str, job_description: str, skills_list: List[str]) -> dict:
    jd_clean = clean_text(job_description) if (job_description or "").strip() else ""
    resume_skills = extract_skills(resume_text, skills_list)
    jd_skills = extract_skills(jd_clean, skills_list) if jd_clean else []
    match_score = jaccard_similarity(resume_skills, jd_skills) if jd_skills else 0.0
    gap = skill_gap_analysis(resume_skills, jd_skills) if jd_skills else {
        "matched": [],
        "missing": [],
        "extra": sorted(resume_skills),
    }
    return {
        "resume_skills": resume_skills,
        "jd_skills": jd_skills,
        "match_score": match_score,
        "gap": gap,
        "feedback": get_match_feedback(match_score),
    }
