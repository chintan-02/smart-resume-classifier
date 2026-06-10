import re
from collections import Counter
from typing import Any


PLACEHOLDER_REWRITE_TEMPLATES = {
    "responsible_for": {
        "issue_label": "Responsibility wording",
        "explanation": "This explains a duty, but it does not clearly show action, method, or impact.",
        "rewrite_template": "Analyzed [project/process] using [tool/library] to identify [insight], supporting [business impact].",
    },
    "worked_on": {
        "issue_label": "Vague contribution",
        "explanation": "This says you were involved, but it does not explain your specific contribution.",
        "rewrite_template": "Built or improved [project/process] using [tool/library] to support [stakeholder/user group] with [business impact].",
    },
    "helped_with": {
        "issue_label": "Support wording",
        "explanation": "This sounds supportive, but it does not show the specific task, skill, or result.",
        "rewrite_template": "Supported [stakeholder/user group] by completing [project/process] with [tool/library], improving [business impact].",
    },
    "generic_results": {
        "issue_label": "Results claim",
        "explanation": "This claims success, but it does not include enough evidence, context, or measurable impact.",
        "rewrite_template": "Delivered [project/process] by applying [skill/method], resulting in [add truthful result] for [business impact].",
    },
    "team_player": {
        "issue_label": "Generic soft skill",
        "explanation": "This names a trait without showing how you used it in real work.",
        "rewrite_template": "Collaborated with [stakeholder/user group] to complete [project/process], improving [business impact].",
    },
    "passive_statement": {
        "issue_label": "Low ownership",
        "explanation": "This may hide your role and make the bullet feel less action-oriented.",
        "rewrite_template": "Led or contributed to [project/process] using [skill/method] to achieve [truthful result].",
    },
    "vague_skill": {
        "issue_label": "Skill without proof",
        "explanation": "This names a skill, but it does not show where or how you used it.",
        "rewrite_template": "Applied [skill/method] in [project/process] using [tool/library] to support [business impact].",
    },
    "generic_summary": {
        "issue_label": "Generic summary",
        "explanation": "This may sound broad or reusable across many resumes instead of specific to your experience.",
        "rewrite_template": "[Role/level] with experience in [skill/method], [tool/library], and [project/process], focused on [business impact].",
    },
    "default": {
        "issue_label": "Generic wording",
        "explanation": "This sentence may need more detail about action, method, and impact.",
        "rewrite_template": "Completed [project/process] using [skill/method] and [tool/library] to achieve [truthful result].",
    },
}

REWRITE_FORMULA = "Action Verb + Task + Tool/Method + Result/Impact"
SAFETY_NOTE = "Use only truthful details from your real experience."
CUSTOMIZATION_TIPS = [
    "Replace placeholders with truthful project/task details.",
    "Add tools or methods only if you actually used them.",
    "Add measurable results only if you can support them.",
]
CONTEXT_TERMS = [
    "MICE imputation",
    "outlier detection",
    "dashboards",
    "dashboard",
    "classification",
    "Python",
    "SQL",
    "machine learning",
    "API",
    "Streamlit",
    "FastAPI",
    "React",
    "Node",
    "cloud",
    "Docker",
    "Kubernetes",
    "k8s",
]


def _normalize_sentence(sentence: Any) -> str:
    return re.sub(r"\s+", " ", str(sentence or "")).strip()


def detect_rewrite_pattern(sentence: str) -> str:
    text = _normalize_sentence(sentence).lower()

    if not text:
        return "default"
    if re.search(r"\bresponsible\s+for\b", text):
        return "responsible_for"
    if re.search(r"\bworked\s+on\b", text):
        return "worked_on"
    if re.search(r"\b(helped|assisted)\s+with\b", text):
        return "helped_with"
    if any(phrase in text for phrase in ("proven track record", "results-driven", "track record of success")):
        return "generic_results"
    if any(phrase in text for phrase in ("team player", "excellent communication", "good communication")):
        return "team_player"
    if re.search(r"\b(was|were|am|is)\s+(tasked|assigned|involved|required)\b", text):
        return "passive_statement"
    if re.search(r"\b(skilled|proficient|experienced|knowledgeable)\s+(in|with)\b", text):
        return "vague_skill"
    if any(
        phrase in text
        for phrase in (
            "detail-oriented",
            "self-motivated",
            "hardworking",
            "fast learner",
            "passionate professional",
            "dynamic professional",
        )
    ):
        return "generic_summary"
    return "default"


def _extract_context_terms(sentence: str) -> list[str]:
    lowered = sentence.lower()
    terms = []
    for term in CONTEXT_TERMS:
        if term.lower() in lowered:
            terms.append(term)
    return terms


def _join_terms(terms: list[str]) -> str:
    if not terms:
        return ""
    if len(terms) == 1:
        return terms[0]
    if len(terms) == 2:
        return f"{terms[0]} and {terms[1]}"
    return f"{', '.join(terms[:-1])}, and {terms[-1]}"


def _build_contextual_template(sentence: str, pattern: str, fallback_template: str) -> str:
    terms = _extract_context_terms(sentence)
    if not terms:
        return fallback_template

    lowered = sentence.lower()

    if "missing data" in lowered and ("MICE imputation" in terms or "outlier detection" in terms):
        method_text = _join_terms(terms[:3])
        return (
            f"Handled missing data using {method_text} to improve "
            "[data quality/model reliability/analysis accuracy] for [project/dataset]."
        )
    if "dashboard" in lowered or "dashboards" in lowered:
        method_terms = [term for term in terms if term.lower() not in {"dashboard", "dashboards"}]
        method_text = _join_terms(method_terms[:3]) if method_terms else "[tool/method]"
        return (
            f"Built [dashboard/reporting workflow] using {method_text} to help "
            "[stakeholder/user group] monitor [business/process metric]."
        )
    if "classification" in lowered or "machine learning" in lowered:
        method_terms = [term for term in terms if term.lower() not in {"classification", "machine learning"}]
        method_text = _join_terms(method_terms[:3]) if method_terms else "[modeling method/tool]"
        return (
            f"Developed [classification/modeling workflow] using {method_text} to support "
            "[prediction/analysis goal] for [project/dataset]."
        )
    if "api" in lowered or "fastapi" in lowered:
        method_terms = [term for term in terms if term.lower() != "api"]
        method_text = _join_terms(method_terms[:3]) if method_terms else "[tool/method]"
        return (
            f"Built [API/service] using {method_text} to support "
            "[application workflow/user need] with [reliability/performance outcome]."
        )
    if any(term in terms for term in ("Docker", "Kubernetes", "k8s", "cloud")):
        method_text = _join_terms(terms[:3])
        return (
            f"Supported [deployment/workflow] using {method_text} to improve "
            "[release reliability/scalability/operational visibility]."
        )

    method_text = _join_terms(terms[:3])
    return (
        f"Applied {method_text} to complete [project/task] and improve "
        "[business/process/model outcome]."
    )


def suggest_rewrite_for_sentence(sentence: str) -> dict:
    original_sentence = _normalize_sentence(sentence)
    pattern = detect_rewrite_pattern(original_sentence)
    template = PLACEHOLDER_REWRITE_TEMPLATES.get(pattern, PLACEHOLDER_REWRITE_TEMPLATES["default"])
    rewrite_template = _build_contextual_template(
        original_sentence,
        pattern,
        template["rewrite_template"],
    )
    issue_label = template["issue_label"]

    return {
        "issue_type": pattern,
        "issue_label": issue_label,
        "original_sentence": original_sentence,
        "pattern": pattern,
        "issue": issue_label,
        "explanation": template["explanation"],
        "why_weak": template["explanation"],
        "rewrite_formula": REWRITE_FORMULA,
        "rewrite_template": rewrite_template,
        "suggested_rewrite": rewrite_template,
        "customization_tips": CUSTOMIZATION_TIPS,
        "rewrite_tip": "Customize the template with truthful details from your resume or project history.",
        "safety_note": SAFETY_NOTE,
    }


def _extract_sentence_text(item: Any) -> str:
    if isinstance(item, str):
        return _normalize_sentence(item)
    if isinstance(item, dict):
        for key in ("sentence", "text", "original_sentence", "content"):
            value = item.get(key)
            if value:
                return _normalize_sentence(value)
    return ""


def generate_rewrite_suggestions(flagged_sentences, max_suggestions: int = 8) -> list[dict]:
    if not flagged_sentences:
        return []

    suggestions = []
    seen_sentences = set()
    limit = max(0, int(max_suggestions or 0))
    if limit == 0:
        return []

    for item in flagged_sentences:
        if len(suggestions) >= limit:
            break

        sentence = _extract_sentence_text(item)
        if not sentence:
            continue

        normalized_key = sentence.lower()
        if normalized_key in seen_sentences:
            continue

        seen_sentences.add(normalized_key)
        suggestions.append(suggest_rewrite_for_sentence(sentence))

    return suggestions


def get_rewrite_summary(suggestions: list[dict]) -> dict:
    items = suggestions or []
    pattern_counts = Counter(
        item.get("issue_type") or item.get("pattern", "default")
        for item in items
        if isinstance(item, dict)
    )
    top_patterns = [
        PLACEHOLDER_REWRITE_TEMPLATES.get(pattern, PLACEHOLDER_REWRITE_TEMPLATES["default"])["issue_label"]
        for pattern, _ in pattern_counts.most_common(3)
    ]

    if not items:
        priority_message = "No rewrite suggestions yet."
    elif "responsible_for" in pattern_counts or "worked_on" in pattern_counts:
        priority_message = "Focus on replacing generic responsibility statements with action-result bullets."
    elif "vague_skill" in pattern_counts:
        priority_message = "Focus on connecting skills to real projects, tools, and impact."
    elif "team_player" in pattern_counts or "generic_summary" in pattern_counts:
        priority_message = "Focus on replacing broad traits with specific examples from your experience."
    else:
        priority_message = "Focus on adding clear actions, methods, and truthful outcomes."

    return {
        "total_suggestions": len(items),
        "top_patterns": top_patterns,
        "priority_message": priority_message,
    }
