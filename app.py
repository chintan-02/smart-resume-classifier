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
from src.jd_matcher import analyze_job_description_match, get_match_feedback
from src.prediction_service import get_top_predictions as get_model_top_predictions
from src.prediction_service import load_model_artifacts, predict_resume_role
from src.preprocessing import preprocess_resume_text
from src.report_builder import build_resume_improvement_report, get_report_summary_cards
from src.resume_parser import is_supported_file, parse_resume
from src.rewrite_suggestions import generate_rewrite_suggestions, get_rewrite_summary
from src.sentence_quality import detect_ai_like_sentences
from src.skill_extractor import (
    load_skills,
)
from src.ui.ui_components import (
    render_alert_banner,
    render_badge_group,
    render_empty_state,
    render_hero,
    render_metric_card,
    render_score_summary,
    render_section_title,
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
        render_metric_card("Predicted Role", predicted_role, "Top classification output")
    with c2:
        render_metric_card("Model Confidence", confidence_display, "Highest class probability")
    with c3:
        render_metric_card("ATS Score", f"{ats_result.get('ats_score', 0)}%", ats_result.get("grade"))
    with c4:
        render_metric_card("JD Match Score", f"{match_score:.2%}", "Skill overlap with target job")

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

    render_section_title("Recruiter-Style Interpretation")
    if match_score >= 0.65:
        render_alert_banner(get_match_feedback(match_score), "success")
    elif match_score >= 0.35:
        render_alert_banner(get_match_feedback(match_score), "info")
    else:
        render_alert_banner(get_match_feedback(match_score), "warning")

    render_section_title("Recommended Next Step")
    if missing_count > 0:
        st.write("Focus resume improvement on the missing skills and tailor project descriptions around the target role.")
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
            helper_text="Estimated resume compatibility",
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
        st.dataframe(breakdown_df, use_container_width=True, hide_index=True)

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


def summarize_detected_sections(sections: dict) -> dict:
    return {
        section_name: bool(section_text.strip())
        for section_name, section_text in sections.items()
    }


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

render_hero()

with st.sidebar:
    st.markdown("### Project Controls")
    use_sample_jd = st.toggle("Use sample ML/Data Science JD", value=False)

    st.markdown("---")
    st.markdown("### Model Snapshot")
    accuracy = metrics.get("accuracy", 0)
    st.metric("Validation accuracy", f"{accuracy:.2%}")

    classes = metrics.get("report", {}).keys()
    clean_classes = [c for c in classes if c not in {"accuracy", "macro avg", "weighted avg"}]
    st.caption(f"Supported roles: {', '.join(clean_classes[:10])}")

    st.markdown("---")
    st.markdown("### Why this project stands out")
    st.markdown(
        """
        <div class="subtle">
        • End-to-end NLP + ML workflow<br>
        • Recruiter-friendly use case<br>
        • Portfolio-quality dashboard UI<br>
        • Deployment-ready for Azure
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("### Local Run")
    st.code("python -m streamlit run app.py", language="bash")

top_left, top_right = st.columns([1.18, 0.82], gap="large")

with top_left:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">1) Upload Resume</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload a resume in PDF, TXT, or DOCX format",
        type=SUPPORTED_FILE_TYPES,
        label_visibility="collapsed",
    )
    st.caption("Best results come from text-based PDFs or DOCX files rather than scanned-image PDFs.")
    st.markdown("</div>", unsafe_allow_html=True)

    default_jd = load_sample_jd() if use_sample_jd else ""
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">2) Paste Job Description</div>', unsafe_allow_html=True)
    job_description = st.text_area(
        "Paste job description",
        value=default_jd,
        height=240,
        label_visibility="collapsed",
        placeholder="Paste a Data Scientist / ML Engineer / Analyst job description here...",
    )
    st.markdown("</div>", unsafe_allow_html=True)

with top_right:
    st.markdown(
        """
        <div class="panel-card">
            <div class="section-label">Dashboard Overview</div>
            <div class="subtle">
                This tool simulates a recruiter-assist workflow:
                it reads resume content, predicts the most likely role,
                extracts candidate skills, compares them against a target job,
                and surfaces missing skills for faster decision-making.
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
                3. Review predicted role and confidence<br>
                4. Examine skill match and missing skills<br>
                5. Explain how this supports hiring or candidate preparation
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
                Python • Streamlit • scikit-learn • pandas • pypdf • Azure Deployment
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

if uploaded_file is None:
    render_empty_state(
        "Upload a resume to begin",
        "Upload a PDF, DOCX, or TXT resume to unlock prediction, ATS compatibility, skill matching, writing-quality checks, and recruiter-style insights.",
    )
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

        match_analysis = analyze_job_description_match(resume_clean, job_description, skills_list)
        resume_skills = match_analysis["resume_skills"]
        jd_skills = match_analysis["jd_skills"]
        match_score = match_analysis["match_score"]
        gap = match_analysis["gap"]

        matched_count = len(gap["matched"])
        missing_count = len(gap["missing"])
        extra_count = len(gap["extra"])
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

        (
            overview_tab,
            ats_tab,
            quality_tab,
            skills_tab,
            rewrite_tab,
            preview_tab,
            model_tab,
        ) = st.tabs(
            [
                "Overview",
                "ATS & Job Match",
                "Resume Quality",
                "Skills Intelligence",
                "Rewrite Suggestions",
                "Resume Preview",
                "Model Details",
            ]
        )

        with overview_tab:
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
            render_resume_improvement_report(resume_improvement_report)

        with ats_tab:
            render_ats_section(ats_result, bool(job_description.strip()))
            render_section_title("Job Description Match", "Skill overlap between the resume and target role.")

            jm1, jm2, jm3 = st.columns(3, gap="medium")
            with jm1:
                render_score_summary("JD Match Percentage", f"{match_score:.2%}", helper_text="Resume/JD skill overlap")
            with jm2:
                render_metric_card("Matched Skills", matched_count, "Skills found in both resume and JD")
            with jm3:
                render_metric_card("Missing Skills", missing_count, "JD skills not detected in resume")

            if job_description.strip():
                st.markdown("##### Matched skills")
                render_badge_group(gap.get("matched", []))
                st.markdown("##### Missing skills")
                render_badge_group(gap.get("missing", []))
            else:
                render_alert_banner("Paste a job description to unlock matched and missing skill analysis.", "info")

        with quality_tab:
            template_message = template_detection.get("warning")
            if template_severity == "strong" and template_message:
                render_alert_banner(template_message, "warning")
            elif template_severity == "partial" and template_message:
                render_alert_banner(template_message, "info")
            render_sentence_quality_section(sentence_quality_result)

        with skills_tab:
            render_section_title(
                "Skills Intelligence",
                "Extracted resume skills, target-job overlap, missing skills, and additional resume strengths.",
            )
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

        with rewrite_tab:
            render_section_title(
                "Humanized Rewrite Suggestions",
                "These suggestions are local and template-based. They do not invent achievements. Replace placeholders with your real details.",
            )

            if not rewrite_suggestions:
                render_empty_state(
                    "No rewrite suggestions yet",
                    "ResumeIQ generates rewrite suggestions when it finds generic, vague, or AI-like sentences.",
                )
            else:
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

                for index, suggestion in enumerate(rewrite_suggestions, start=1):
                    with st.expander(f"{index}. {suggestion.get('issue', 'Rewrite suggestion')}", expanded=index == 1):
                        st.markdown("##### Original sentence")
                        st.write(suggestion.get("original_sentence", ""))

                        st.markdown("##### Issue")
                        st.write(suggestion.get("issue", ""))

                        st.markdown("##### Why it may be weak")
                        st.write(suggestion.get("why_weak", ""))

                        st.markdown("##### Suggested rewrite template")
                        st.write(suggestion.get("suggested_rewrite", ""))

                        st.markdown("##### Stronger resume version")
                        st.write(suggestion.get("stronger_resume_version", ""))

                        st.markdown("##### Rewrite tip")
                        st.write(suggestion.get("rewrite_tip", ""))

        with preview_tab:
            render_section_title(
                "Resume Preview",
                "Extracted text and parser details used by the current analysis pipeline.",
            )
            st.markdown("##### Extracted resume text")
            st.text_area("Resume text", resume_text[:8000], height=320, label_visibility="collapsed")

            with st.expander("Parser details", expanded=False):
                sections = parser_result.get("sections", {})
                if sections:
                    st.markdown("##### Detected sections")
                    st.json(summarize_detected_sections(sections))

                contact_info = parser_result.get("contact_info")
                if contact_info:
                    st.markdown("##### Contact summary")
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

        with model_tab:
            render_section_title(
                "Model Details",
                "Current baseline classifier metadata and probability output.",
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

            st.markdown("##### Prediction probabilities")
            if not top_predictions.empty:
                chart_df = top_predictions.set_index("Role")
                st.bar_chart(chart_df["Confidence %"])
                st.dataframe(top_predictions, use_container_width=True, hide_index=True)
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
                st.dataframe(analytics_df, use_container_width=True, hide_index=True)

st.markdown(
    '<div class="footer-note">Built with Streamlit, scikit-learn, pandas, and pypdf. Designed as a portfolio-grade NLP + ML dashboard and ready for GitHub + Azure deployment.</div>',
    unsafe_allow_html=True,
)
