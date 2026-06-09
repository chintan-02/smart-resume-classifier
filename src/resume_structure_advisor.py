import re


RECOMMENDED_SECTION_ORDER = [
    "Contact Information",
    "Professional Summary",
    "Technical Skills",
    "Work Experience",
    "Projects",
    "Education",
    "Certifications",
]

RECOMMENDED_BULLET_FORMULA = "Action Verb + Task + Tool/Method + Result/Impact"

STRUCTURE_DISCLAIMER = (
    "This advisor uses local, rule-based checks to suggest resume structure and formatting improvements. "
    "It does not guarantee ATS performance, job success, or hiring outcomes."
)

ACTION_VERBS = {
    "analyzed",
    "automated",
    "built",
    "created",
    "delivered",
    "designed",
    "developed",
    "engineered",
    "implemented",
    "improved",
    "increased",
    "led",
    "optimized",
    "reduced",
    "streamlined",
    "supported",
}

SECTION_ALIASES = {
    "contact": "contact",
    "contact information": "contact",
    "professional summary": "summary",
    "summary": "summary",
    "objective": "summary",
    "technical skills": "skills",
    "skills": "skills",
    "work experience": "experience",
    "professional experience": "experience",
    "experience": "experience",
    "projects": "projects",
    "project experience": "projects",
    "education": "education",
    "certification": "certifications",
    "certifications": "certifications",
}


def safe_get(data, key, default=None):
    if not isinstance(data, dict):
        return default
    return data.get(key, default)


def _has_content(value) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return value is not None


def normalize_sections(parser_result=None) -> dict:
    source_sections = safe_get(parser_result, "sections")
    if source_sections is None:
        source_sections = safe_get(parser_result, "detected_sections", {})
    if not isinstance(source_sections, dict):
        source_sections = {}

    normalized = {}
    for raw_name, content in source_sections.items():
        cleaned_name = re.sub(r"[^a-z0-9\s]", "", str(raw_name).lower()).strip()
        normalized_name = SECTION_ALIASES.get(cleaned_name, cleaned_name.replace(" ", "_"))
        normalized[normalized_name] = content

    contact_info = safe_get(parser_result, "contact_info", {})
    if isinstance(contact_info, dict) and any(contact_info.values()):
        normalized["contact"] = contact_info

    return normalized


def _finding(issue, severity, why_it_matters, recommendation):
    return {
        "issue": issue,
        "severity": severity,
        "why_it_matters": why_it_matters,
        "recommendation": recommendation,
    }


def analyze_missing_sections(sections: dict) -> list[dict]:
    findings = []
    has_contact = _has_content(safe_get(sections, "contact"))
    has_skills = _has_content(safe_get(sections, "skills"))
    has_experience = _has_content(safe_get(sections, "experience"))
    has_projects = _has_content(safe_get(sections, "projects"))
    has_education = _has_content(safe_get(sections, "education"))
    has_summary = _has_content(safe_get(sections, "summary"))
    has_certifications = _has_content(safe_get(sections, "certifications"))

    if not has_contact:
        findings.append(
            _finding(
                "Missing Contact Information section",
                "high",
                "Recruiters need a clear way to identify and contact the candidate.",
                "Add name, email, phone, LinkedIn/GitHub, or portfolio details where appropriate.",
            )
        )
    if not has_skills:
        findings.append(
            _finding(
                "Missing Technical Skills section",
                "high",
                "A skills section helps recruiters and screening tools quickly understand relevant capabilities.",
                "Add a concise skills section grouped by tools, languages, frameworks, and methods.",
            )
        )
    if not has_experience and not has_projects:
        findings.append(
            _finding(
                "Missing Experience or Projects section",
                "high",
                "Experience or projects show applied ability instead of only listing skills.",
                "Add work experience or 1-3 relevant projects with tools, methods, and truthful outcomes.",
            )
        )
    if not has_education:
        findings.append(
            _finding(
                "Missing Education section",
                "medium",
                "Education helps provide background context, especially for students and early-career candidates.",
                "Add relevant education, training, or credentials.",
            )
        )
    if not has_summary:
        findings.append(
            _finding(
                "Missing Professional Summary section",
                "low",
                "A short summary can help frame the resume for the target role.",
                "Add 2-3 lines summarizing role focus, core skills, and target impact.",
            )
        )
    if not has_projects:
        findings.append(
            _finding(
                "Missing Projects section",
                "medium",
                "Projects help demonstrate applied technical ability, especially for students and early-career candidates.",
                "Add 1-3 relevant projects with tools, methods, and measurable outcomes where truthful.",
            )
        )
    if not has_certifications:
        findings.append(
            _finding(
                "Certifications section not detected",
                "low",
                "Certifications can support specialized tools or domains when they are relevant.",
                "Add certifications only if they are real and relevant to the target role.",
            )
        )

    return findings


def analyze_section_order(sections: dict) -> list[dict]:
    detected_order = [name for name, content in (sections or {}).items() if _has_content(content)]
    if len(detected_order) < 3:
        return [
            _finding(
                "Section order is hard to evaluate",
                "low",
                "The parser detected too few sections to confidently judge ordering.",
                "Use a clear order: Contact, Summary, Skills, Experience, Projects, Education, Certifications.",
            )
        ]

    recommended_positions = {
        "contact": 0,
        "summary": 1,
        "skills": 2,
        "experience": 3,
        "projects": 4,
        "education": 5,
        "certifications": 6,
    }
    numeric_order = [
        recommended_positions[name]
        for name in detected_order
        if name in recommended_positions
    ]
    if numeric_order and numeric_order != sorted(numeric_order):
        return [
            _finding(
                "Section order may be harder to scan",
                "low",
                "Recruiters usually scan resumes faster when common sections appear in a predictable order.",
                "Use the suggested section order: Contact, Summary, Skills, Experience, Projects, Education, Certifications.",
            )
        ]
    return []


def _bullet_lines(resume_text: str) -> list[str]:
    return [
        line.strip()
        for line in (resume_text or "").splitlines()
        if re.match(r"^\s*(?:[-*•]|\d+[.)])\s+", line)
    ]


def _content_lines(resume_text: str) -> list[str]:
    return [line.strip() for line in (resume_text or "").splitlines() if line.strip()]


def analyze_bullet_quality(resume_text: str) -> list[dict]:
    findings = []
    text = resume_text or ""
    lines = _content_lines(text)
    bullets = _bullet_lines(text)
    paragraphs = [line for line in lines if len(line.split()) >= 35]

    if len(bullets) < 3:
        findings.append(
            _finding(
                "Few resume bullets detected",
                "medium",
                "Recruiters scan bullets quickly, so bullets can make impact easier to see.",
                f"Use concise bullets with this formula: {RECOMMENDED_BULLET_FORMULA}.",
            )
        )
    if len(paragraphs) >= 3:
        findings.append(
            _finding(
                "Resume may be paragraph-heavy",
                "medium",
                "Long paragraphs can make important accomplishments harder to scan.",
                "Break dense paragraphs into concise bullets focused on actions, methods, and results.",
            )
        )

    if bullets:
        action_bullet_count = sum(
            1
            for bullet in bullets
            if re.search(rf"\b({'|'.join(sorted(ACTION_VERBS))})\b", bullet, flags=re.IGNORECASE)
        )
        metric_bullet_count = sum(1 for bullet in bullets if re.search(r"\b\d+(?:\.\d+)?\s*%?|\[[^\]]+\]", bullet))
        generic_bullet_count = sum(
            1
            for bullet in bullets
            if re.search(r"\b(responsible for|worked on|helped with|various tasks|team player)\b", bullet, flags=re.IGNORECASE)
        )

        if action_bullet_count < max(1, len(bullets) // 2):
            findings.append(
                _finding(
                    "Bullets need stronger action-result structure",
                    "medium",
                    "Recruiters scan bullets quickly, so each bullet should show what you did, how you did it, and why it mattered.",
                    f"Rewrite bullets using: {RECOMMENDED_BULLET_FORMULA}.",
                )
            )
        if metric_bullet_count == 0:
            findings.append(
                _finding(
                    "Bullets may be missing measurable impact",
                    "medium",
                    "Numbers, scale, frequency, or outcome details make accomplishments easier to understand.",
                    "Add measurable outcomes where truthful, such as [add measurable result].",
                )
            )
        if generic_bullet_count:
            findings.append(
                _finding(
                    "Some bullets may sound generic",
                    "medium",
                    "Generic bullets can make real work sound less specific than it is.",
                    "Replace generic wording with specific tasks, tools, methods, and impact.",
                )
            )

    return findings


def analyze_template_or_placeholder_risk(parser_result=None) -> list[dict]:
    template_detection = safe_get(parser_result, "template_detection", {}) or {}
    template_warning = safe_get(parser_result, "template_warning") or safe_get(parser_result, "placeholder_warning")
    severity = safe_get(template_detection, "severity", "none")
    warning = safe_get(template_detection, "warning", "") or template_warning

    if severity == "strong":
        return [
            _finding(
                "Strong template or placeholder risk detected",
                "high",
                "Placeholder text may reduce analysis quality and make the resume look incomplete.",
                "Replace placeholders with real resume details before relying on the report.",
            )
        ]
    if severity == "partial" or warning:
        return [
            _finding(
                "Some template or placeholder content may remain",
                "medium",
                "Placeholder text can make resume sections less credible and harder to evaluate.",
                "Review the resume and replace placeholders with real details.",
            )
        ]
    return []


def build_structure_advice(parser_result=None, resume_text: str = "") -> dict:
    sections = normalize_sections(parser_result)
    findings = []
    findings.extend(analyze_missing_sections(sections))
    findings.extend(analyze_section_order(sections))
    findings.extend(analyze_bullet_quality(resume_text))
    findings.extend(analyze_template_or_placeholder_risk(parser_result))

    severity_counts = {
        "high": sum(1 for finding in findings if finding.get("severity") == "high"),
        "medium": sum(1 for finding in findings if finding.get("severity") == "medium"),
        "low": sum(1 for finding in findings if finding.get("severity") == "low"),
    }
    required_sections_present = all(
        [
            _has_content(safe_get(sections, "contact")),
            _has_content(safe_get(sections, "skills")),
            _has_content(safe_get(sections, "education")),
            _has_content(safe_get(sections, "experience")) or _has_content(safe_get(sections, "projects")),
        ]
    )

    if severity_counts["high"] >= 2 or not sections:
        grade = "High Priority Fixes Needed"
    elif severity_counts["high"] or severity_counts["medium"] >= 3:
        grade = "Needs Improvement"
    elif required_sections_present and severity_counts["medium"] <= 1:
        grade = "Strong"
    else:
        grade = "Good"

    if grade == "Strong":
        overall_message = "The resume structure looks recruiter-friendly, with only minor formatting checks recommended."
    elif grade == "Good":
        overall_message = "Most core structure signals are present, with a few formatting improvements recommended."
    elif grade == "Needs Improvement":
        overall_message = "The resume may improve recruiter readability by strengthening sections, bullets, or formatting."
    else:
        overall_message = "Several structure or formatting issues should be reviewed before applying."

    priority_fixes = [
        finding["recommendation"]
        for finding in findings
        if finding.get("severity") in {"high", "medium"}
    ][:5]
    if not priority_fixes:
        priority_fixes = ["Review section labels and bullets for clarity before applying."]

    return {
        "overall_structure_grade": grade,
        "overall_message": overall_message,
        "findings": findings,
        "recommended_section_order": RECOMMENDED_SECTION_ORDER,
        "recommended_bullet_formula": RECOMMENDED_BULLET_FORMULA,
        "example_before_after": {
            "before": "Responsible for data analysis.",
            "after": "Analyzed [project/process] using [tool/library] to identify [insight], supporting [business impact].",
        },
        "priority_fixes": priority_fixes,
        "disclaimer": STRUCTURE_DISCLAIMER,
    }


def get_structure_summary_cards(advice: dict) -> list[dict]:
    findings = safe_get(advice, "findings", []) or []
    priority_fixes = safe_get(advice, "priority_fixes", []) or []
    grade = safe_get(advice, "overall_structure_grade", "Not available")

    return [
        {
            "title": "Structure Grade",
            "value": grade,
            "helper_text": "Rule-based review of sections and formatting.",
        },
        {
            "title": "Findings",
            "value": str(len(findings)),
            "helper_text": "Structure and formatting items to review.",
        },
        {
            "title": "Priority Fixes",
            "value": str(len(priority_fixes)),
            "helper_text": "Recommended changes before applying.",
        },
    ]
