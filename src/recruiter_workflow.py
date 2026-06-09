import re


REVIEW_STATUS_OPTIONS = [
    "Recommended for review",
    "Shortlisted for follow-up",
    "Needs follow-up",
    "Not selected for now",
]


def safe_get(data, key, default=None):
    if not isinstance(data, dict):
        return default
    return data.get(key, default)


def _as_list(value) -> list:
    if not value:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, (tuple, set)):
        return list(value)
    return []


def _safe_text(value, default="") -> str:
    text = str(value or "").strip()
    return text if text else default


def get_review_status_options() -> list[str]:
    return REVIEW_STATUS_OPTIONS.copy()


def get_default_review_status(row: dict) -> str:
    recommendation = _safe_text(safe_get(row, "Recommendation")).lower()
    fit_label = _safe_text(safe_get(row, "Fit Label")).lower()

    if "recommended for review" in recommendation:
        return "Recommended for review"
    if "good fit" in fit_label or "strong fit" in fit_label:
        return "Recommended for review"
    if "partial fit" in fit_label:
        return "Needs follow-up"
    return "Needs follow-up"


def make_review_key(row: dict) -> str:
    raw_key = "|".join(
        [
            _safe_text(safe_get(row, "Rank"), "0"),
            _safe_text(safe_get(row, "Candidate"), "Candidate"),
            _safe_text(safe_get(row, "File"), "File"),
        ]
    )
    cleaned = re.sub(r"\s+", "_", raw_key.strip())
    return re.sub(r"[^A-Za-z0-9_.|-]", "", cleaned) or "review_record"


def create_review_record(row: dict, status: str, note: str) -> dict:
    return {
        "Candidate": _safe_text(safe_get(row, "Candidate"), "Candidate"),
        "File": _safe_text(safe_get(row, "File"), "Unknown file"),
        "Rank": safe_get(row, "Rank", ""),
        "Overall Fit Score": safe_get(row, "Overall Fit Score", 0.0),
        "Fit Label": _safe_text(safe_get(row, "Fit Label"), "Not available"),
        "Recommendation": _safe_text(safe_get(row, "Recommendation"), "Not available"),
        "Manual Review Status": _safe_text(status, "Needs follow-up"),
        "Recruiter Note": _safe_text(note),
        "Priority Actions": _safe_text(safe_get(row, "Priority Actions")),
    }


def build_review_records(rows: list[dict], review_state: dict) -> list[dict]:
    review_state = review_state if isinstance(review_state, dict) else {}
    records = []
    for row in _as_list(rows):
        if not isinstance(row, dict):
            continue
        review_key = make_review_key(row)
        saved_review = safe_get(review_state, review_key, {}) or {}
        status = safe_get(saved_review, "status", get_default_review_status(row))
        note = safe_get(saved_review, "note", "")
        records.append(create_review_record(row, status, note))
    return records


def get_review_summary(records: list[dict]) -> dict:
    records = _as_list(records)
    total_reviewed = len(records)
    recommended_for_review = 0
    shortlisted_for_follow_up = 0
    needs_follow_up = 0
    not_selected_for_now = 0

    for record in records:
        status = safe_get(record, "Manual Review Status")
        if status == "Recommended for review":
            recommended_for_review += 1
        elif status == "Shortlisted for follow-up":
            shortlisted_for_follow_up += 1
        elif status == "Needs follow-up":
            needs_follow_up += 1
        elif status == "Not selected for now":
            not_selected_for_now += 1

    if total_reviewed:
        main_message = (
            f"Prepared manual review records for {total_reviewed} ranked resumes. "
            "These statuses and notes are session-local decision-support data."
        )
    else:
        main_message = "Run Batch Ranking first to add recruiter notes and shortlist statuses."

    return {
        "total_reviewed": total_reviewed,
        "recommended_for_review": recommended_for_review,
        "shortlisted_for_follow_up": shortlisted_for_follow_up,
        "needs_follow_up": needs_follow_up,
        "not_selected_for_now": not_selected_for_now,
        "main_message": main_message,
    }


def get_review_summary_cards(summary: dict) -> list[dict]:
    summary = summary if isinstance(summary, dict) else {}
    return [
        {
            "title": "Reviewed Resumes",
            "value": str(safe_get(summary, "total_reviewed", 0)),
            "helper_text": "Ranked resumes with review records.",
        },
        {
            "title": "Shortlisted",
            "value": str(safe_get(summary, "shortlisted_for_follow_up", 0)),
            "helper_text": "Marked for follow-up.",
        },
        {
            "title": "Needs Follow-Up",
            "value": str(safe_get(summary, "needs_follow_up", 0)),
            "helper_text": "Requires additional manual review.",
        },
    ]


def convert_review_records_to_csv(records: list[dict]) -> str:
    records = _as_list(records)
    try:
        import pandas as pd

        return pd.DataFrame(records).to_csv(index=False)
    except Exception:
        import csv
        from io import StringIO

        output = StringIO()
        fieldnames = list(records[0].keys()) if records else []
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
        return output.getvalue()
