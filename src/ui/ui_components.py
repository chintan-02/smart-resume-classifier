from html import escape

import streamlit as st


def _safe_text(value) -> str:
    if value is None:
        return "N/A"
    return escape(str(value))


def _format_score(score) -> str:
    if score is None:
        return "N/A"
    if isinstance(score, (int, float)):
        return f"{score:.0f}%" if float(score).is_integer() else f"{score:.1f}%"
    text = str(score).strip()
    return text if text else "N/A"


def render_hero() -> None:
    badges = [
        "ATS Compatibility Estimate",
        "Skill Gap Analysis",
        "Writing Quality Review",
        "Rewrite Suggestions",
        "Job Matching",
        "Decision-Support Signals",
    ]
    badge_markup = "".join(f'<span class="hero-chip">{escape(badge)}</span>' for badge in badges)
    st.markdown(
        f"""
        <div class="resumeiq-hero">
            <div class="resumeiq-kicker">Resume Intelligence Dashboard</div>
            <h1 class="resumeiq-title">ResumeIQ</h1>
            <div class="resumeiq-subtitle">AI Resume Intelligence &amp; Job Application Assistant</div>
            <div class="resumeiq-description">
                Analyze resumes, compare against job descriptions, review candidate fit, and prepare
                recruiter-ready insights using privacy-aware decision-support workflows.
            </div>
            <div class="badge-row">{badge_markup}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(primary_analysis_badge: str = "Local analysis currently active") -> None:
    badges = [
        primary_analysis_badge,
        "Decision-support signal",
        "Recruiter-ready insights",
        "Privacy-safe mode available",
    ]
    badge_markup = "".join(f'<span class="hero-chip">{escape(badge)}</span>' for badge in badges)
    st.markdown(
        f"""
        <div class="resumeiq-hero">
            <div class="resumeiq-kicker">Resume Intelligence Dashboard</div>
            <h1 class="resumeiq-title">ResumeIQ</h1>
            <div class="resumeiq-subtitle">AI Resume Intelligence &amp; Job Application Assistant</div>
            <div class="resumeiq-description">
                Analyze resumes, compare against job descriptions, review candidate fit, and prepare
                recruiter-ready insights using local decision-support workflows.
            </div>
            <div class="badge-row">{badge_markup}</div>
            <div class="hero-disclaimer">Decision-support tool. Human review required.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(title, value, helper_text=None) -> None:
    helper_markup = f'<div class="metric-subtext">{_safe_text(helper_text)}</div>' if helper_text else ""
    card_markup = (
        '<div class="metric-card">'
        f'<div class="metric-label">{_safe_text(title)}</div>'
        f'<div class="metric-value">{_safe_text(value)}</div>'
        f"{helper_markup}"
        "</div>"
    )
    st.markdown(card_markup, unsafe_allow_html=True)


def render_alert_banner(message, tone="info") -> None:
    tone_class = {
        "info": "alert-info",
        "success": "alert-success",
        "warning": "alert-warning",
        "danger": "alert-danger",
    }.get(str(tone).lower(), "alert-info")
    st.markdown(
        f'<div class="alert-banner {tone_class}">{_safe_text(message)}</div>',
        unsafe_allow_html=True,
    )


def render_section_title(title, subtitle=None) -> None:
    subtitle_markup = f'<div class="section-subtitle">{_safe_text(subtitle)}</div>' if subtitle else ""
    st.markdown(
        f"""
        <div>
            <div class="section-title">{_safe_text(title)}</div>
            {subtitle_markup}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_score_summary(label, score, grade=None, helper_text=None) -> None:
    grade_markup = f'<div class="score-grade">{_safe_text(grade)}</div>' if grade else ""
    helper_markup = f'<div class="score-helper">{_safe_text(helper_text)}</div>' if helper_text else ""
    card_markup = (
        '<div class="score-card">'
        f'<div class="score-label">{_safe_text(label)}</div>'
        f'<div class="score-value">{_safe_text(_format_score(score))}</div>'
        f"{grade_markup}"
        f"{helper_markup}"
        "</div>"
    )
    st.markdown(card_markup, unsafe_allow_html=True)


def render_badge_group(badges) -> None:
    items = [str(item).strip() for item in (badges or []) if str(item).strip()]
    if not items:
        st.markdown('<span class="subtle">None detected.</span>', unsafe_allow_html=True)
        return

    markup = "".join(f'<span class="ui-badge">{escape(item)}</span>' for item in items)
    st.markdown(f'<div class="badge-row">{markup}</div>', unsafe_allow_html=True)


def render_status_badge(label, is_active: bool, active_text="Ready", inactive_text="Needed") -> None:
    state_class = "status-ready" if is_active else "status-muted"
    state_text = active_text if is_active else inactive_text
    st.markdown(
        f"""
        <div class="status-badge {state_class}">
            <span>{_safe_text(label)}</span>
            <strong>{_safe_text(state_text)}</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_workflow_status(items) -> None:
    for item in items:
        render_status_badge(
            item.get("label", ""),
            bool(item.get("is_active")),
            item.get("active_text", "Ready"),
            item.get("inactive_text", "Needed"),
        )


def render_feature_placeholder_card(title, description) -> None:
    st.markdown(
        f"""
        <div class="feature-placeholder-card">
            <div class="feature-placeholder-title">{_safe_text(title)}</div>
            <div class="feature-placeholder-copy">{_safe_text(description)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_navigation_section_title(title, subtitle=None) -> None:
    subtitle_markup = f'<div class="nav-section-subtitle">{_safe_text(subtitle)}</div>' if subtitle else ""
    st.markdown(
        f"""
        <div class="nav-section-header">
            <div class="nav-section-title">{_safe_text(title)}</div>
            {subtitle_markup}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_disclaimer_box(message) -> None:
    st.markdown(
        f'<div class="disclaimer-box">{_safe_text(message)}</div>',
        unsafe_allow_html=True,
    )


def render_empty_state(title, message) -> None:
    st.markdown(
        f"""
        <div class="empty-state-card">
            <div class="empty-state-title">{_safe_text(title)}</div>
            <div class="empty-state-message">{_safe_text(message)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
