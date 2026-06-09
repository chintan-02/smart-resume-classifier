import re


CANDIDATE_FIT_DISCLAIMER = (
    "This is a local, explainable ResumeIQ fit estimate based on available resume and "
    "job-description content. It is a decision-support recommendation only, not an official "
    "ATS score, hiring decision, or guarantee of job success."
)


def safe_get(data, key, default=None):
    if not isinstance(data, dict):
        return default
    return data.get(key, default)


def normalize_score(value, default=0.0) -> float:
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


def _append_unique(items: list, value: str) -> None:
    if value and value not in items:
        items.append(value)


def _score_label(score: float) -> str:
    if score >= 80:
        return "Strong"
    if score >= 65:
        return "Good"
    if score >= 45:
        return "Partial"
    return "Needs Improvement"


def _skill_score_label(score: float) -> str:
    if score >= 75:
        return "Strong"
    if score >= 60:
        return "Good"
    if score >= 40:
        return "Partial"
    return "Needs Improvement"


def calculate_skill_score(jd_match_result=None, skill_taxonomy_result=None) -> dict:
    jd_match_result = jd_match_result if isinstance(jd_match_result, dict) else {}
    skill_taxonomy_result = skill_taxonomy_result if isinstance(skill_taxonomy_result, dict) else {}
    gap = safe_get(jd_match_result, "gap", {}) or {}

    matched_skills = _as_list(safe_get(gap, "matched", safe_get(jd_match_result, "matched_skills", [])))
    missing_skills = _as_list(safe_get(gap, "missing", safe_get(jd_match_result, "missing_skills", [])))
    top_gap_categories = _as_list(safe_get(skill_taxonomy_result, "top_gap_categories", []))
    category_summary = _as_list(safe_get(skill_taxonomy_result, "category_summary", []))
    category_gap_count = len(top_gap_categories) or sum(
        1
        for item in category_summary
        if isinstance(item, dict) and safe_get(item, "missing_count", 0) > 0
    )

    matched_count = len(matched_skills)
    missing_count = len(missing_skills)

    raw_match_score = safe_get(jd_match_result, "match_score")
    match_score = normalize_score(raw_match_score, 0)
    if raw_match_score is None and (matched_skills or missing_skills):
        total_target_skills = len(matched_skills) + len(missing_skills)
        match_score = (len(matched_skills) / total_target_skills) * 100 if total_target_skills else 0

    score = match_score
    score -= min(missing_count, 12) * 0.8
    score -= min(category_gap_count, 5) * 2.0
    if matched_skills:
        score += min(matched_count, 8) * 1.2

    if matched_count >= 10:
        score = max(score, 45)
    elif matched_count >= 5:
        score = max(score, 30)
    elif matched_count >= 3:
        score = max(score, 20)

    score = normalize_score(score)

    signals = []
    risks = []
    if matched_skills:
        _append_unique(signals, f"{len(matched_skills)} target skills were detected in both the resume and job description.")
    if score >= 65:
        _append_unique(signals, "Skill alignment shows good fit signals based on available content.")
    if missing_skills:
        _append_unique(risks, f"{len(missing_skills)} target skills were not detected in the resume.")
    if top_gap_categories:
        _append_unique(risks, "Category-level gaps detected in " + ", ".join(top_gap_categories[:3]) + ".")
    if not signals:
        _append_unique(signals, "Skill alignment can be estimated after resume and job-description skills are detected.")

    return {
        "score": round(score, 1),
        "label": _skill_score_label(score),
        "signals": signals[:4],
        "risks": risks[:4],
    }


def calculate_resume_quality_score(
    sentence_quality_result=None,
    rewrite_suggestions=None,
    structure_advice=None,
    parser_result=None,
) -> dict:
    sentence_quality_result = sentence_quality_result if isinstance(sentence_quality_result, dict) else {}
    structure_advice = structure_advice if isinstance(structure_advice, dict) else {}
    parser_result = parser_result if isinstance(parser_result, dict) else {}
    rewrite_suggestions = _as_list(rewrite_suggestions)

    template_detection = safe_get(parser_result, "template_detection", {}) or {}
    template_severity = safe_get(template_detection, "severity", "none")
    high_risk_count = int(normalize_score(safe_get(sentence_quality_result, "high_risk_count", 0)))
    moderate_risk_count = int(normalize_score(safe_get(sentence_quality_result, "moderate_risk_count", 0)))
    structure_grade = safe_get(structure_advice, "overall_structure_grade", "")

    score = 85.0
    if template_severity == "strong":
        score -= 30
    elif template_severity == "partial":
        score -= 15
    score -= min(high_risk_count, 6) * 6
    score -= min(moderate_risk_count, 8) * 2.5
    score -= min(len(rewrite_suggestions), 8) * 1.5
    if structure_grade == "High Priority Fixes Needed":
        score -= 20
    elif structure_grade == "Needs Improvement":
        score -= 12
    score = normalize_score(score)

    signals = []
    risks = []
    if not high_risk_count and not moderate_risk_count:
        _append_unique(signals, "No major generic or AI-like writing issues were detected.")
    if structure_grade and structure_grade not in {"Needs Improvement", "High Priority Fixes Needed"}:
        _append_unique(signals, f"Resume structure is currently rated {structure_grade}.")
    if high_risk_count:
        _append_unique(risks, f"{high_risk_count} high-risk writing findings may need humanized rewrites.")
    if moderate_risk_count:
        _append_unique(risks, f"{moderate_risk_count} moderate writing findings may need more detail.")
    if rewrite_suggestions:
        _append_unique(risks, f"{len(rewrite_suggestions)} rewrite suggestions are available for review.")
    if template_severity in {"strong", "partial"}:
        _append_unique(risks, "Template or placeholder content may reduce resume quality.")
    if not signals:
        _append_unique(signals, "Resume quality was estimated from writing, structure, and parser signals.")

    return {
        "score": round(score, 1),
        "label": _score_label(score),
        "signals": signals[:4],
        "risks": risks[:4],
    }


def calculate_experience_project_score(parser_result=None, resume_text: str = "") -> dict:
    parser_result = parser_result if isinstance(parser_result, dict) else {}
    sections = safe_get(parser_result, "sections", {}) or {}
    text = resume_text or ""

    years = safe_get(parser_result, "estimated_years_experience")
    experience = safe_get(parser_result, "experience") or safe_get(sections, "experience")
    projects = safe_get(parser_result, "projects") or safe_get(sections, "projects")
    certifications = safe_get(parser_result, "certifications") or safe_get(sections, "certifications")

    has_experience = bool(experience)
    has_projects = bool(projects)
    has_certifications = bool(certifications)
    measurable_patterns = [
        r"\b\d+(?:\.\d+)?\s*%",
        r"\$\s?\d+",
        r"\b\d+(?:\.\d+)?\s*(?:k|m|million|thousand|\+)\b",
        r"\b(improved|reduced|increased|built|developed|deployed|automated|optimized|delivered|launched)\b",
    ]
    measurable_signal_count = sum(
        1 for pattern in measurable_patterns if re.search(pattern, text, flags=re.IGNORECASE)
    )

    score = 35.0
    if has_experience:
        score += 25
    if has_projects:
        score += 20
    if has_certifications:
        score += 5
    if isinstance(years, (int, float)) and years > 0:
        score += min(float(years), 5) * 2
    if measurable_signal_count:
        score += min(measurable_signal_count, 4) * 5
    score = normalize_score(score)

    signals = []
    risks = []
    if has_experience:
        _append_unique(signals, "Experience evidence was detected in the resume.")
    if has_projects:
        _append_unique(signals, "Project evidence was detected in the resume.")
    if measurable_signal_count:
        _append_unique(signals, "Measurable or action-oriented impact signals were found.")
    if not has_experience and not has_projects:
        _append_unique(risks, "Experience or project evidence was not clearly detected.")
    if not measurable_signal_count:
        _append_unique(risks, "Resume bullets may need more truthful measurable outcomes or impact signals.")
    if not signals:
        _append_unique(signals, "Experience and project evidence was estimated from parser and resume-text signals.")

    return {
        "score": round(score, 1),
        "label": _score_label(score),
        "signals": signals[:4],
        "risks": risks[:4],
    }


def calculate_model_signal_score(prediction_result=None) -> dict:
    prediction_result = prediction_result if isinstance(prediction_result, dict) else {}
    confidence = safe_get(prediction_result, "confidence")
    if confidence is None:
        confidence = safe_get(prediction_result, "confidence_display")

    if confidence is None:
        score = 50.0
    else:
        score = normalize_score(confidence, default=50)

    signals = []
    risks = []
    if confidence is None:
        _append_unique(signals, "Model confidence is unavailable, so this component stays neutral.")
    else:
        _append_unique(signals, "Classifier confidence is used as a weak supporting signal.")
    if score < 35:
        _append_unique(risks, "Model confidence is low, so the predicted role should be interpreted carefully.")

    return {
        "score": round(score, 1),
        "label": _score_label(score),
        "signals": signals[:4],
        "risks": risks[:4],
    }


def _fit_label(score: float) -> str:
    if score >= 80:
        return "Strong Fit"
    if score >= 65:
        return "Good Fit"
    if score >= 45:
        return "Partial Fit"
    return "Needs Improvement"


def _recommendation_for_label(label: str) -> str:
    if label in {"Strong Fit", "Good Fit"}:
        return "Recommended for review"
    if label == "Partial Fit":
        return "Review after targeted resume improvements"
    return "Needs targeted resume improvement before applying"


def _component(name: str, score: float, weight: float, label: str, reason: str) -> dict:
    return {
        "component": name,
        "score": round(normalize_score(score), 1),
        "weight": weight,
        "label": label,
        "reason": reason,
    }


def build_candidate_fit_score(
    prediction_result=None,
    ats_result=None,
    jd_match_result=None,
    semantic_result=None,
    skill_taxonomy_result=None,
    sentence_quality_result=None,
    rewrite_suggestions=None,
    structure_advice=None,
    parser_result=None,
    resume_text: str = "",
) -> dict:
    ats_result = ats_result if isinstance(ats_result, dict) else {}
    semantic_result = semantic_result if isinstance(semantic_result, dict) else {}

    semantic_available = (
        bool(safe_get(semantic_result, "available"))
        and safe_get(semantic_result, "semantic_score") is not None
    )
    weights = {
        "Semantic Match": 0.25,
        "Skill Alignment": 0.25,
        "ATS Compatibility": 0.20,
        "Resume Quality": 0.15,
        "Experience / Project Evidence": 0.10,
        "Model Confidence Signal": 0.05,
    }
    if not semantic_available:
        weights = {
            "Skill Alignment": 0.35,
            "ATS Compatibility": 0.25,
            "Resume Quality": 0.20,
            "Experience / Project Evidence": 0.15,
            "Model Confidence Signal": 0.05,
        }

    skill_score = calculate_skill_score(jd_match_result, skill_taxonomy_result)
    quality_score = calculate_resume_quality_score(
        sentence_quality_result=sentence_quality_result,
        rewrite_suggestions=rewrite_suggestions,
        structure_advice=structure_advice,
        parser_result=parser_result,
    )
    experience_score = calculate_experience_project_score(parser_result=parser_result, resume_text=resume_text)
    model_score = calculate_model_signal_score(prediction_result)

    component_scores = []
    if semantic_available:
        semantic_score = normalize_score(safe_get(semantic_result, "semantic_score", 0))
        component_scores.append(
            _component(
                "Semantic Match",
                semantic_score,
                weights["Semantic Match"],
                safe_get(semantic_result, "similarity_label", _score_label(semantic_score)),
                "Meaning-based alignment between resume and JD.",
            )
        )

    ats_score = normalize_score(safe_get(ats_result, "ats_score", 0))
    component_scores.extend(
        [
            _component(
                "Skill Alignment",
                skill_score["score"],
                weights["Skill Alignment"],
                skill_score["label"],
                "Detected target-skill overlap and category-level gaps.",
            ),
            _component(
                "ATS Compatibility",
                ats_score,
                weights["ATS Compatibility"],
                safe_get(ats_result, "grade", _score_label(ats_score)),
                "Estimated resume structure, keywords, and JD alignment.",
            ),
            _component(
                "Resume Quality",
                quality_score["score"],
                weights["Resume Quality"],
                quality_score["label"],
                "Writing, structure, rewrite, and placeholder signals.",
            ),
            _component(
                "Experience / Project Evidence",
                experience_score["score"],
                weights["Experience / Project Evidence"],
                experience_score["label"],
                "Evidence from experience, projects, certifications, and measurable impact.",
            ),
            _component(
                "Model Confidence Signal",
                model_score["score"],
                weights["Model Confidence Signal"],
                model_score["label"],
                "Classifier confidence used only as a weak supporting signal.",
            ),
        ]
    )

    overall_fit_score = sum(item["score"] * item["weight"] for item in component_scores)
    fit_label = _fit_label(overall_fit_score)
    recommendation = _recommendation_for_label(fit_label)

    strength_signals = []
    risk_signals = []
    priority_actions = []
    for result in (skill_score, quality_score, experience_score, model_score):
        for signal in result.get("signals", []):
            _append_unique(strength_signals, signal)
        for risk in result.get("risks", []):
            _append_unique(risk_signals, risk)

    if semantic_available and normalize_score(safe_get(semantic_result, "semantic_score", 0)) >= 65:
        _append_unique(strength_signals, "Semantic matching shows good meaning-based alignment with the job description.")
    elif semantic_available:
        _append_unique(risk_signals, "Semantic coverage may be weak for some job-description requirements.")
        _append_unique(priority_actions, "Improve semantic coverage for weak JD requirements if relevant.")
    else:
        _append_unique(risk_signals, "Semantic matching was unavailable, so the score used redistributed local weights.")

    if skill_score["risks"]:
        _append_unique(priority_actions, "Add missing target skills only if they reflect your real experience.")
    if experience_score["risks"]:
        _append_unique(priority_actions, "Strengthen project or experience bullets with truthful measurable outcomes.")
    if quality_score["risks"]:
        _append_unique(priority_actions, "Rewrite generic bullets using Action Verb + Task + Tool/Method + Result/Impact.")
    if model_score["risks"]:
        _append_unique(priority_actions, "Treat low model confidence carefully and rely on combined fit signals.")
    if not priority_actions:
        _append_unique(priority_actions, "Review the resume for truthful role-specific details before applying.")

    summary = (
        f"ResumeIQ estimates a {round(overall_fit_score)}% multi-score candidate fit. "
        f"This combines {len(component_scores)} local signals based on available resume and "
        "job-description content."
    )

    return {
        "overall_fit_score": round(overall_fit_score, 1),
        "fit_label": fit_label,
        "recommendation": recommendation,
        "summary": summary,
        "component_scores": component_scores,
        "strength_signals": strength_signals[:7],
        "risk_signals": risk_signals[:7],
        "priority_actions": priority_actions[:7],
        "disclaimer": CANDIDATE_FIT_DISCLAIMER,
    }


def get_candidate_fit_summary_cards(candidate_fit_result: dict) -> list[dict]:
    score = normalize_score(safe_get(candidate_fit_result, "overall_fit_score", 0))
    return [
        {
            "title": "Overall Fit Score",
            "value": f"{round(score)}%",
            "helper_text": "Weighted local fit estimate.",
        },
        {
            "title": "Fit Label",
            "value": safe_get(candidate_fit_result, "fit_label", "Not available"),
            "helper_text": "Based on multiple resume/JD signals.",
        },
        {
            "title": "Recommendation",
            "value": safe_get(candidate_fit_result, "recommendation", "Not available"),
            "helper_text": "Decision-support recommendation only.",
        },
    ]
