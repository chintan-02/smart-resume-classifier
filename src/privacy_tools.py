import copy
import re


def mask_email(text: str) -> str:
    return re.sub(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", "[email]", str(text or ""), flags=re.IGNORECASE)


def mask_phone(text: str) -> str:
    phone_pattern = re.compile(
        r"(?:(?:\+\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)\d{3,5}[\s.-]?\d{4})",
        flags=re.IGNORECASE,
    )
    return phone_pattern.sub("[phone]", str(text or ""))


def mask_linkedin(text: str) -> str:
    return re.sub(
        r"(?:https?://)?(?:www\.)?linkedin\.com/in/[^\s,)>\]]+",
        "[linkedin]",
        str(text or ""),
        flags=re.IGNORECASE,
    )


def mask_github(text: str) -> str:
    return re.sub(
        r"(?:https?://)?(?:www\.)?github\.com/[^\s,)>\]]+",
        "[github]",
        str(text or ""),
        flags=re.IGNORECASE,
    )


def mask_portfolio_urls(text: str) -> str:
    text = str(text or "")
    url_pattern = re.compile(r"(?:https?://|www\.)[^\s,)>\]]+|(?:[A-Za-z0-9-]+\.)+(?:dev|me|io|app|site|portfolio)\b[^\s,)>\]]*", re.IGNORECASE)

    def replace_url(match):
        url = match.group(0)
        lowered = url.lower()
        if "linkedin.com" in lowered or "github.com" in lowered:
            return url
        return "[portfolio]"

    return url_pattern.sub(replace_url, text)


def mask_candidate_name(text: str, candidate_name: str | None = None) -> str:
    text = str(text or "")
    candidate_name = str(candidate_name or "").strip()
    if not candidate_name:
        return text
    name_parts = [re.escape(part) for part in re.split(r"\s+", candidate_name) if part]
    if not name_parts:
        return text
    flexible_name_pattern = r"\b" + r"\s+".join(name_parts) + r"\b"
    return re.sub(flexible_name_pattern, "[candidate_name]", text, flags=re.IGNORECASE)


def mask_resume_header_name(text: str) -> str:
    # Privacy support only: this is not full anonymization; it masks conservative resume-header names.
    text = str(text or "")
    if not text.strip():
        return text

    section_headings = {
        "PROFESSIONAL SUMMARY",
        "SUMMARY",
        "EXPERIENCE",
        "EDUCATION",
        "SKILLS",
        "TECHNICAL SKILLS",
        "PROJECTS",
        "CERTIFICATIONS",
    }
    header_text = text.strip()[:120]
    first_line = header_text.splitlines()[0].strip()
    normalized_first_line = re.sub(r"\s+", " ", first_line).upper()
    if any(
        normalized_first_line == heading or normalized_first_line.startswith(f"{heading} ")
        for heading in section_headings
    ):
        return text

    role_keywords = (
        r"Senior|Junior|Lead|Principal|Staff|Data|Software|ML|MLOps|AI|Machine|"
        r"Engineer|Developer|Scientist|Analyst|Architect|Manager|Consultant|Specialist"
    )
    name_pattern = re.compile(
        rf"^\s*((?:[A-Z][A-Za-z'-]*|[A-Z]{{2,}})(?:\s+(?:[A-Z][A-Za-z'-]*|[A-Z]{{2,}})){{1,3}}?)"
        rf"(?=\s+(?:{role_keywords})\b)",
    )
    return name_pattern.sub("[candidate_name]", text, count=1)


def mask_location(text: str) -> str:
    text = str(text or "")
    location_pattern = re.compile(
        r"\b(?:Calgary|Edmonton|Toronto|Vancouver|Montreal|Ottawa|Vadodara|Ahmedabad|Bengaluru|Mumbai|Delhi),?\s+"
        r"(?:AB|BC|ON|QC|Alberta|British Columbia|Ontario|Quebec|Gujarat|Karnataka|Maharashtra|Canada|India)\b",
        flags=re.IGNORECASE,
    )
    return location_pattern.sub("[location]", text)


def mask_pii(
    text: str,
    candidate_name: str | None = None,
    mask_name: bool = True,
    mask_location_enabled: bool = True,
) -> str:
    masked_text = str(text or "")
    if mask_name:
        masked_text = mask_candidate_name(masked_text, candidate_name)
        masked_text = mask_resume_header_name(masked_text)
    masked_text = mask_email(masked_text)
    masked_text = mask_phone(masked_text)
    masked_text = mask_linkedin(masked_text)
    masked_text = mask_github(masked_text)
    masked_text = mask_portfolio_urls(masked_text)
    if mask_location_enabled:
        masked_text = mask_location(masked_text)
    return masked_text


def anonymize_candidate_label(candidate_name: str, rank: int | None = None) -> str:
    if rank is None:
        return "Candidate"
    return f"Candidate {rank}"


def anonymize_batch_rows(rows: list[dict]) -> list[dict]:
    anonymized_rows = []
    for index, row in enumerate(rows or [], start=1):
        copied_row = copy.deepcopy(row)
        rank = copied_row.get("Rank") or index
        copied_row["Candidate"] = anonymize_candidate_label(copied_row.get("Candidate"), rank)
        copied_row["File"] = f"resume_{rank}"
        anonymized_rows.append(copied_row)
    return anonymized_rows


def anonymize_review_records(records: list[dict]) -> list[dict]:
    anonymized_records = []
    for index, record in enumerate(records or [], start=1):
        copied_record = copy.deepcopy(record)
        rank = copied_record.get("Rank") or index
        copied_record["Candidate"] = anonymize_candidate_label(copied_record.get("Candidate"), rank)
        copied_record["File"] = f"resume_{rank}"
        copied_record["Recruiter Note"] = mask_pii(copied_record.get("Recruiter Note", ""))
        anonymized_records.append(copied_record)
    return anonymized_records


def get_privacy_mode_message(enabled: bool) -> str:
    if enabled:
        return (
            "Privacy-safe display mode is enabled. Common personal identifiers are masked in review screens "
            "and exports where possible. This does not guarantee full anonymization or remove all bias."
        )
    return "Privacy-safe display mode is off. Resume text and candidate labels may show uploaded resume information."
