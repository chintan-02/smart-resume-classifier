
import re
from io import BytesIO
from typing import List, Tuple, Dict
from pypdf import PdfReader

def extract_text_from_pdf(file) -> str:
    try:
        reader = PdfReader(file)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)
    except Exception:
        return ""

def extract_text_from_txt(file) -> str:
    try:
        return file.read().decode("utf-8", errors="ignore")
    except Exception:
        return ""

def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9+#./ ]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def load_skills(path: str) -> List[str]:
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

def jaccard_similarity(a: List[str], b: List[str]) -> float:
    sa, sb = set([x.lower() for x in a]), set([x.lower() for x in b])
    if not sa and not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)

def skill_gap_analysis(resume_skills: List[str], jd_skills: List[str]) -> Dict[str, List[str]]:
    rs, js = set(map(str.lower, resume_skills)), set(map(str.lower, jd_skills))
    matched = sorted(js & rs)
    missing = sorted(js - rs)
    extra = sorted(rs - js)
    return {"matched": matched, "missing": missing, "extra": extra}
