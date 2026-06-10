import re
from collections import Counter
from io import BytesIO

import pandas as pd
import streamlit as st

from src.app_config import (
    APP_INITIAL_SIDEBAR_STATE,
    APP_LAYOUT,
    APP_PAGE_ICON,
    APP_TITLE,
    METRICS_PATH,
    SAMPLE_JD_PATH,
    SKILLS_PATH,
    SUPPORTED_FILE_TYPES,
)
from src.ats_scorer import calculate_ats_score
from src.batch_ranker import (
    build_batch_row,
    convert_rows_to_csv,
    extract_candidate_name,
    get_batch_summary,
    get_batch_summary_cards,
    rank_batch_results,
)
from src.candidate_fit_scorer import build_candidate_fit_score, get_candidate_fit_summary_cards
from src.fairness_dashboard import (
    calculate_fairness_summary,
    get_fairness_intro,
    get_fairness_limitations,
    get_fairness_metric_cards,
    get_fairness_risk_notes,
    get_responsible_ai_checklist,
    get_synthetic_fairness_data,
)
from src.jd_matcher import analyze_job_description_match, get_match_feedback
from src.prediction_service import get_top_predictions as get_model_top_predictions
from src.prediction_service import load_model_artifacts, predict_resume_role
from src.prediction_explainer import build_prediction_explanation, get_prediction_explanation_cards
from src.preprocessing import preprocess_resume_text
from src.privacy_tools import (
    anonymize_batch_rows,
    anonymize_review_records,
    get_privacy_mode_message,
    mask_pii,
)
from src.recruiter_workflow import (
    build_review_records,
    convert_review_records_to_csv,
    get_default_review_status,
    get_review_status_options,
    get_review_summary,
    get_review_summary_cards,
    make_review_key,
)
from src.report_builder import build_resume_improvement_report, get_report_summary_cards
from src.resume_parser import is_supported_file, parse_resume
from src.resume_structure_advisor import build_structure_advice, get_structure_summary_cards
from src.rewrite_suggestions import generate_rewrite_suggestions, get_rewrite_summary
from src.role_profiles import infer_target_role, get_role_profile, get_role_profile_summary
from src.semantic_matcher import build_semantic_match_result, get_semantic_summary_cards
from src.sentence_quality import detect_ai_like_sentences
from src.skill_taxonomy import compare_skill_categories, get_skill_taxonomy_summary
from src.skill_extractor import (
    load_skills,
)
from src.ui.ui_components import (
    render_alert_banner,
    render_badge_group,
    render_disclaimer_box,
    render_empty_state,
    render_feature_placeholder_card,
    render_navigation_section_title,
    render_page_header,
    render_metric_card,
    render_score_summary,
    render_section_title,
    render_workflow_status,
)
from src.ui.ui_styles import apply_global_styles

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_PAGE_ICON,
    layout=APP_LAYOUT,
    initial_sidebar_state=APP_INITIAL_SIDEBAR_STATE,
)

apply_global_styles()


@st.cache_resource
def load_model():
    model, vectorizer = load_model_artifacts()
    return model, vectorizer


@st.cache_data
def get_skills():
    return load_skills(SKILLS_PATH)


@st.cache_data
def get_metrics():
    if METRICS_PATH.exists():
        import json

        return json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    return {}


@st.cache_data
def load_sample_jd() -> str:
    return SAMPLE_JD_PATH.read_text(encoding="utf-8") if SAMPLE_JD_PATH.exists() else ""


def get_top_predictions(text: str, top_n: int = 5) -> pd.DataFrame:
    return get_model_top_predictions(text, model, vectorizer, top_n)


class StoredUploadedFile:
    def __init__(self, name, file_type, data):
        self.name = name
        self.type = file_type
        self._data = data
        self._buffer = BytesIO(data)

    def getvalue(self):
        return self._data

    def read(self, *args, **kwargs):
        return self._buffer.read(*args, **kwargs)

    def seek(self, *args, **kwargs):
        return self._buffer.seek(*args, **kwargs)

    def tell(self):
        return self._buffer.tell()


def ensure_batch_file_store() -> None:
    if "batch_file_store" not in st.session_state:
        st.session_state["batch_file_store"] = []


def store_files_for_batch(files) -> int:
    ensure_batch_file_store()
    stored_names = {item.get("name") for item in st.session_state["batch_file_store"]}
    added_count = 0
    for file in list(files or []):
        file_name = getattr(file, "name", "")
        if not file_name or file_name in stored_names:
            continue
        st.session_state["batch_file_store"].append(
            {
                "name": file_name,
                "type": getattr(file, "type", ""),
                "bytes": file.getvalue(),
            }
        )
        stored_names.add(file_name)
        added_count += 1
    return added_count


def get_candidate_name_from_parser(parser_result) -> str:
    parser_result = parser_result if isinstance(parser_result, dict) else {}
    contact_info = parser_result.get("contact_info", {}) if isinstance(parser_result, dict) else {}
    return (
        parser_result.get("candidate_name")
        or parser_result.get("name")
        or contact_info.get("name")
        or contact_info.get("candidate_name")
        or ""
    )


def build_summary_insight(predicted_role, match_score, matched_count, missing_count):
    if match_score >= 0.65:
        fit = "strong"
    elif match_score >= 0.35:
        fit = "moderate"
    else:
        fit = "limited"

    return (
        f"This resume is currently classified as **{predicted_role}** and shows a **{fit} fit** "
        f"for the provided job description. It matches **{matched_count}** relevant skills "
        f"while missing **{missing_count}** target skills."
    )


def render_analysis_overview(
    predicted_role,
    confidence_display,
    ats_result,
    match_score,
    matched_count,
    missing_count,
    extra_count,
    gap,
) -> None:
    render_section_title(
        "Candidate Snapshot",
        "A recruiter-style summary of the current resume, model output, and job alignment signals.",
    )
    c1, c2, c3, c4 = st.columns(4, gap="medium")
    with c1:
        render_metric_card("Predicted Role", predicted_role, "Current classifier output")
    with c2:
        render_metric_card("Model Confidence", confidence_display, "Baseline model signal")
    with c3:
        render_metric_card("ATS Compatibility Score", f"{ats_result.get('ats_score', 0)}%", ats_result.get("grade"))
    with c4:
        render_metric_card("JD Keyword Match", f"{match_score:.2%}", "Skill overlap with target job")

    st.markdown(
        f"""
        <div class="insight-box">
            {build_summary_insight(predicted_role, match_score, matched_count, missing_count)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.05, 0.95], gap="large")
    with left:
        render_section_title("Top Highlights")
        highlights = [
            f"Matched skills: {matched_count}",
            f"Extra resume skills: {extra_count}",
            f"Model confidence: {confidence_display}",
        ]
        if ats_result.get("grade"):
            highlights.append(f"ATS grade: {ats_result.get('grade')}")
        for item in highlights:
            st.markdown(f"- {item}")

    with right:
        render_section_title("Top Risks")
        risks = []
        missing_skills = gap.get("missing", []) if isinstance(gap, dict) else []
        if missing_skills:
            risks.append("Missing target skills: " + ", ".join(missing_skills[:8]))
        if match_score < 0.35:
            risks.append("Job-description skill overlap is currently limited.")
        if ats_result.get("ats_score", 0) < 50:
            risks.append("ATS compatibility needs stronger structure, keywords, or evidence.")
        if not risks:
            risks.append("No major job-match risks detected from the available signals.")
        for item in risks:
            st.markdown(f"- {item}")

    render_section_title("Decision-Support Interpretation")
    if match_score >= 0.65:
        render_alert_banner(get_match_feedback(match_score), "success")
    elif match_score >= 0.35:
        render_alert_banner(get_match_feedback(match_score), "info")
    else:
        render_alert_banner(get_match_feedback(match_score), "warning")

    render_section_title("Recommended Next Step")
    if missing_count > 0:
        st.write("Focus resume improvements on relevant missing skills and tailor project descriptions around the target role.")
    else:
        st.write("The candidate already aligns well. The next step is strengthening achievement-based bullet points.")


def render_resume_improvement_report(report: dict) -> None:
    render_section_title(
        "Resume Improvement Report",
        "A local, rule-based action plan built from existing ResumeIQ analysis results.",
    )
    st.write(report.get("overall_summary", ""))

    cards = get_report_summary_cards(report)
    card_columns = st.columns(len(cards), gap="medium")
    for column, card in zip(card_columns, cards):
        with column:
            render_metric_card(
                card.get("title", ""),
                card.get("value", ""),
                card.get("helper_text", ""),
            )

    strengths_col, risks_col = st.columns(2, gap="large")
    with strengths_col:
        render_section_title("Strengths")
        for strength in report.get("strengths", []):
            st.markdown(f"- {strength}")

    with risks_col:
        render_section_title("Risks")
        for risk in report.get("risks", []):
            st.markdown(f"- {risk}")

    render_section_title("Priority Actions")
    for action in report.get("priority_actions", []):
        st.markdown(f"- {action}")

    render_alert_banner(report.get("disclaimer", ""), "info")


def render_candidate_fit_section(candidate_fit_result: dict, role_profile_summary: dict | None = None) -> None:
    render_section_title(
        "Multi-Score Candidate Fit",
        "An explainable local estimate that combines resume, job-description, ATS, quality, and model signals.",
    )
    st.write(candidate_fit_result.get("summary", ""))

    if role_profile_summary:
        render_section_title("Role-Specific Scoring Profile")
        role_col, component_col = st.columns(2, gap="medium")
        with role_col:
            render_metric_card(
                "Target Role Used",
                role_profile_summary.get("target_role", "General / Unknown"),
                "Inferred from JD text first, then predicted role.",
            )
        with component_col:
            render_metric_card(
                "Top Weighted Component",
                role_profile_summary.get("top_weighted_component", "Not available"),
                "Highest-weighted local fit signal for this role.",
            )
        st.markdown("##### Priority skill categories")
        render_badge_group(role_profile_summary.get("priority_categories", []))
        if role_profile_summary.get("role_guidance"):
            st.write(role_profile_summary.get("role_guidance"))
        render_alert_banner(
            "ResumeIQ adjusts fit-signal weights based on the target role. This is a local rule-based profile, not a hiring decision.",
            "info",
        )

    cards = get_candidate_fit_summary_cards(candidate_fit_result)
    card_columns = st.columns(len(cards), gap="medium")
    for column, card in zip(card_columns, cards):
        with column:
            render_metric_card(
                card.get("title", ""),
                card.get("value", ""),
                card.get("helper_text", ""),
            )

    component_scores = candidate_fit_result.get("component_scores", [])
    if component_scores:
        component_df = pd.DataFrame(component_scores)
        component_df["weight"] = component_df["weight"].apply(lambda value: f"{value:.0%}")
        st.dataframe(component_df, width="stretch", hide_index=True)

    strengths_col, risks_col = st.columns(2, gap="large")
    with strengths_col:
        render_section_title("Strong Fit Signals")
        for signal in candidate_fit_result.get("strength_signals", []):
            st.markdown(f"- {signal}")

    with risks_col:
        render_section_title("Risk Signals")
        risks = candidate_fit_result.get("risk_signals", [])
        if risks:
            for risk in risks:
                st.markdown(f"- {risk}")
        else:
            st.write("No major risk signals detected from the available fit components.")

    render_section_title("Priority Actions")
    for action in candidate_fit_result.get("priority_actions", []):
        st.markdown(f"- {action}")

    render_alert_banner(candidate_fit_result.get("disclaimer", ""), "info")


def render_recruiter_workflow_section(ranked_rows: list[dict], privacy_mode: bool = False) -> None:
    render_section_title(
        "Recruiter Notes & Shortlist Workflow",
        "Add manual review statuses and notes for each ranked resume.",
    )
    st.write(
        "Add manual review statuses and notes for each ranked resume. These notes are stored locally "
        "in this session and can be exported as CSV."
    )

    if "recruiter_review_state" not in st.session_state:
        st.session_state["recruiter_review_state"] = {}

    if not ranked_rows:
        render_empty_state(
            "Run Batch Ranking first",
            "Run Batch Ranking first to add recruiter notes and shortlist statuses.",
        )
        return

    status_options = get_review_status_options()
    display_rows = anonymize_batch_rows(ranked_rows) if privacy_mode else ranked_rows
    for row, display_row in zip(ranked_rows, display_rows):
        review_key = make_review_key(row)
        saved_review = st.session_state["recruiter_review_state"].get(review_key, {})
        current_status = saved_review.get("status", get_default_review_status(row))
        if current_status not in status_options:
            current_status = get_default_review_status(row)
        current_note = saved_review.get("note", "")

        with st.expander(f"{display_row.get('Rank')}. {display_row.get('Candidate')}"):
            score_col, label_col, recommendation_col = st.columns(3, gap="medium")
            with score_col:
                render_metric_card("Overall Fit Score", f"{display_row.get('Overall Fit Score', 0)}%", "Batch fit signal")
            with label_col:
                render_metric_card("Fit Label", display_row.get("Fit Label", "Not available"), "Local fit interpretation")
            with recommendation_col:
                render_metric_card(
                    "Recommendation",
                    display_row.get("Recommendation", "Not available"),
                    "Decision-support recommendation",
                )

            actions_text = display_row.get("Priority Actions", "")
            actions = [item.strip() for item in actions_text.split("|") if item.strip()]
            st.markdown("##### Priority Actions")
            if actions:
                for action in actions:
                    st.markdown(f"- {action}")
            else:
                st.write("No priority actions available.")

            status = st.selectbox(
                "Manual Review Status",
                options=status_options,
                index=status_options.index(current_status),
                key=f"review_status_{review_key}",
            )
            note = st.text_area(
                "Recruiter Note",
                value=current_note,
                key=f"review_note_{review_key}",
                placeholder="Add session-local review notes...",
            )
            st.session_state["recruiter_review_state"][review_key] = {
                "status": status,
                "note": note,
            }

    review_records = build_review_records(ranked_rows, st.session_state["recruiter_review_state"])
    export_review_records = anonymize_review_records(review_records) if privacy_mode else review_records
    review_summary = get_review_summary(export_review_records)
    st.write(review_summary.get("main_message", ""))

    review_cards = get_review_summary_cards(review_summary)
    review_columns = st.columns(len(review_cards), gap="medium")
    for column, card in zip(review_columns, review_cards):
        with column:
            render_metric_card(card.get("title", ""), card.get("value", ""), card.get("helper_text", ""))

    review_csv = convert_review_records_to_csv(export_review_records)
    csv_col, clear_col = st.columns([0.58, 0.42], gap="medium")
    with csv_col:
        st.download_button(
            "Download Recruiter Review CSV",
            data=review_csv,
            file_name="resumeiq_recruiter_review.csv",
            mime="text/csv",
        )
    with clear_col:
        if st.button("Clear Recruiter Notes"):
            st.session_state["recruiter_review_state"] = {}
            for key in list(st.session_state.keys()):
                if key.startswith("review_status_") or key.startswith("review_note_"):
                    del st.session_state[key]
            st.rerun()


def render_prediction_explanation_section(prediction_explanation: dict) -> None:
    render_section_title(
        "Local Baseline Explanation",
        "Terms that may have influenced the current classifier output.",
    )

    cards = get_prediction_explanation_cards(prediction_explanation)
    card_columns = st.columns(len(cards), gap="medium")
    for column, card in zip(card_columns, cards):
        with column:
            render_metric_card(card.get("title", ""), card.get("value", ""), card.get("helper_text", ""))

    confidence = prediction_explanation.get("confidence", {}) or {}
    if confidence.get("message"):
        render_alert_banner(confidence.get("message"), "info")

    supporting_terms = prediction_explanation.get("supporting_terms", [])
    if supporting_terms:
        st.markdown("##### Supporting terms")
        terms_df = pd.DataFrame(supporting_terms)
        st.dataframe(terms_df, width="stretch", hide_index=True)
        render_badge_group([item.get("term", "") for item in supporting_terms])
    else:
        render_empty_state(
            "Prediction explanation unavailable",
            "Prediction explanation is unavailable for the current model artifact, but confidence interpretation is still shown.",
        )

    if prediction_explanation.get("message"):
        st.write(prediction_explanation.get("message"))

    warnings = prediction_explanation.get("warnings", [])
    if warnings:
        render_section_title("Interpretation Notes")
        for warning in warnings:
            render_alert_banner(warning, "warning")

    render_alert_banner(prediction_explanation.get("disclaimer", ""), "info")


def render_batch_ranking_section(job_description: str, privacy_mode: bool = False) -> None:
    render_section_title(
        "Batch Resume Ranking",
        "Upload multiple resumes and compare them against the pasted job description using ResumeIQ fit signals.",
    )
    render_alert_banner(
        "This is a decision-support ranking. Review the full resume and job context before making decisions.",
        "info",
    )
    st.info("First run may take longer while the local semantic model loads.")

    batch_uploaded_files = st.file_uploader(
        "Upload multiple resumes",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        key="batch_resume_uploads",
        help="Select multiple files at once using Command + click on Mac or Ctrl + click on Windows.",
    )
    st.caption("Select multiple files at once using Command + click on Mac or Ctrl + click on Windows.")

    ensure_batch_file_store()

    render_section_title("Or Add Resumes One at a Time")
    single_batch_file = st.file_uploader(
        "Add one resume to batch",
        type=["pdf", "docx", "txt"],
        key="single_batch_resume_upload",
    )
    add_col, clear_col = st.columns([0.5, 0.5], gap="medium")
    with add_col:
        if st.button("Add Resume to Batch"):
            if single_batch_file is None:
                render_alert_banner("Choose one resume before adding it to the batch.", "warning")
            else:
                added_count = store_files_for_batch([single_batch_file])
                if added_count == 0:
                    render_alert_banner("This file is already added to the batch.", "warning")
                else:
                    st.success(f"{single_batch_file.name} added to the batch list.")
    with clear_col:
        if st.button("Clear Batch List"):
            st.session_state["batch_file_store"] = []
            st.session_state["batch_ranking_rows"] = []
            st.info("Batch list cleared.")

    stored_batch_files = [
        StoredUploadedFile(item.get("name", "Candidate"), item.get("type", ""), item.get("bytes", b""))
        for item in st.session_state.get("batch_file_store", [])
    ]
    batch_files = []
    seen_batch_names = set()
    for file in list(batch_uploaded_files or []) + stored_batch_files:
        file_name = getattr(file, "name", "")
        if file_name in seen_batch_names:
            continue
        batch_files.append(file)
        seen_batch_names.add(file_name)

    if batch_files:
        st.success(f"{len(batch_files)} resume file(s) ready for batch ranking.")
        st.markdown("##### Batch files ready:")
        with st.expander("Selected batch files"):
            for file in batch_files:
                st.write(f"- {file.name}")
    else:
        st.info(
            "No batch resumes selected yet. Select multiple files at once or add resumes one at a time."
        )

    if not job_description.strip():
        render_alert_banner("Paste a job description first to run batch ranking.", "warning")
        return

    if len(batch_files) == 1:
        render_alert_banner(
            "Upload two or more resumes for a true comparison. One resume can still be analyzed.",
            "info",
        )

    if not batch_files:
        render_empty_state(
            "No batch resumes uploaded",
            "Upload multiple PDF, DOCX, or TXT resumes here to compare them against the pasted job description.",
        )
    run_batch = st.button("Run Batch Ranking", type="primary")

    if run_batch:
        if not batch_files:
            render_alert_banner("Upload at least one batch resume before running batch ranking.", "warning")
        else:
            rows = []
            progress = st.progress(0, text="Preparing batch ranking...")
            with st.spinner("Analyzing batch resumes locally..."):
                for index, batch_file in enumerate(batch_files, start=1):
                    rows.append(analyze_resume_for_batch(batch_file, job_description))
                    progress.progress(index / len(batch_files), text=f"Analyzed {index} of {len(batch_files)} resumes")
            ranked_rows = rank_batch_results(rows)
            st.session_state["batch_ranking_rows"] = ranked_rows
            progress.empty()

    ranked_rows = st.session_state.get("batch_ranking_rows", [])
    if ranked_rows:
        display_rows = anonymize_batch_rows(ranked_rows) if privacy_mode else ranked_rows
        summary = get_batch_summary(display_rows)
        st.write(summary.get("main_message", ""))
        summary_cards = get_batch_summary_cards(summary)
        summary_columns = st.columns(len(summary_cards), gap="medium")
        for column, card in zip(summary_columns, summary_cards):
            with column:
                render_metric_card(card.get("title", ""), card.get("value", ""), card.get("helper_text", ""))

        render_section_title("Ranked Resumes by Fit Signals")
        st.caption(summary.get("top_candidate_label", ""))
        st.dataframe(pd.DataFrame(display_rows), width="stretch", hide_index=True)

        csv_data = convert_rows_to_csv(display_rows)
        st.download_button(
            "Download Ranking CSV",
            data=csv_data,
            file_name="resumeiq_batch_ranking.csv",
            mime="text/csv",
        )

        rows_with_actions = [
            (row, display_row)
            for row, display_row in zip(ranked_rows, display_rows)
            if row.get("Priority Actions")
        ]
        if rows_with_actions:
            render_section_title("Priority Actions by Resume")
            for row, display_row in rows_with_actions[:5]:
                with st.expander(f"{display_row.get('Rank')}. {display_row.get('Candidate')}"):
                    actions_text = row.get("Priority Actions", "")
                    actions = [item.strip() for item in actions_text.split("|") if item.strip()]
                    if actions:
                        for action in actions:
                            st.markdown(f"- {action}")
                    else:
                        st.write("No priority actions available.")

        render_recruiter_workflow_section(ranked_rows, privacy_mode=privacy_mode)
    else:
        render_recruiter_workflow_section([], privacy_mode=privacy_mode)


def render_ats_section(ats_result: dict, has_job_description: bool) -> None:
    render_section_title("ATS Compatibility", "Structure, keyword coverage, skill overlap, and role alignment.")

    if not has_job_description:
        render_alert_banner("Paste a job description to calculate ATS compatibility.", "info")
        return

    score_col, grade_col = st.columns([0.45, 0.55], gap="medium")
    with score_col:
        render_score_summary(
            "ATS Compatibility Score",
            ats_result.get("ats_score"),
            helper_text="Estimated compatibility signal",
        )
    with grade_col:
        render_metric_card("Grade", ats_result.get("grade", "N/A"), "Structure, keywords, skills, and alignment")

    st.write(ats_result.get("feedback", ""))

    with st.expander("Score breakdown and suggestions", expanded=False):
        breakdown_labels = {
            "skill_match": "Skill Match",
            "keyword_coverage": "Keyword Coverage",
            "section_quality": "Section Quality",
            "achievement_score": "Achievement Score",
            "formatting_score": "Formatting Score",
            "jd_alignment": "JD Alignment",
        }
        breakdown_df = pd.DataFrame(
            {
                "Category": [breakdown_labels[key] for key in breakdown_labels],
                "Score": [(ats_result.get("breakdown") or {}).get(key, 0) for key in breakdown_labels],
            }
        )
        st.dataframe(breakdown_df, width="stretch", hide_index=True)

        left, right = st.columns(2, gap="large")
        with left:
            st.markdown("##### Strengths")
            if ats_result.get("strengths"):
                for strength in ats_result.get("strengths", []):
                    st.markdown(f"- {strength}")
            else:
                st.write("No strong ATS compatibility signals detected yet.")

        with right:
            st.markdown("##### Improvement suggestions")
            if ats_result.get("improvements"):
                for improvement in ats_result.get("improvements", []):
                    st.markdown(f"- {improvement}")
            else:
                st.write("No major improvement suggestions detected.")

    st.caption(ats_result.get("disclaimer", ""))


def render_sentence_quality_section(sentence_quality_result: dict) -> None:
    render_section_title(
        "AI-Like / Generic Sentence Detection",
        "Flags wording that may sound generic, vague, or AI-like. This does not prove AI usage.",
    )
    st.write(
        "This section highlights resume sentences that may sound generic, vague, or AI-like. "
        "It does not prove AI usage; it helps improve recruiter readability."
    )

    flagged_sentences = sentence_quality_result.get("flagged_sentences", [])
    st.write(sentence_quality_result.get("summary", ""))

    total_col, high_col, moderate_col = st.columns(3, gap="medium")
    with total_col:
        render_metric_card(
            "Total Sentences Analyzed",
            str(sentence_quality_result.get("total_sentences_analyzed", 0)),
            "Readable resume sentences and bullets",
        )
    with high_col:
        render_metric_card(
            "High Risk",
            str(sentence_quality_result.get("high_risk_count", 0)),
            "May sound generic or AI-like",
        )
    with moderate_col:
        render_metric_card(
            "Moderate Risk",
            str(sentence_quality_result.get("moderate_risk_count", 0)),
            "Worth reviewing for specificity",
        )

    if not flagged_sentences:
        render_alert_banner("Your resume language looks specific, natural, and recruiter-friendly.", "success")
        return

    for index, item in enumerate(flagged_sentences, start=1):
        label = f"{index}. {item.get('risk_level', 'Unknown')} risk | Score {item.get('generic_score', 0)}/100"
        with st.expander(label, expanded=index == 1):
            st.markdown("##### Original sentence")
            st.write(item.get("sentence", ""))

            score_col, risk_col = st.columns(2, gap="medium")
            with score_col:
                st.metric("Generic/AI-like score", f"{item.get('generic_score', 0)}/100")
            with risk_col:
                st.metric("Risk level", item.get("risk_level", "Unknown"))

            st.markdown("##### Reasons")
            for reason in item.get("reasons", []):
                st.markdown(f"- {reason}")

            signals = item.get("signals", {})
            st.markdown("##### Signals")
            st.write(
                {
                    "generic_phrases": signals.get("generic_phrases", []),
                    "weak_phrases": signals.get("weak_phrases", []),
                    "vague_phrases": signals.get("vague_phrases", []),
                    "has_metric": signals.get("has_metric", False),
                    "has_tool_or_skill": signals.get("has_tool_or_skill", False),
                    "has_action_verb": signals.get("has_action_verb", False),
                }
            )


def render_structure_advisor(advice: dict) -> None:
    render_section_title(
        "Resume Structure & Format Advisor",
        "Local, rule-based suggestions for resume sections, bullets, formatting, and recruiter readability.",
    )
    st.write(advice.get("overall_message", ""))

    cards = get_structure_summary_cards(advice)
    card_columns = st.columns(len(cards), gap="medium")
    for column, card in zip(card_columns, cards):
        with column:
            render_metric_card(
                card.get("title", ""),
                card.get("value", ""),
                card.get("helper_text", ""),
            )

    order_col, formula_col = st.columns(2, gap="large")
    with order_col:
        render_section_title("Suggested Section Order")
        for index, section in enumerate(advice.get("recommended_section_order", []), start=1):
            st.markdown(f"{index}. {section}")

    with formula_col:
        render_section_title("Recommended Bullet Formula")
        render_alert_banner(advice.get("recommended_bullet_formula", ""), "info")

        example = advice.get("example_before_after", {})
        st.markdown("##### Example before")
        st.write(example.get("before", ""))
        st.markdown("##### Suggested template")
        st.write(example.get("after", ""))

    render_section_title("Findings")
    findings = advice.get("findings", [])
    if not findings:
        render_alert_banner("No major structure findings detected. Review section labels and bullets for clarity before applying.", "success")
    else:
        for index, finding in enumerate(findings, start=1):
            with st.expander(f"{index}. {finding.get('issue', 'Structure finding')}", expanded=index == 1):
                st.write(f"Severity: {finding.get('severity', 'info')}")
                st.markdown("##### Why it matters")
                st.write(finding.get("why_it_matters", ""))
                st.markdown("##### Recommendation")
                st.write(finding.get("recommendation", ""))

    render_section_title("Priority Fixes")
    for fix in advice.get("priority_fixes", []):
        st.markdown(f"- {fix}")

    render_alert_banner(advice.get("disclaimer", ""), "info")


def render_skill_taxonomy_breakdown(taxonomy_result: dict) -> None:
    render_section_title(
        "Skill Taxonomy Breakdown",
        "Category-level skill intelligence for understanding alignment with the target role.",
    )
    summary = get_skill_taxonomy_summary(taxonomy_result)
    category_summary = taxonomy_result.get("category_summary", [])

    if not category_summary:
        render_empty_state(
            "No categorized skills yet",
            "Upload a resume and paste a job description to view skill taxonomy.",
        )
        return

    metric_cols = st.columns(4, gap="medium")
    with metric_cols[0]:
        render_metric_card(
            "Resume Categories",
            summary.get("total_resume_categories", 0),
            "Skill categories detected in the resume",
        )
    with metric_cols[1]:
        render_metric_card(
            "Gap Categories",
            summary.get("total_gap_categories", 0),
            "Category-level gaps from the target role",
        )
    with metric_cols[2]:
        render_metric_card(
            "Strength Categories",
            len(taxonomy_result.get("top_strength_categories", [])),
            "Categories with matched skills",
        )
    with metric_cols[3]:
        render_metric_card(
            "Missing Categories",
            len(taxonomy_result.get("top_gap_categories", [])),
            "Categories with missing skills",
        )

    render_alert_banner(summary.get("top_strength_message", ""), "info")
    render_alert_banner(summary.get("top_gap_message", ""), "warning")

    st.markdown("##### Category summary")
    st.dataframe(pd.DataFrame(category_summary), width="stretch", hide_index=True)

    categorized_cols = st.columns(3, gap="large")
    categorized_groups = [
        ("Categorized Resume Skills", taxonomy_result.get("resume_categories", {})),
        ("Categorized Matched Skills", taxonomy_result.get("matched_categories", {})),
        ("Categorized Missing Skills", taxonomy_result.get("missing_categories", {})),
    ]
    for column, (title, categories) in zip(categorized_cols, categorized_groups):
        with column:
            render_section_title(title)
            if not categories:
                st.write("None detected.")
                continue
            for category, skills in categories.items():
                st.markdown(f"##### {category}")
                render_badge_group(skills)

    if taxonomy_result.get("top_gap_categories"):
        render_alert_banner("Add missing skills only if they reflect your real experience.", "info")


def render_semantic_match_section(semantic_result: dict, privacy_mode: bool = False, candidate_name: str = "") -> None:
    render_section_title(
        "Semantic JD-Resume Match",
        "Meaning-based similarity between the resume and target job description.",
    )

    if not semantic_result.get("available"):
        render_alert_banner(semantic_result.get("message", "Semantic matching is unavailable."), "warning")
        render_alert_banner(semantic_result.get("disclaimer", ""), "info")
        return

    score_col, label_col = st.columns([0.45, 0.55], gap="medium")
    with score_col:
        render_score_summary(
            "Semantic Match Score",
            semantic_result.get("semantic_score"),
            helper_text="Meaning-based JD/resume alignment",
        )
    with label_col:
        render_metric_card(
            "Similarity Label",
            semantic_result.get("similarity_label", "Unavailable"),
            semantic_result.get("message", ""),
        )

    summary_cards = get_semantic_summary_cards(semantic_result)
    summary_cols = st.columns(len(summary_cards), gap="medium")
    for column, card in zip(summary_cols, summary_cards):
        with column:
            render_metric_card(card.get("title", ""), card.get("value", ""), card.get("helper_text", ""))

    top_pairs = semantic_result.get("top_matching_pairs", [])
    if top_pairs:
        render_section_title("Top Matching Pairs")
        for index, pair in enumerate(top_pairs, start=1):
            with st.expander(f"{index}. Similarity {pair.get('similarity', 0)}", expanded=index == 1):
                st.markdown("##### Resume evidence")
                resume_chunk = pair.get("resume_chunk", "")
                if privacy_mode:
                    resume_chunk = mask_pii(resume_chunk, candidate_name=candidate_name)
                st.write(resume_chunk)
                st.markdown("##### Job description requirement")
                st.write(pair.get("jd_chunk", ""))

    weak_chunks = semantic_result.get("weak_jd_chunks", [])
    if weak_chunks:
        render_section_title("Weak JD Coverage Areas")
        for index, item in enumerate(weak_chunks, start=1):
            with st.expander(f"{index}. Best similarity {item.get('best_similarity', 0)}", expanded=False):
                st.markdown("##### JD requirement")
                st.write(item.get("jd_chunk", ""))
                st.markdown("##### Recommendation")
                st.write(item.get("recommendation", ""))
    else:
        render_alert_banner("No weak JD chunks detected by semantic matching.", "success")

    render_alert_banner(semantic_result.get("disclaimer", ""), "info")


def render_jd_keyword_match_section(match_score, matched_count, missing_count, gap) -> None:
    render_section_title("JD Keyword Match", "Skill overlap between the resume and target job description.")

    jm1, jm2, jm3 = st.columns(3, gap="medium")
    with jm1:
        render_score_summary("JD Match Percentage", f"{match_score:.2%}", helper_text="Resume/JD skill overlap")
    with jm2:
        render_metric_card("Matched Skills", matched_count, "Skills found in both resume and JD")
    with jm3:
        render_metric_card("Missing Skills", missing_count, "JD skills not detected in resume")

    st.markdown("##### Matched skills")
    render_badge_group(gap.get("matched", []))
    st.markdown("##### Missing skills")
    render_badge_group(gap.get("missing", []))


def render_skills_intelligence_section(resume_skills, gap, role_profile_summary, skill_taxonomy_result) -> None:
    render_section_title(
        "Skills Intelligence",
        "Extracted resume skills, target-job overlap, missing skills, and role-specific skill categories.",
    )
    if role_profile_summary.get("priority_categories"):
        st.write("Priority categories for this role:")
        render_badge_group(role_profile_summary.get("priority_categories", []))

    skill_cols = st.columns(2, gap="large")
    with skill_cols[0]:
        st.markdown("##### Resume skills")
        render_badge_group(resume_skills)

        st.markdown("##### Matched skills")
        render_badge_group(gap.get("matched", []))

    with skill_cols[1]:
        st.markdown("##### Missing skills")
        render_badge_group(gap.get("missing", []))

        st.markdown("##### Extra resume skills")
        render_badge_group(gap.get("extra", []))

    render_skill_taxonomy_breakdown(skill_taxonomy_result)


def _preview_sentence(sentence: str, max_words: int = 9) -> str:
    cleaned = re.sub(r"\s+", " ", str(sentence or "")).strip()
    if not cleaned:
        return "review flagged sentence"
    words = cleaned.split()
    preview = " ".join(words[:max_words])
    if len(words) > max_words:
        preview += "..."
    return preview


def format_suggestion_title(index: int, issue_label: str, original_sentence: str) -> str:
    label = str(issue_label or "Rewrite suggestion").strip()
    preview = _preview_sentence(original_sentence)
    return f"{index}. {label} - {preview}"


def render_rewrite_suggestions_section(
    rewrite_suggestions,
    rewrite_summary,
    privacy_mode: bool = False,
    candidate_name: str = "",
) -> None:
    render_section_title(
        "Humanized Rewrite Suggestions",
        "Local template-based rewrite suggestions from flagged resume sentences.",
    )
    render_alert_banner(
        "These are local template-based rewrite suggestions from flagged resume sentences. They help improve clarity and structure but do not create final AI-generated bullets or invent achievements.",
        "info",
    )

    if not rewrite_suggestions:
        render_empty_state(
            "No rewrite suggestions yet",
            "ResumeIQ generates rewrite suggestions when it finds generic, vague, or AI-like sentences.",
        )
        return

    summary_col, pattern_col = st.columns([0.42, 0.58], gap="medium")
    with summary_col:
        render_metric_card(
            "Total Suggestions",
            rewrite_summary.get("total_suggestions", 0),
            "Template-based suggestions from flagged sentences",
        )
    with pattern_col:
        render_section_title("Top Issue Patterns")
        render_badge_group(rewrite_summary.get("top_patterns", []))

    render_alert_banner(rewrite_summary.get("priority_message", ""), "info")
    issue_counts = Counter(
        suggestion.get("issue_type") or suggestion.get("pattern", "default")
        for suggestion in rewrite_suggestions
        if isinstance(suggestion, dict)
    )
    if any(count > 1 for count in issue_counts.values()):
        st.caption("Repeated issue types mean multiple resume sentences have the same writing pattern.")

    for index, suggestion in enumerate(rewrite_suggestions, start=1):
        original_sentence = suggestion.get("original_sentence", "")
        display_sentence = original_sentence
        if privacy_mode:
            display_sentence = mask_pii(display_sentence, candidate_name=candidate_name)
        title = format_suggestion_title(
            index,
            suggestion.get("issue_label") or suggestion.get("issue", "Rewrite suggestion"),
            display_sentence,
        )
        with st.expander(title, expanded=index == 1):
            st.markdown("##### Flagged sentence")
            st.markdown(f"> {display_sentence}")

            st.markdown("##### Why this needs attention")
            st.write(suggestion.get("explanation") or suggestion.get("why_weak", "Review this sentence for clarity and specificity."))

            st.markdown("##### Suggested rewrite pattern")
            st.code(suggestion.get("rewrite_formula", "Action Verb + Task + Tool/Method + Result/Impact"), language="text")

            st.markdown("##### Rewrite template")
            st.write(suggestion.get("rewrite_template") or suggestion.get("suggested_rewrite", ""))

            st.markdown("##### How to customize")
            tips = suggestion.get("customization_tips") or [
                "Replace placeholders with truthful project/task details.",
                "Add tools or methods only if you actually used them.",
                "Add measurable results only if you can support them.",
            ]
            for tip in tips[:3]:
                st.markdown(f"- {tip}")

            safety_note = suggestion.get("safety_note")
            if safety_note:
                st.caption(safety_note)


def render_resume_preview_section(parser_result, resume_text, job_description, template_detection, template_severity, privacy_mode) -> None:
    render_section_title(
        "Resume Preview",
        "Extracted text and parser details used by the current analysis pipeline.",
    )
    st.markdown("##### Extracted resume text")
    preview_candidate_name = get_candidate_name_from_parser(parser_result)
    display_resume_text = resume_text
    if privacy_mode:
        render_alert_banner(
            "Privacy-safe display mode is enabled. Extracted resume text is masked for review.",
            "info",
        )
        display_resume_text = mask_pii(resume_text, candidate_name=preview_candidate_name)
    st.text_area("Resume text", display_resume_text[:8000], height=320, label_visibility="collapsed")

    with st.expander("Parser details", expanded=False):
        sections = parser_result.get("sections", {})
        if sections:
            st.markdown("##### Detected sections")
            st.json(summarize_detected_sections(sections))

        contact_info = parser_result.get("contact_info")
        if contact_info:
            st.markdown("##### Contact summary")
            if privacy_mode:
                st.json(
                    {
                        "email": "[email]" if contact_info.get("email") else None,
                        "phone": "[phone]" if contact_info.get("phone") else None,
                        "linkedin": "[linkedin]" if contact_info.get("linkedin") else None,
                        "github": "[github]" if contact_info.get("github") else None,
                        "portfolio": "[portfolio]" if contact_info.get("portfolio") else None,
                    }
                )
            else:
                st.json(contact_info)

        st.markdown("##### Estimated years of experience")
        years = parser_result.get("estimated_years_experience")
        st.write(f"{years} years" if years is not None else "Not detected")

        if template_detection:
            st.markdown("##### Template detection")
            if template_severity == "strong" and template_detection.get("warning"):
                st.warning(template_detection.get("warning"))
            elif template_severity == "partial" and template_detection.get("warning"):
                st.info(template_detection.get("warning"))
            st.write(
                {
                    "template_score": template_detection.get("template_score"),
                    "severity": template_detection.get("severity", "none"),
                    "matched_placeholders": template_detection.get("matched_placeholders", []),
                    "real_content_signals": template_detection.get("real_content_signals", []),
                }
            )

        parsed_items = {
            "education": parser_result.get("education"),
            "experience": parser_result.get("experience"),
            "projects": parser_result.get("projects"),
            "certifications": parser_result.get("certifications"),
        }
        available_items = {key: value for key, value in parsed_items.items() if value}
        if available_items:
            st.markdown("##### Parsed resume items")
            st.write(available_items)

    if job_description.strip():
        st.markdown("##### Job description text")
        st.text_area("Job description text", job_description[:5000], height=220, label_visibility="collapsed")


def render_model_transparency_section(prediction_explanation, top_predictions, metrics, clean_classes, jd_skills, matched_count, missing_count, extra_count) -> None:
    render_section_title(
        "Model Transparency",
        "Baseline classifier metadata, explainability, probabilities, and evaluation warnings.",
    )
    render_alert_banner(
        "The current baseline model is useful for demonstration, but the 100% validation accuracy and low real-resume confidence should be investigated later with stronger evaluation, calibration, and model comparison.",
        "info",
    )

    st.markdown("##### Model pipeline")
    st.code(
        "TF-IDF Vectorizer (1-2 grams, English stop words) -> Logistic Regression",
        language="text",
    )

    render_prediction_explanation_section(prediction_explanation)

    st.markdown("##### Prediction probabilities")
    if not top_predictions.empty:
        chart_df = top_predictions.set_index("Role")
        st.bar_chart(chart_df["Confidence %"])
        st.dataframe(top_predictions, width="stretch", hide_index=True)
    else:
        st.write("Probability output is not available for this classifier.")

    st.markdown("##### Stored evaluation metadata")
    if metrics:
        st.json({"accuracy": metrics.get("accuracy"), "available_roles": clean_classes})
    else:
        st.info("No metrics metadata file found.")

    if jd_skills:
        st.markdown("##### Match analytics snapshot")
        analytics_df = pd.DataFrame(
            {
                "Metric": ["Matched Skills", "Missing Skills", "Extra Skills"],
                "Count": [matched_count, missing_count, extra_count],
            }
        )
        st.bar_chart(analytics_df.set_index("Metric"))
        st.dataframe(analytics_df, width="stretch", hide_index=True)


def render_privacy_responsible_ai_section(privacy_mode: bool) -> None:
    render_navigation_section_title(
        "Privacy & Responsible AI",
        "Decision-support boundaries, privacy-safe display mode, and synthetic fairness monitoring concepts.",
    )
    render_disclaimer_box(
        "ResumeIQ is a decision-support tool. Final hiring or application decisions should be made by humans using complete context."
    )
    render_workflow_status(
        [
            {
                "label": "Privacy-safe display mode",
                "is_active": privacy_mode,
                "active_text": "On",
                "inactive_text": "Off",
            },
            {
                "label": "Local analysis",
                "is_active": True,
                "active_text": "Active",
                "inactive_text": "Inactive",
            },
        ]
    )
    st.write(
        "Privacy-safe mode masks common identifiers for display and exports where possible. "
        "It does not guarantee full anonymization or remove all bias."
    )
    render_alert_banner(
        "ResumeIQ does not score protected attributes such as age, gender, race, religion, disability, marital status, or immigration status.",
        "info",
    )

    fairness_intro = get_fairness_intro()
    render_section_title(
        fairness_intro.get("title", "Responsible AI Fairness Dashboard"),
        fairness_intro.get(
            "description",
            "Synthetic/demo monitoring view for understanding fairness risks in resume screening workflows.",
        ),
    )
    render_alert_banner(fairness_intro.get("disclaimer", ""), "info")
    render_alert_banner(
        f"{fairness_intro.get('safe_use', '')} ResumeIQ is not a hiring decision system and requires human review.",
        "warning",
    )

    synthetic_rows = get_synthetic_fairness_data()
    fairness_summary = calculate_fairness_summary(synthetic_rows)
    fairness_cards = get_fairness_metric_cards(fairness_summary)
    card_columns = st.columns(len(fairness_cards), gap="medium")
    for column, card in zip(card_columns, fairness_cards):
        with column:
            render_metric_card(card.get("title", ""), card.get("value", ""), card.get("helper_text", ""))

    st.markdown("##### Synthetic aggregate monitoring table")
    fairness_df = pd.DataFrame(synthetic_rows).rename(
        columns={
            "group": "Group",
            "applicants": "Applicants",
            "average_fit_score": "Average Fit Score",
            "recommended_for_review_rate": "Review Rate",
            "shortlist_rate": "Shortlist Rate",
            "false_positive_proxy": "False Positive Proxy",
            "false_negative_proxy": "False Negative Proxy",
        }
    )
    st.dataframe(fairness_df, width="stretch", hide_index=True)

    chart_df = fairness_df.set_index("Group")[["Review Rate"]]
    st.bar_chart(chart_df)
    st.caption(
        "Review Rate chart uses synthetic/demo data only. It is a monitoring concept and is not connected to real candidate records."
    )

    notes_col, checklist_col = st.columns(2, gap="large")
    with notes_col:
        render_section_title("Risk Notes")
        for note in get_fairness_risk_notes(fairness_summary):
            st.markdown(f"- {note}")

    with checklist_col:
        render_section_title("Responsible AI Checklist")
        checklist_rows = get_responsible_ai_checklist()
        for item in checklist_rows:
            st.markdown(
                f"""
                <div class="panel-card">
                    <div class="section-label">{item.get("title", "")}</div>
                    <div class="badge-row"><span class="ui-badge">{item.get("status", "")}</span></div>
                    <div class="subtle">{item.get("description", "")}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with st.expander("Fairness dashboard limitations", expanded=False):
        for limitation in get_fairness_limitations():
            st.markdown(f"- {limitation}")


def render_job_application_assistant_placeholder() -> None:
    render_navigation_section_title(
        "Job Application Assistant",
        "Future tools for candidate-facing documents.",
    )
    placeholder_text = "Planned future feature. Requires privacy safeguards and user consent before using external AI."
    cards = [
        "Tailored Resume Guidance",
        "Cover Letter Draft",
        "Recruiter Cold Email",
        "LinkedIn Cold Message",
        "Interview Prep Questions",
    ]
    columns = st.columns(2, gap="medium")
    for index, title in enumerate(cards):
        with columns[index % 2]:
            render_feature_placeholder_card(title, placeholder_text)


def summarize_detected_sections(sections: dict) -> dict:
    return {
        section_name: bool(section_text.strip())
        for section_name, section_text in sections.items()
    }


def analyze_resume_for_batch(uploaded_resume, job_description: str) -> dict:
    filename = getattr(uploaded_resume, "name", "Unknown file")
    try:
        if not is_supported_file(uploaded_resume):
            candidate_name = extract_candidate_name(filename=filename)
            return build_batch_row(
                filename=filename,
                candidate_name=candidate_name,
                candidate_fit_result={
                    "recommendation": "Could not analyze",
                    "risk_signals": ["Unsupported file type."],
                    "priority_actions": ["Upload a PDF, DOCX, or TXT resume."],
                },
            )

        parser_result = parse_resume(uploaded_resume)
        resume_text = parser_result.get("text", "")
        resume_clean = preprocess_resume_text(resume_text)
        candidate_name = extract_candidate_name(parser_result=parser_result, filename=filename)

        if not resume_clean.strip():
            return build_batch_row(
                filename=filename,
                candidate_name=candidate_name,
                candidate_fit_result={
                    "recommendation": "Could not analyze",
                    "risk_signals": ["Readable resume text could not be extracted."],
                    "priority_actions": ["Try a completed, text-based PDF, DOCX, or TXT resume."],
                },
            )

        prediction_result = predict_resume_role(resume_clean, model, vectorizer)
        predicted_role = prediction_result.get("role")
        target_role = infer_target_role(predicted_role=predicted_role, job_description=job_description)
        role_profile = get_role_profile(target_role)

        jd_match_result = analyze_job_description_match(resume_clean, job_description, skills_list)
        resume_skills = jd_match_result.get("resume_skills", [])
        jd_skills = jd_match_result.get("jd_skills", [])
        gap = jd_match_result.get("gap", {}) or {}

        skill_taxonomy_result = compare_skill_categories(
            resume_skills=resume_skills,
            jd_skills=jd_skills,
            matched_skills=gap.get("matched", []),
            missing_skills=gap.get("missing", []),
            extra_skills=gap.get("extra", []),
        )
        semantic_result = build_semantic_match_result(resume_text, job_description)
        ats_result = calculate_ats_score(
            resume_text=resume_text,
            job_description=job_description,
            resume_skills=resume_skills,
            jd_skills=jd_skills,
            matched_skills=gap.get("matched", []),
            missing_skills=gap.get("missing", []),
            parser_result=parser_result,
            existing_match_score=jd_match_result.get("match_score", 0),
        )
        sentence_quality_result = detect_ai_like_sentences(
            resume_text=resume_text,
            extracted_skills=resume_skills,
            max_results=10,
        )
        structure_advice = build_structure_advice(parser_result=parser_result, resume_text=resume_text)
        flagged_sentences = sentence_quality_result.get("flagged_sentences", [])
        rewrite_suggestions = generate_rewrite_suggestions(flagged_sentences, max_suggestions=8)
        candidate_fit_result = build_candidate_fit_score(
            prediction_result=prediction_result,
            ats_result=ats_result,
            jd_match_result=jd_match_result,
            semantic_result=semantic_result,
            skill_taxonomy_result=skill_taxonomy_result,
            sentence_quality_result=sentence_quality_result,
            rewrite_suggestions=rewrite_suggestions,
            structure_advice=structure_advice,
            parser_result=parser_result,
            resume_text=resume_text,
            target_role=target_role,
            role_profile=role_profile,
        )

        return build_batch_row(
            filename=filename,
            candidate_name=candidate_name,
            prediction_result=prediction_result,
            ats_result=ats_result,
            jd_match_result=jd_match_result,
            semantic_result=semantic_result,
            candidate_fit_result=candidate_fit_result,
            skill_taxonomy_result=skill_taxonomy_result,
            structure_advice=structure_advice,
            sentence_quality_result=sentence_quality_result,
        )
    except Exception as exc:
        candidate_name = extract_candidate_name(filename=filename)
        return build_batch_row(
            filename=filename,
            candidate_name=candidate_name,
            candidate_fit_result={
                "recommendation": "Could not analyze",
                "risk_signals": [f"File issue: {exc}"],
                "priority_actions": ["Review the file format and try uploading a readable resume."],
            },
        )


app_ready = True
model = None
vectorizer = None
skills_list = []

try:
    model, vectorizer = load_model()
except FileNotFoundError as exc:
    app_ready = False
    st.error(f"Model artifact is missing. Please run `python train.py` first. Details: {exc}")
except Exception as exc:
    app_ready = False
    st.error(f"Could not load model artifacts. Details: {exc}")

try:
    skills_list = get_skills()
except FileNotFoundError as exc:
    app_ready = False
    st.error(f"Skills list is missing. Details: {exc}")
except Exception as exc:
    app_ready = False
    st.error(f"Could not load skills list. Details: {exc}")

metrics = get_metrics()

ensure_batch_file_store()

render_page_header()

with st.sidebar:
    st.markdown("### Project Controls")
    use_sample_jd = st.toggle("Use sample job description", value=False)
    privacy_mode = st.toggle(
        "Privacy-safe display mode",
        value=False,
        help="Masks common personal identifiers in displayed resume text, batch ranking, recruiter notes, and exports where possible.",
    )
    st.caption(get_privacy_mode_message(privacy_mode))

    st.markdown("---")
    input_status_slot = st.container()

    st.markdown("---")
    st.markdown("### Model Snapshot")
    accuracy = metrics.get("accuracy", 0)
    st.metric("Validation accuracy", f"{accuracy:.2%}")
    st.caption("Baseline TF-IDF + Logistic Regression model. Treat high validation accuracy as a signal to investigate later.")

    classes = metrics.get("report", {}).keys()
    clean_classes = [c for c in classes if c not in {"accuracy", "macro avg", "weighted avg"}]
    st.caption(f"Supported roles: {', '.join(clean_classes[:10])}")

    st.markdown("---")
    st.markdown("### Workflow Guide")
    st.markdown(
        """
        <div class="subtle">
        1. Upload resume<br>
        2. Add job description<br>
        3. Review intelligence tabs
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("### Local Run")
    st.code("streamlit run app.py --server.fileWatcherType none", language="bash")

top_left, top_right = st.columns([1.18, 0.82], gap="large")

with top_left:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">1) Upload Resume</div>', unsafe_allow_html=True)
    main_uploaded_files = st.file_uploader(
        "Upload one or more resumes in PDF, TXT, or DOCX format",
        type=SUPPORTED_FILE_TYPES,
        accept_multiple_files=True,
        label_visibility="collapsed",
        key="main_resume_uploads",
    )
    main_uploaded_files = list(main_uploaded_files or [])
    uploaded_file = main_uploaded_files[0] if main_uploaded_files else None
    if main_uploaded_files:
        store_files_for_batch(main_uploaded_files)
    if len(main_uploaded_files) > 1:
        st.info(
            f"{len(main_uploaded_files)} resumes uploaded. The first resume will be used for the single-resume "
            "analysis. All uploaded resumes are available for Batch Ranking."
        )
    st.caption("Best results come from text-based PDFs or DOCX files rather than scanned-image PDFs.")
    st.markdown("</div>", unsafe_allow_html=True)

    default_jd = load_sample_jd() if use_sample_jd else ""
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">2) Paste Job Description</div>', unsafe_allow_html=True)
    job_description = st.text_area(
        "Paste job description",
        value=default_jd,
        height=240,
        label_visibility="collapsed",
        placeholder="Paste a Data Scientist / ML Engineer / Analyst job description here...",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    render_section_title("Input Status")
    render_workflow_status(
        [
            {
                "label": "Resume uploaded",
                "is_active": uploaded_file is not None,
                "active_text": "Uploaded",
                "inactive_text": "Needed",
            },
            {
                "label": "JD provided",
                "is_active": bool(job_description.strip()),
                "active_text": "Provided",
                "inactive_text": "Needed",
            },
            {
                "label": "Privacy mode",
                "is_active": privacy_mode,
                "active_text": "On",
                "inactive_text": "Off",
            },
            {
                "label": "Batch mode",
                "is_active": len(st.session_state.get("batch_file_store", [])) > 0,
                "active_text": "Available",
                "inactive_text": "Available",
            },
        ]
    )

with top_right:
    st.markdown(
        """
        <div class="panel-card">
            <div class="section-label">Dashboard Overview</div>
            <div class="subtle">
                ResumeIQ supports a recruiter and candidate review workflow:
                it reads resume content, estimates the most likely role,
                extracts candidate skills, compares them against a target job,
                and surfaces fit signals for human review.
                Final hiring or application decisions should be made by humans using complete context.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="panel-card">
            <div class="section-label">Suggested Demo Flow</div>
            <div class="subtle">
                1. Upload a resume<br>
                2. Paste a target job description<br>
                3. Review candidate overview<br>
                4. Examine job-match and quality signals<br>
                5. Export recruiter-ready notes if needed
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="panel-card">
            <div class="section-label">Tech Stack</div>
            <div class="subtle">
                Python • Streamlit • scikit-learn • pandas • pypdf
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with input_status_slot:
    st.markdown("### Input Status")
    render_workflow_status(
        [
            {
                "label": "Resume uploaded",
                "is_active": uploaded_file is not None,
                "active_text": "Yes",
                "inactive_text": "No",
            },
            {
                "label": "JD added",
                "is_active": bool(job_description.strip()),
                "active_text": "Yes",
                "inactive_text": "No",
            },
            {
                "label": "Batch files ready",
                "is_active": len(st.session_state.get("batch_file_store", [])) > 0,
                "active_text": str(len(st.session_state.get("batch_file_store", []))),
                "inactive_text": "0",
            },
        ]
    )

if uploaded_file is None:
    render_empty_state(
        "Upload a resume to begin",
        "Upload a PDF, DOCX, or TXT resume to unlock prediction, ATS compatibility, skill matching, writing-quality checks, and recruiter-style insights.",
    )
    if app_ready:
        render_batch_ranking_section(job_description, privacy_mode=privacy_mode)
elif not app_ready:
    st.error("The app cannot analyze resumes until the required model and data files are available.")
elif not is_supported_file(uploaded_file):
    st.error("Unsupported file type. Please upload a PDF, TXT, or DOCX resume.")
else:
    parser_result = parse_resume(uploaded_file)
    resume_text = parser_result["text"]
    resume_clean = preprocess_resume_text(resume_text)
    template_detection = parser_result["template_detection"]

    if not resume_clean.strip():
        if uploaded_file.name.lower().endswith(".docx"):
            st.error("Could not extract readable text from the uploaded DOCX file. Please try a completed, text-based DOCX resume.")
        elif uploaded_file.name.lower().endswith(".pdf"):
            st.error("Could not extract readable text from the uploaded PDF file. Please try a text-based PDF rather than a scanned-image PDF.")
        else:
            st.error("Could not extract readable text from the uploaded file. Please try a text-based PDF, DOCX, or TXT file.")
    else:
        template_severity = template_detection.get("severity", "strong" if template_detection.get("is_template") else "none")
        if template_severity == "strong":
            st.warning(template_detection["warning"])
        elif template_severity == "partial":
            st.info(template_detection["warning"])

        prediction = predict_resume_role(resume_clean, model, vectorizer)
        predicted_role = prediction["role"]
        top_predictions = prediction["top_predictions"]
        confidence_display = "N/A"

        if not top_predictions.empty:
            confidence_display = f"{top_predictions.iloc[0]['Confidence %']:.2f}%"

        prediction_explanation = build_prediction_explanation(
            resume_text=resume_text,
            prediction_result=prediction,
            model_or_pipeline=model,
            top_n=12,
        )

        target_role = infer_target_role(predicted_role=predicted_role, job_description=job_description)
        role_profile = get_role_profile(target_role)
        role_profile_summary = get_role_profile_summary(role_profile)

        match_analysis = analyze_job_description_match(resume_clean, job_description, skills_list)
        resume_skills = match_analysis["resume_skills"]
        jd_skills = match_analysis["jd_skills"]
        match_score = match_analysis["match_score"]
        gap = match_analysis["gap"]

        matched_count = len(gap["matched"])
        missing_count = len(gap["missing"])
        extra_count = len(gap["extra"])
        skill_taxonomy_result = compare_skill_categories(
            resume_skills=resume_skills,
            jd_skills=jd_skills,
            matched_skills=gap.get("matched", []),
            missing_skills=gap.get("missing", []),
            extra_skills=gap.get("extra", []),
        )
        semantic_result = build_semantic_match_result(resume_text, job_description)
        ats_result = calculate_ats_score(
            resume_text=resume_text,
            job_description=job_description,
            resume_skills=resume_skills,
            jd_skills=jd_skills,
            matched_skills=gap["matched"],
            missing_skills=gap["missing"],
            parser_result=parser_result,
            existing_match_score=match_score,
        )
        sentence_quality_result = detect_ai_like_sentences(
            resume_text=resume_text,
            extracted_skills=resume_skills,
            max_results=10,
        )
        structure_advice = build_structure_advice(parser_result=parser_result, resume_text=resume_text)
        flagged_sentences = sentence_quality_result.get("flagged_sentences", [])
        rewrite_suggestions = generate_rewrite_suggestions(flagged_sentences, max_suggestions=8)
        rewrite_summary = get_rewrite_summary(rewrite_suggestions)
        report_prediction = {
            "role": predicted_role,
            "confidence_display": confidence_display,
        }
        resume_improvement_report = build_resume_improvement_report(
            prediction_result=report_prediction,
            ats_result=ats_result,
            jd_match_result=match_analysis,
            sentence_quality_result=sentence_quality_result,
            rewrite_suggestions=rewrite_suggestions,
            parser_result=parser_result,
        )
        candidate_fit_result = build_candidate_fit_score(
            prediction_result=prediction,
            ats_result=ats_result,
            jd_match_result=match_analysis,
            semantic_result=semantic_result,
            skill_taxonomy_result=skill_taxonomy_result,
            sentence_quality_result=sentence_quality_result,
            rewrite_suggestions=rewrite_suggestions,
            structure_advice=structure_advice,
            parser_result=parser_result,
            resume_text=resume_text,
            target_role=target_role,
            role_profile=role_profile,
        )

        (
            overview_tab,
            quality_tab,
            match_tab,
            recruiter_tab,
            model_tab,
            privacy_tab,
            assistant_tab,
        ) = st.tabs(
            [
                "Candidate Overview",
                "Resume Quality",
                "Job Match Intelligence",
                "Recruiter Workspace",
                "Model Transparency",
                "Privacy & Responsible AI",
                "Job Application Assistant",
            ]
        )

        with overview_tab:
            render_navigation_section_title(
                "Candidate Overview",
                "High-level fit signals, recruiter-readable summary, and priority next steps.",
            )
            render_analysis_overview(
                predicted_role=predicted_role,
                confidence_display=confidence_display,
                ats_result=ats_result,
                match_score=match_score,
                matched_count=matched_count,
                missing_count=missing_count,
                extra_count=extra_count,
                gap=gap,
            )
            if semantic_result.get("available"):
                render_metric_card(
                    "Semantic Match Score",
                    f"{semantic_result.get('semantic_score')}%",
                    "Meaning-based JD/resume alignment",
                )
            explanation_confidence = prediction_explanation.get("confidence", {})
            if explanation_confidence.get("confidence_label") in {"Low", "Very Low"}:
                render_alert_banner(
                    "Model confidence is low; use the combined fit signals instead of relying only on the predicted role.",
                    "warning",
                )

        with quality_tab:
            render_navigation_section_title(
                "Resume Quality",
                "ATS compatibility, writing quality, structure advice, rewrites, and improvement planning.",
            )
            render_ats_section(ats_result, bool(job_description.strip()))
            template_message = template_detection.get("warning")
            if template_severity == "strong" and template_message:
                render_alert_banner(template_message, "warning")
            elif template_severity == "partial" and template_message:
                render_alert_banner(template_message, "info")
            render_sentence_quality_section(sentence_quality_result)
            render_structure_advisor(structure_advice)
            candidate_name = get_candidate_name_from_parser(parser_result)
            render_rewrite_suggestions_section(
                rewrite_suggestions,
                rewrite_summary,
                privacy_mode=privacy_mode,
                candidate_name=candidate_name,
            )
            render_resume_improvement_report(resume_improvement_report)

        with match_tab:
            render_navigation_section_title(
                "Job Match Intelligence",
                "Keyword, taxonomy, semantic, role-profile, and fit-score evidence for the target job.",
            )
            if job_description.strip():
                render_jd_keyword_match_section(match_score, matched_count, missing_count, gap)
            else:
                render_alert_banner("Paste a job description to unlock matched and missing skill analysis.", "info")
            render_skills_intelligence_section(resume_skills, gap, role_profile_summary, skill_taxonomy_result)
            candidate_name = get_candidate_name_from_parser(parser_result)
            render_semantic_match_section(
                semantic_result,
                privacy_mode=privacy_mode,
                candidate_name=candidate_name,
            )
            render_candidate_fit_section(candidate_fit_result, role_profile_summary)

        with recruiter_tab:
            render_navigation_section_title(
                "Recruiter Workspace",
                "Batch ranking, priority actions, manual notes, shortlist status, and CSV exports.",
            )
            render_batch_ranking_section(job_description, privacy_mode=privacy_mode)

        with model_tab:
            render_model_transparency_section(
                prediction_explanation=prediction_explanation,
                top_predictions=top_predictions,
                metrics=metrics,
                clean_classes=clean_classes,
                jd_skills=jd_skills,
                matched_count=matched_count,
                missing_count=missing_count,
                extra_count=extra_count,
            )
            render_resume_preview_section(
                parser_result=parser_result,
                resume_text=resume_text,
                job_description=job_description,
                template_detection=template_detection,
                template_severity=template_severity,
                privacy_mode=privacy_mode,
            )

        with privacy_tab:
            render_privacy_responsible_ai_section(privacy_mode)

        with assistant_tab:
            render_job_application_assistant_placeholder()

st.markdown(
    '<div class="footer-note">Built with Streamlit, scikit-learn, pandas, and pypdf. Designed as a responsible local resume intelligence dashboard.</div>',
    unsafe_allow_html=True,
)
