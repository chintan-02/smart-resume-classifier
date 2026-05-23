import re
from pathlib import Path
from typing import Dict, List

from src.app_config import SKILLS_PATH
from src.preprocessing import clean_text


def load_skills(path: Path = SKILLS_PATH) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        skills = [line.strip().lower() for line in f if line.strip()]
    return sorted(set(skills), key=len, reverse=True)


def extract_skills(text: str, skills_list: List[str]) -> List[str]:
    text = clean_text(text)
    found = []
    for skill in skills_list:
        pattern = rf"(?<!\w){re.escape(skill.lower())}(?!\w)"
        if re.search(pattern, text):
            found.append(skill)
    return sorted(set(found))


def compare_skills(resume_skills: List[str], jd_skills: List[str]) -> Dict[str, List[str]]:
    return skill_gap_analysis(resume_skills, jd_skills)


def skill_gap_analysis(resume_skills: List[str], jd_skills: List[str]) -> Dict[str, List[str]]:
    rs, js = set(map(str.lower, resume_skills)), set(map(str.lower, jd_skills))
    matched = sorted(js & rs)
    missing = sorted(js - rs)
    extra = sorted(rs - js)
    return {"matched": matched, "missing": missing, "extra": extra}
