from pathlib import Path


def safe_get(data, key, default=None):
    if not isinstance(data, dict):
        return default
    return data.get(key, default)


def _normalize_score(value, default=0.0) -> float:
    if value is None:
        score = float(default)
    elif isinstance(value, (int, float)):
        score = float(value)
    elif isinstance(value, str):
        cleaned = value.strip().replace("%", "")
        if not cleaned:
            score = float(default)
        else:
            try:
                score = float(cleaned)
            except ValueError:
                score = float(default)
    else:
        score = float(default)

    if 0 < score <= 1:
        score *= 100
    return max(0.0, min(100.0, score))


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


def _is_private_contact(value: str) -> bool:
    text = str(value or "").strip()
    return "@" in text or any(character.isdigit() for character in text)


def extract_candidate_name(parser_result=None, filename: str = "") -> str:
    parser_result = parser_result if isinstance(parser_result, dict) else {}
    contact_info = safe_get(parser_result, "contact_info", {}) or safe_get(parser_result, "contact", {}) or {}

    possible_names = [
        safe_get(parser_result, "candidate_name"),
        safe_get(parser_result, "name"),
        safe_get(contact_info, "candidate_name"),
        safe_get(contact_info, "name"),
    ]
    for name in possible_names:
        text = _safe_text(name)
        if text and not _is_private_contact(text):
            return text

    fallback_name = Path(str(filename or "")).stem.strip()
    if fallback_name and not _is_private_contact(fallback_name):
        return fallback_name
    return "Candidate"


def _component_label(candidate_fit_result: dict, component_name: str, default="Not available") -> str:
    for component in _as_list(safe_get(candidate_fit_result, "component_scores", [])):
        if safe_get(component, "component") == component_name:
            return _safe_text(safe_get(component, "label"), default)
    return default


def build_batch_row(
    filename: str,
    candidate_name: str,
    prediction_result=None,
    ats_result=None,
    jd_match_result=None,
    semantic_result=None,
    candidate_fit_result=None,
    skill_taxonomy_result=None,
    structure_advice=None,
    sentence_quality_result=None,
) -> dict:
    prediction_result = prediction_result if isinstance(prediction_result, dict) else {}
    ats_result = ats_result if isinstance(ats_result, dict) else {}
    jd_match_result = jd_match_result if isinstance(jd_match_result, dict) else {}
    semantic_result = semantic_result if isinstance(semantic_result, dict) else {}
    candidate_fit_result = candidate_fit_result if isinstance(candidate_fit_result, dict) else {}
    skill_taxonomy_result = skill_taxonomy_result if isinstance(skill_taxonomy_result, dict) else {}
    structure_advice = structure_advice if isinstance(structure_advice, dict) else {}
    sentence_quality_result = sentence_quality_result if isinstance(sentence_quality_result, dict) else {}

    gap = safe_get(jd_match_result, "gap", {}) or {}
    matched_skills = _as_list(safe_get(gap, "matched", safe_get(jd_match_result, "matched_skills", [])))
    missing_skills = _as_list(safe_get(gap, "missing", safe_get(jd_match_result, "missing_skills", [])))
    top_gap_categories = _as_list(safe_get(skill_taxonomy_result, "top_gap_categories", []))
    risk_signals = _as_list(safe_get(candidate_fit_result, "risk_signals", []))
    priority_actions = _as_list(safe_get(candidate_fit_result, "priority_actions", []))

    semantic_score = 0.0
    if safe_get(semantic_result, "available") and safe_get(semantic_result, "semantic_score") is not None:
        semantic_score = _normalize_score(safe_get(semantic_result, "semantic_score"))

    return {
        "Rank": None,
        "Candidate": _safe_text(candidate_name, "Candidate"),
        "File": _safe_text(filename, "Unknown file"),
        "Predicted Role": _safe_text(safe_get(prediction_result, "role"), "Not available"),
        "Model Confidence": round(_normalize_score(safe_get(prediction_result, "confidence")), 1),
        "Overall Fit Score": round(_normalize_score(safe_get(candidate_fit_result, "overall_fit_score")), 1),
        "Fit Label": _safe_text(safe_get(candidate_fit_result, "fit_label"), "Not available"),
        "Recommendation": _safe_text(safe_get(candidate_fit_result, "recommendation"), "Not available"),
        "ATS Score": round(_normalize_score(safe_get(ats_result, "ats_score")), 1),
        "JD Match Score": round(_normalize_score(safe_get(jd_match_result, "match_score")), 1),
        "Semantic Match Score": round(semantic_score, 1),
        "Matched Skills": len(matched_skills),
        "Missing Skills": len(missing_skills),
        "Top Gap Categories": ", ".join(top_gap_categories[:4]),
        "Resume Quality": _component_label(candidate_fit_result, "Resume Quality"),
        "Structure Grade": _safe_text(safe_get(structure_advice, "overall_structure_grade"), "Not available"),
        "Risk Count": len(risk_signals),
        "Priority Actions": " | ".join(priority_actions[:3]),
    }


def rank_batch_results(rows: list[dict]) -> list[dict]:
    sorted_rows = sorted(
        _as_list(rows),
        key=lambda row: (
            _normalize_score(safe_get(row, "Overall Fit Score")),
            _normalize_score(safe_get(row, "Semantic Match Score")),
            _normalize_score(safe_get(row, "ATS Score")),
            _normalize_score(safe_get(row, "JD Match Score")),
        ),
        reverse=True,
    )
    ranked_rows = []
    for index, row in enumerate(sorted_rows, start=1):
        ranked_row = dict(row)
        ranked_row["Rank"] = index
        ranked_rows.append(ranked_row)
    return ranked_rows


def get_batch_summary(rows: list[dict]) -> dict:
    rows = _as_list(rows)
    total_resumes = len(rows)
    recommended_for_review = sum(1 for row in rows if safe_get(row, "Recommendation") == "Recommended for review")
    partial_fit = sum(1 for row in rows if safe_get(row, "Fit Label") == "Partial Fit")
    needs_improvement = sum(1 for row in rows if safe_get(row, "Fit Label") == "Needs Improvement")
    scores = [_normalize_score(safe_get(row, "Overall Fit Score")) for row in rows]
    average_fit_score = sum(scores) / total_resumes if total_resumes else 0.0
    top_candidate_label = "Not available"
    if rows:
        top_candidate_label = f"Top-ranked resume by fit signals: {safe_get(rows[0], 'Candidate', 'Candidate')}"

    if total_resumes:
        main_message = (
            f"Analyzed {total_resumes} resumes and ranked them by fit signals based on available "
            "resume and job-description content."
        )
    else:
        main_message = "Upload multiple resumes and run batch ranking to compare local fit signals."

    return {
        "total_resumes": total_resumes,
        "recommended_for_review": recommended_for_review,
        "partial_fit": partial_fit,
        "needs_improvement": needs_improvement,
        "average_fit_score": round(average_fit_score, 1),
        "top_candidate_label": top_candidate_label,
        "main_message": main_message,
    }


def convert_rows_to_csv(rows: list[dict]) -> str:
    rows = _as_list(rows)
    try:
        import pandas as pd

        return pd.DataFrame(rows).to_csv(index=False)
    except Exception:
        import csv
        from io import StringIO

        output = StringIO()
        fieldnames = list(rows[0].keys()) if rows else []
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        return output.getvalue()


def get_batch_summary_cards(summary: dict) -> list[dict]:
    summary = summary if isinstance(summary, dict) else {}
    return [
        {
            "title": "Resumes Analyzed",
            "value": str(safe_get(summary, "total_resumes", 0)),
            "helper_text": "Uploaded resumes processed locally.",
        },
        {
            "title": "Recommended for Review",
            "value": str(safe_get(summary, "recommended_for_review", 0)),
            "helper_text": "Decision-support recommendation only.",
        },
        {
            "title": "Average Fit Score",
            "value": f"{round(_normalize_score(safe_get(summary, 'average_fit_score', 0)))}%",
            "helper_text": "Average weighted fit signal.",
        },
    ]
