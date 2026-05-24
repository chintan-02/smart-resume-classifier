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
from src.resume_parser import is_supported_file, parse_resume
from src.skill_extractor import (
    load_skills,
)

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_PAGE_ICON,
    layout=APP_LAYOUT,
    initial_sidebar_state=APP_INITIAL_SIDEBAR_STATE,
)


def inject_css() -> None:
    st.markdown(
        """
        <style>
        /* Keep the header present so the sidebar reopen arrow can appear */
        header[data-testid="stHeader"] {
            background: transparent !important;
        }

        /* Keep sidebar toggle visible */
        [data-testid="collapsedControl"] {
            display: flex !important;
            opacity: 1 !important;
            visibility: visible !important;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(99,102,241,0.16), transparent 28%),
                radial-gradient(circle at top right, rgba(16,185,129,0.12), transparent 24%),
                linear-gradient(180deg, #07111f 0%, #0a1326 45%, #07111f 100%);
        }

        .block-container {
            padding-top: 1.05rem !important;
            padding-bottom: 2.4rem;
            padding-left: 2rem;
            padding-right: 2rem;
            max-width: 1260px;
        }

        [data-testid="stAppViewContainer"] {
            padding-top: 0rem !important;
            margin-top: 0rem !important;
        }

        section[data-testid="stSidebar"] > div {
            padding-top: 1.2rem !important;
            background: linear-gradient(180deg, rgba(9,15,27,0.97), rgba(16,24,39,0.96));
        }

        .hero {
            background: linear-gradient(135deg, rgba(79,70,229,0.24), rgba(16,185,129,0.17));
            border: 1px solid rgba(255,255,255,0.09);
            padding: 1.8rem 1.8rem 1.4rem 1.8rem;
            border-radius: 28px;
            box-shadow: 0 18px 45px rgba(0,0,0,0.28);
            margin-bottom: 1.35rem;
        }

        .hero-badge {
            display: inline-block;
            padding: 0.36rem 0.78rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.12);
            color: #dbeafe;
            font-size: 0.82rem;
            font-weight: 600;
            margin-bottom: 0.9rem;
        }

        .hero-title {
            margin: 0;
            color: #f8fafc;
            font-size: 2.45rem;
            line-height: 1.1;
            font-weight: 800;
            letter-spacing: -0.03em;
        }

        .hero-subtitle {
            color: #dbe4ff;
            font-size: 1.02rem;
            line-height: 1.7;
            margin-top: 0.8rem;
            margin-bottom: 1.1rem;
            max-width: 950px;
        }

        .hero-chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem;
        }

        .hero-chip {
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.1);
            color: #eef2ff;
            padding: 0.45rem 0.8rem;
            border-radius: 999px;
            font-size: 0.84rem;
        }

        .panel-card {
            background: rgba(255,255,255,0.045);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 22px;
            padding: 1.15rem 1.15rem 1rem 1.15rem;
            box-shadow: 0 12px 28px rgba(0,0,0,0.18);
            margin-bottom: 1rem;
        }

        .metric-card {
            background: linear-gradient(180deg, rgba(255,255,255,0.055), rgba(255,255,255,0.04));
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 20px;
            padding: 1rem 1rem 0.95rem 1rem;
            min-height: 125px;
            box-shadow: 0 10px 24px rgba(0,0,0,0.14);
        }

        .metric-label {
            color: #b8c1d9;
            font-size: 0.85rem;
            margin-bottom: 0.45rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .metric-value {
            color: #ffffff;
            font-size: 1.75rem;
            font-weight: 800;
            line-height: 1.1;
        }

        .metric-subtext {
            color: #93c5fd;
            font-size: 0.86rem;
            margin-top: 0.45rem;
        }

        .section-label {
            color: #f8fafc;
            font-size: 1.08rem;
            margin-bottom: 0.7rem;
            font-weight: 700;
        }

        .minor-label {
            color: #e5e7eb;
            font-size: 0.96rem;
            font-weight: 600;
            margin-bottom: 0.35rem;
        }

        .subtle {
            color: #b8c1d9;
            font-size: 0.93rem;
            line-height: 1.75;
        }

        .skill-pill {
            display: inline-block;
            padding: 0.36rem 0.72rem;
            border-radius: 999px;
            margin: 0.18rem 0.26rem 0.18rem 0;
            background: rgba(99,102,241,0.18);
            border: 1px solid rgba(129,140,248,0.35);
            color: #eef2ff;
            font-size: 0.86rem;
        }

        .pill-green {
            background: rgba(16,185,129,0.18);
            border-color: rgba(52,211,153,0.45);
        }

        .pill-red {
            background: rgba(239,68,68,0.14);
            border-color: rgba(248,113,113,0.35);
        }

        .pill-slate {
            background: rgba(148,163,184,0.12);
            border-color: rgba(148,163,184,0.25);
        }

        [data-testid="stFileUploader"] {
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 18px;
            padding: 0.7rem;
        }

        [data-testid="stTextArea"] textarea {
            background: rgba(255,255,255,0.04) !important;
            color: #f8fafc !important;
            border: 1px solid rgba(255,255,255,0.08) !important;
            border-radius: 18px !important;
        }

        .stTextArea textarea, .stTextInput input {
            border-radius: 16px !important;
        }

        div[data-testid="stMetric"] {
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 18px;
            padding: 0.8rem;
        }

        hr {
            margin-top: 0.7rem !important;
            margin-bottom: 0.7rem !important;
            border: none !important;
            height: 0 !important;
        }

        .insight-box {
            background: rgba(255,255,255,0.045);
            border-left: 4px solid rgba(96,165,250,0.8);
            padding: 0.95rem 1rem;
            border-radius: 14px;
            color: #dbeafe;
            margin-top: 0.65rem;
            margin-bottom: 0.8rem;
            line-height: 1.65;
        }

        .footer-note {
            color: #94a3b8;
            font-size: 0.88rem;
            margin-top: 1.1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


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


def render_hero():
    st.markdown(
        """
        <div class="hero">
            <div class="hero-badge">Portfolio Project • NLP + ML + Dashboard UI</div>
            <div class="hero-title">📄 Smart Resume Classifier + Skill Extractor</div>
            <div class="hero-subtitle">
                An end-to-end resume intelligence dashboard that predicts likely job roles,
                extracts technical skills, compares resume content with a target job description,
                and highlights skill gaps for interview and application readiness.
            </div>
            <div class="hero-chip-row">
                <div class="hero-chip">Resume Classification</div>
                <div class="hero-chip">Skill Extraction</div>
                <div class="hero-chip">Job Matching</div>
                <div class="hero-chip">Gap Analysis</div>
                <div class="hero-chip">Azure Deployable</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def styled_metric(label: str, value: str, subtext: str = "") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-subtext">{subtext}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def pill_group(items, tone="default"):
    if not items:
        return '<span class="subtle">None</span>'
    tone_class = {
        "green": "pill-green",
        "red": "pill-red",
        "slate": "pill-slate",
    }.get(tone, "")
    return "".join([f'<span class="skill-pill {tone_class}">{item}</span>' for item in items])


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


def render_ats_section(ats_result: dict, has_job_description: bool) -> None:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">ATS Compatibility Score</div>', unsafe_allow_html=True)

    if not has_job_description:
        st.info("Paste a job description to calculate ATS compatibility.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    score_col, grade_col = st.columns([0.45, 0.55], gap="medium")
    with score_col:
        styled_metric("ATS Compatibility Score", f"{ats_result['ats_score']}%", "Estimated resume compatibility")
    with grade_col:
        styled_metric("Grade", ats_result["grade"], "Structure, keywords, skills, and alignment")

    st.write(ats_result["feedback"])

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
                "Score": [ats_result["breakdown"].get(key, 0) for key in breakdown_labels],
            }
        )
        st.dataframe(breakdown_df, use_container_width=True, hide_index=True)

        left, right = st.columns(2, gap="large")
        with left:
            st.markdown("##### Strengths")
            if ats_result["strengths"]:
                for strength in ats_result["strengths"]:
                    st.markdown(f"- {strength}")
            else:
                st.write("No strong ATS compatibility signals detected yet.")

        with right:
            st.markdown("##### Improvement suggestions")
            if ats_result["improvements"]:
                for improvement in ats_result["improvements"]:
                    st.markdown(f"- {improvement}")
            else:
                st.write("No major improvement suggestions detected.")

    st.caption(ats_result["disclaimer"])
    st.markdown("</div>", unsafe_allow_html=True)


def summarize_detected_sections(sections: dict) -> dict:
    return {
        section_name: bool(section_text.strip())
        for section_name, section_text in sections.items()
    }


inject_css()

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
    st.info("Upload a resume to unlock the full dashboard: prediction, confidence, skills, match score, and insights.")
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

        m1, m2, m3, m4 = st.columns(4, gap="medium")
        with m1:
            styled_metric("Predicted Role", predicted_role, "Top classification output")
        with m2:
            styled_metric("Model Confidence", confidence_display, "Highest class probability")
        with m3:
            styled_metric("Resume Skills", str(len(resume_skills)), "Skills extracted from resume")
        with m4:
            styled_metric("JD Match Score", f"{match_score:.2%}", "Overlap with target job skills")

        st.markdown(
            f"""
            <div class="insight-box">
                {build_summary_insight(predicted_role, match_score, matched_count, missing_count)}
            </div>
            """,
            unsafe_allow_html=True,
        )

        render_ats_section(ats_result, bool(job_description.strip()))

        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            ["Executive Summary", "Prediction Analytics", "Skills Intelligence", "Resume Preview", "Model Details"]
        )

        with tab1:
            a, b = st.columns([1.1, 0.9], gap="large")

            with a:
                st.markdown("#### Candidate fit summary")
                st.write(
                    f"""
                    This resume appears most aligned with **{predicted_role}**.
                    The dashboard suggests a **{match_score:.2%}** skill overlap against the target job description.
                    """
                )

                st.markdown("#### Key highlights")
                st.markdown(
                    f"""
                    - **Matched skills:** {matched_count}  
                    - **Missing skills:** {missing_count}  
                    - **Extra resume skills:** {extra_count}  
                    - **Model confidence:** {confidence_display}
                    """
                )

                if gap["missing"]:
                    st.warning("Most important missing skills: " + ", ".join(gap["missing"][:8]))
                else:
                    st.success("No missing skills identified from the supplied job description.")

            with b:
                st.markdown("#### Recruiter-style interpretation")
                if match_score >= 0.65:
                    st.success(get_match_feedback(match_score))
                elif match_score >= 0.35:
                    st.info(get_match_feedback(match_score))
                else:
                    st.error(get_match_feedback(match_score))

                st.markdown("#### Recommended next step")
                if missing_count > 0:
                    st.write("Focus resume improvement on the missing skills and tailor project descriptions accordingly.")
                else:
                    st.write("The candidate already aligns well. The next step is strengthening achievement-based bullet points.")

        with tab2:
            c1, c2 = st.columns([1.0, 1.0], gap="large")

            with c1:
                st.markdown("#### Top predicted roles")
                if not top_predictions.empty:
                    chart_df = top_predictions.set_index("Role")
                    st.bar_chart(chart_df["Confidence %"])
                    st.dataframe(top_predictions, use_container_width=True, hide_index=True)
                else:
                    st.write("Probability output is not available for this classifier.")

            with c2:
                st.markdown("#### Performance snapshot")
                if jd_skills:
                    analytics_df = pd.DataFrame(
                        {
                            "Metric": ["Matched Skills", "Missing Skills", "Extra Skills"],
                            "Count": [matched_count, missing_count, extra_count],
                        }
                    )
                    st.bar_chart(analytics_df.set_index("Metric"))
                    st.dataframe(analytics_df, use_container_width=True, hide_index=True)
                else:
                    st.info("Paste a job description to unlock job-match analytics.")

        with tab3:
            s1, s2 = st.columns(2, gap="large")

            with s1:
                st.markdown("#### Resume skills")
                st.markdown(pill_group(resume_skills), unsafe_allow_html=True)

                st.markdown("#### Matched skills")
                st.markdown(pill_group(gap["matched"], tone="green"), unsafe_allow_html=True)

            with s2:
                st.markdown("#### Missing skills")
                st.markdown(pill_group(gap["missing"], tone="red"), unsafe_allow_html=True)

                st.markdown("#### Extra resume skills")
                st.markdown(pill_group(gap["extra"], tone="slate"), unsafe_allow_html=True)

        with tab4:
            st.markdown("#### Extracted resume text")
            st.text_area("Resume text", resume_text[:8000], height=320, label_visibility="collapsed")

            with st.expander("Advanced parser information"):
                st.markdown("##### Detected sections")
                st.json(summarize_detected_sections(parser_result["sections"]))

                st.markdown("##### Contact info summary")
                st.json(parser_result["contact_info"])

                st.markdown("##### Estimated years of experience")
                years = parser_result["estimated_years_experience"]
                st.write(f"{years} years" if years is not None else "Not detected")

                st.markdown("##### Template detection")
                if template_severity == "strong":
                    st.warning(template_detection["warning"])
                elif template_severity == "partial":
                    st.info(template_detection["warning"])
                st.write(
                    {
                        "template_score": template_detection["template_score"],
                        "severity": template_detection.get("severity", "none"),
                        "matched_placeholders": template_detection["matched_placeholders"],
                        "real_content_signals": template_detection.get("real_content_signals", []),
                    }
                )

                st.markdown("##### Parsed resume items")
                st.write(
                    {
                        "education": parser_result["education"],
                        "experience": parser_result["experience"],
                        "projects": parser_result["projects"],
                        "certifications": parser_result["certifications"],
                    }
                )

            if job_description.strip():
                st.markdown("#### Job description text")
                st.text_area("Job description text", job_description[:5000], height=220, label_visibility="collapsed")

        with tab5:
            st.markdown("#### Model pipeline")
            st.code(
                "TF-IDF Vectorizer (1-2 grams, English stop words) -> Logistic Regression",
                language="text",
            )

            st.markdown("#### Stored evaluation metadata")
            if metrics:
                st.json({"accuracy": metrics.get("accuracy"), "available_roles": clean_classes})
            else:
                st.info("No metrics metadata file found.")

st.markdown(
    '<div class="footer-note">Built with Streamlit, scikit-learn, pandas, and pypdf. Designed as a portfolio-grade NLP + ML dashboard and ready for GitHub + Azure deployment.</div>',
    unsafe_allow_html=True,
)
