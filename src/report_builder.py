import re
from collections import Counter


REPORT_DISCLAIMER = (
    "This report is a local, rule-based ResumeIQ improvement summary. It estimates resume readiness "
    "from available resume and job-description signals, but it is not an official ATS score, hiring "
    "decision, or guarantee of job success."
)


def safe_get(data, key, default=None):
    if not isinstance(data, dict):
        return default
    return data.get(key, default)


def normalize_score(value, default=0):
    if value is None:
        return float(default)
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.strip().replace("%", "")
        if not cleaned:
            return float(default)
        try:
            return float(cleaned)
        except ValueError:
            return float(default)
    return float(default)


def _as_percent(value, default=0):
    score = normalize_score(value, default=default)
    if 0 < score <= 1:
        return score * 100
    return score


def _list_value(value):
    if not value:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple) or isinstance(value, set):
        return list(value)
    return []


def _append_unique(items, value):
    if value and value not in items:
        items.append(value)


def _format_percent(score):
    return f"{round(score)}%"


def _confidence_value(prediction_result):
    confidence = safe_get(prediction_result, "confidence")
    if confidence is None:
        confidence = safe_get(prediction_result, "confidence_display")
    return _as_percent(confidence, default=0)


def _build_readiness_level(ats_score, jd_match_score, high_risk_count, missing_count, template_severity):
    high_priority = (
        template_severity == "strong"
        or (ats_score < 45 and jd_match_score < 30)
        or missing_count >= 8
        or high_risk_count >= 4
    )
    if high_priority:
        return "High Priority Fixes Needed"
    if ats_score >= 80 and jd_match_score >= 70 and high_risk_count <= 1 and missing_count <= 3:
        return "Strong"
    if ats_score >= 65 and jd_match_score >= 50:
        return "Good"
    if ats_score >= 45 or jd_match_score >= 30:
        return "Needs Improvement"
    return "High Priority Fixes Needed"


def build_resume_improvement_report(
    prediction_result=None,
    ats_result=None,
    jd_match_result=None,
    sentence_quality_result=None,
    rewrite_suggestions=None,
    parser_result=None,
) -> dict:
    prediction_result = prediction_result if isinstance(prediction_result, dict) else {}
    ats_result = ats_result if isinstance(ats_result, dict) else {}
    jd_match_result = jd_match_result if isinstance(jd_match_result, dict) else {}
    sentence_quality_result = sentence_quality_result if isinstance(sentence_quality_result, dict) else {}
    parser_result = parser_result if isinstance(parser_result, dict) else {}
    rewrite_suggestions = _list_value(rewrite_suggestions)

    gap = safe_get(jd_match_result, "gap", {}) or {}
    template_detection = safe_get(parser_result, "template_detection", {}) or {}

    ats_score = _as_percent(safe_get(ats_result, "ats_score", 0))
    ats_grade = safe_get(ats_result, "grade", "Not available")
    jd_match_score = _as_percent(safe_get(jd_match_result, "match_score", 0))
    matched_skills = _list_value(safe_get(gap, "matched", safe_get(jd_match_result, "matched_skills", [])))
    missing_skills = _list_value(safe_get(gap, "missing", safe_get(jd_match_result, "missing_skills", [])))
    extra_skills = _list_value(safe_get(gap, "extra", safe_get(jd_match_result, "extra_skills", [])))
    flagged_sentences = _list_value(safe_get(sentence_quality_result, "flagged_sentences", []))
    high_risk_count = int(normalize_score(safe_get(sentence_quality_result, "high_risk_count", 0)))
    moderate_risk_count = int(normalize_score(safe_get(sentence_quality_result, "moderate_risk_count", 0)))
    template_severity = safe_get(template_detection, "severity", "none")
    predicted_role = safe_get(prediction_result, "role", "Not available")
    model_confidence = _confidence_value(prediction_result)

    strengths = []
    risks = []
    priority_actions = []

    if matched_skills:
        _append_unique(strengths, "Resume matches several target job description skills.")
    if extra_skills:
        _append_unique(strengths, "Resume includes relevant skills detected by the parser.")
    if ats_score >= 70:
        _append_unique(strengths, "ATS compatibility is currently strong or good based on available signals.")
    if jd_match_score >= 50:
        _append_unique(strengths, "Resume shows meaningful overlap with the target job description.")
    if (safe_get(ats_result, "breakdown", {}) or {}).get("achievement_score", 0) >= 50:
        _append_unique(strengths, "The resume includes measurable or project-based experience signals.")
    if not strengths:
        _append_unique(strengths, "ResumeIQ found enough content to generate an improvement plan.")

    if missing_skills:
        _append_unique(risks, "Some target job skills are missing from the resume.")
        _append_unique(priority_actions, "Add missing target skills only if they reflect your real experience.")
    if high_risk_count or moderate_risk_count:
        _append_unique(risks, "Several sentences may sound generic, vague, or AI-like.")
        _append_unique(priority_actions, "Rewrite generic bullets using Action Verb + Task + Tool/Method + Result/Impact.")
    if model_confidence and model_confidence < 45:
        _append_unique(risks, "Model confidence is low, so the predicted role should be interpreted carefully.")
    if template_severity in {"strong", "partial"}:
        _append_unique(risks, "Template or placeholder content may reduce analysis quality.")
        _append_unique(priority_actions, "Replace placeholders with real resume details.")
    if ats_score < 65:
        _append_unique(risks, "ATS compatibility may need stronger structure, keywords, or measurable evidence.")
        _append_unique(priority_actions, "Add measurable outcomes where truthful.")
    if jd_match_score < 50 and matched_skills:
        _append_unique(priority_actions, "Tailor project descriptions to the target role.")
    if rewrite_suggestions:
        _append_unique(priority_actions, "Use the rewrite templates as drafts, then replace placeholders with real information.")
    if not priority_actions:
        _append_unique(priority_actions, "Review the resume for truthful role-specific details and measurable impact.")

    readiness_level = _build_readiness_level(
        ats_score=ats_score,
        jd_match_score=jd_match_score,
        high_risk_count=high_risk_count,
        missing_count=len(missing_skills),
        template_severity=template_severity,
    )
    overall_readiness = readiness_level
    overall_summary = (
        f"ResumeIQ estimates this resume as {readiness_level.lower()} for the current target role. "
        f"The report combines an estimated ATS score of {_format_percent(ats_score)}, "
        f"a job-match score of {_format_percent(jd_match_score)}, writing-quality signals, "
        "rewrite opportunities, and parser quality checks."
    )

    rewrite_patterns = [
        safe_get(item, "pattern", "default")
        for item in rewrite_suggestions
        if isinstance(item, dict)
    ]
    top_rewrite_patterns = [pattern for pattern, _ in Counter(rewrite_patterns).most_common(3)]

    return {
        "overall_summary": overall_summary,
        "overall_readiness": overall_readiness,
        "readiness_level": readiness_level,
        "strengths": strengths[:6],
        "risks": risks[:6],
        "priority_actions": priority_actions[:7],
        "ats_feedback": {
            "score": round(ats_score, 1),
            "grade": ats_grade,
            "message": safe_get(ats_result, "feedback", ""),
        },
        "job_match_feedback": {
            "match_percentage": round(jd_match_score, 1),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "extra_resume_skills": extra_skills,
        },
        "writing_quality_feedback": {
            "total_flagged_sentences": len(flagged_sentences),
            "high_risk_count": high_risk_count,
            "moderate_risk_count": moderate_risk_count,
            "message": safe_get(sentence_quality_result, "summary", ""),
        },
        "rewrite_feedback": {
            "total_suggestions": len(rewrite_suggestions),
            "top_patterns": top_rewrite_patterns,
        },
        "parser_quality_feedback": {
            "template_severity": template_severity,
            "template_score": safe_get(template_detection, "template_score", 0),
            "warning": safe_get(template_detection, "warning", ""),
        },
        "prediction_feedback": {
            "predicted_role": predicted_role,
            "model_confidence": round(model_confidence, 1),
        },
        "disclaimer": REPORT_DISCLAIMER,
    }


def get_priority_actions(report: dict, max_actions: int = 5) -> list[str]:
    actions = _list_value(safe_get(report, "priority_actions", []))
    return actions[: max(0, int(max_actions or 0))]


def get_report_summary_cards(report: dict) -> list[dict]:
    priority_actions = _list_value(safe_get(report, "priority_actions", []))
    risks = _list_value(safe_get(report, "risks", []))
    readiness = safe_get(report, "overall_readiness", "Not available")
    ats_feedback = safe_get(report, "ats_feedback", {}) or {}
    job_match_feedback = safe_get(report, "job_match_feedback", {}) or {}

    return [
        {
            "title": "Overall Readiness",
            "value": readiness,
            "helper_text": "Rule-based summary of current resume readiness.",
        },
        {
            "title": "Priority Actions",
            "value": str(len(priority_actions)),
            "helper_text": "Recommended next steps from the report.",
        },
        {
            "title": "Key Risks",
            "value": str(len(risks)),
            "helper_text": "Main issues to review before applying.",
        },
        {
            "title": "ATS / JD Match",
            "value": f"{round(normalize_score(safe_get(ats_feedback, 'score', 0)))}% / {round(normalize_score(safe_get(job_match_feedback, 'match_percentage', 0)))}%",
            "helper_text": "Estimated ATS compatibility and job match.",
        },
    ]
