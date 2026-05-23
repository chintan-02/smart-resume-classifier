from pathlib import Path

from pypdf import PdfReader

from src.app_config import SUPPORTED_FILE_EXTENSIONS


def extract_text_from_pdf(uploaded_file) -> str:
    try:
        reader = PdfReader(uploaded_file)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)
    except Exception:
        return ""


def extract_text_from_txt(uploaded_file) -> str:
    try:
        return uploaded_file.read().decode("utf-8", errors="ignore")
    except Exception:
        return ""


def get_file_extension(uploaded_file) -> str:
    return Path(getattr(uploaded_file, "name", "")).suffix.lower()


def is_supported_file(uploaded_file) -> bool:
    return get_file_extension(uploaded_file) in SUPPORTED_FILE_EXTENSIONS


def extract_resume_text(uploaded_file) -> str:
    suffix = get_file_extension(uploaded_file)
    if suffix == ".pdf":
        return extract_text_from_pdf(uploaded_file)
    if suffix == ".txt":
        return extract_text_from_txt(uploaded_file)
    return ""
