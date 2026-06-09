import re
from collections import Counter
from typing import Any


PLACEHOLDER_REWRITE_TEMPLATES = {
    "responsible_for": {
        "issue": "Responsibility-focused wording",
        "why_weak": "This explains a duty, but it does not show action, method, or impact.",
        "suggested_rewrite": "Analyzed [project/process] using [tool/library] to identify [insight], supporting [business impact].",
        "stronger_resume_version": "Use: Action Verb + Task + Tool/Method + Result/Impact.",
        "rewrite_tip": "Replace responsibilities with measurable actions and outcomes.",
    },
    "worked_on": {
        "issue": "Vague project contribution",
        "why_weak": "This says you were involved, but it does not explain your specific contribution.",
        "suggested_rewrite": "Built or improved [project/process] using [tool/library] to support [stakeholder/user group] with [business impact].",
        "stronger_resume_version": "Use: Built/Improved + Project + Tool/Method + User/Impact.",
        "rewrite_tip": "Clarify what you personally did and what changed because of the work.",
    },
    "helped_with": {
        "issue": "Support wording without clear ownership",
        "why_weak": "This sounds supportive, but it does not show the specific task, skill, or result.",
        "suggested_rewrite": "Supported [stakeholder/user group] by completing [project/process] with [tool/library], improving [business impact].",
        "stronger_resume_version": "Use: Supported + Audience + Action + Tool/Method + Outcome.",
        "rewrite_tip": "Show the concrete work you completed instead of only saying you helped.",
    },
    "generic_results": {
        "issue": "Generic results claim",
        "why_weak": "This claims success, but it does not include evidence, context, or measurable impact.",
        "suggested_rewrite": "Delivered [project/process] by applying [skill/method], resulting in [add measurable result] for [business impact].",
        "stronger_resume_version": "Use: Delivered + Method + Evidence + Impact.",
        "rewrite_tip": "Replace broad claims with a specific example and a real result.",
    },
    "team_player": {
        "issue": "Generic soft-skill wording",
        "why_weak": "This may sound generic because it names a trait without showing how you used it.",
        "suggested_rewrite": "Collaborated with [stakeholder/user group] to complete [project/process], improving [business impact].",
        "stronger_resume_version": "Use: Collaborated + Team/Audience + Work Completed + Result.",
        "rewrite_tip": "Show teamwork through a real collaboration example.",
    },
    "passive_statement": {
        "issue": "Passive or low-ownership wording",
        "why_weak": "This may hide your role and make the bullet feel less action-oriented.",
        "suggested_rewrite": "Led or contributed to [project/process] using [skill/method] to achieve [add measurable result].",
        "stronger_resume_version": "Use: Active Verb + Ownership + Method + Result.",
        "rewrite_tip": "Start with a strong action verb that clearly shows your contribution.",
    },
    "vague_skill": {
        "issue": "Skill listed without proof",
        "why_weak": "This names a skill, but it does not show where or how you used it.",
        "suggested_rewrite": "Applied [skill/method] in [project/process] using [tool/library] to support [business impact].",
        "stronger_resume_version": "Use: Applied + Skill + Project Context + Tool + Impact.",
        "rewrite_tip": "Connect skills to a project, task, or result.",
    },
    "generic_summary": {
        "issue": "Generic summary wording",
        "why_weak": "This may sound broad or reusable across many resumes instead of specific to your experience.",
        "suggested_rewrite": "[Role/level] with experience in [skill/method], [tool/library], and [project/process], focused on [business impact].",
        "stronger_resume_version": "Use: Role + Specific Skills + Domain/Project + Impact Area.",
        "rewrite_tip": "Make summary lines specific to your real tools, projects, and strengths.",
    },
    "default": {
        "issue": "Generic or low-specificity wording",
        "why_weak": "This sentence may need more detail about action, method, and impact.",
        "suggested_rewrite": "Completed [project/process] using [skill/method] and [tool/library] to achieve [add measurable result].",
        "stronger_resume_version": "Use: Action Verb + Work + Method/Tool + Result.",
        "rewrite_tip": "Add truthful details that show what you did, how you did it, and why it mattered.",
    },
}


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


def suggest_rewrite_for_sentence(sentence: str) -> dict:
    original_sentence = _normalize_sentence(sentence)
    pattern = detect_rewrite_pattern(original_sentence)
    template = PLACEHOLDER_REWRITE_TEMPLATES.get(pattern, PLACEHOLDER_REWRITE_TEMPLATES["default"])

    return {
        "original_sentence": original_sentence,
        "pattern": pattern,
        "issue": template["issue"],
        "why_weak": template["why_weak"],
        "suggested_rewrite": template["suggested_rewrite"],
        "stronger_resume_version": template["stronger_resume_version"],
        "rewrite_tip": template["rewrite_tip"],
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
        item.get("pattern", "default")
        for item in items
        if isinstance(item, dict)
    )
    top_patterns = [pattern for pattern, _ in pattern_counts.most_common(3)]

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
