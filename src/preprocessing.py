import re


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def clean_text(text: str) -> str:
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9+#./ ]", " ", text)
    return normalize_whitespace(text)


def preprocess_resume_text(text: str) -> str:
    return clean_text(text)
