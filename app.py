import json
import pickle
from pathlib import Path

import pandas as pd
import streamlit as st

from utils import (
    clean_text,
    extract_skills,
    extract_text_from_pdf,
    extract_text_from_txt,
    jaccard_similarity,
    load_skills,
    skill_gap_analysis,
)

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "artifacts" / "resume_classifier.pkl"
SKILLS_PATH = BASE_DIR / "data" / "skills_list.txt"
METRICS_PATH = BASE_DIR / "artifacts" / "metrics.json"
SAMPLE_JD_PATH = BASE_DIR / "data" / "sample_job_description.txt"

st.set_page_config(
    page_title="Smart Resume Classifier",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(180deg, #0b1020 0%, #121a31 55%, #0b1020 100%);
        }
        .block-container {
            padding-top: 1.8rem;
            padding-bottom: 2.5rem;
            max-width: 1200px;
        }
        .hero {
            background: linear-gradient(135deg, rgba(99,102,241,0.20), rgba(16,185,129,0.16));
            border: 1px solid rgba(255,255,255,0.10);
            padding: 1.4rem 1.4rem 1.1rem 1.4rem;
            border-radius: 24px;
            margin-bottom: 1rem;
            box-shadow: 0 12px 35px rgba(0,0,0,0.18);
        }
        .hero h1 {
            margin: 0;
            font-size: 2.1rem;
            color: #f8fafc;
            letter-spacing: -0.02em;
        }
        .hero p {
            color: #dbe4ff;
            margin-top: 0.45rem;
            margin-bottom: 0.2rem;
            font-size: 1rem;
        }
        .glass-card {
            background: rgba(255,255,255,0.045);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 20px;
            padding: 1rem 1rem 0.95rem 1rem;
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
            margin-bottom: 0.9rem;
        }
        .metric-card {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 18px;
            padding: 0.95rem 1rem;
            min-height: 120px;
        }
        .metric-label {
            color: #b8c1d9;
            font-size: 0.88rem;
            margin-bottom: 0.4rem;
        }
        .metric-value {
            color: #ffffff;
            font-size: 1.7rem;
            font-weight: 700;
            line-height: 1.1;
        }
        .metric-subtext {
            color: #a7f3d0;
            font-size: 0.88rem;
            margin-top: 0.35rem;
        }
        .section-title {
            color: #f8fafc;
            font-size: 1.05rem;
            margin-bottom: 0.65rem;
            font-weight: 600;
        }
        .skill-pill {
            display: inline-block;
            padding: 0.34rem 0.68rem;
            border-radius: 999px;
            margin: 0.18rem 0.25rem 0.18rem 0;
            background: rgba(99,102,241,0.18);
            border: 1px solid rgba(129,140,248,0.35);
            color: #eef2ff;
            font-size: 0.88rem;
        }
        .pill-green { background: rgba(16,185,129,0.18); border-color: rgba(52,211,153,0.45); }
        .pill-red { background: rgba(239,68,68,0.14); border-color: rgba(248,113,113,0.35); }
        .pill-slate { background: rgba(148,163,184,0.12); border-color: rgba(148,163,184,0.25); }
        .subtle {
            color: #b8c1d9;
            font-size: 0.92rem;
        }
        .stTextArea textarea, .stTextInput input {
            border-radius: 14px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource
def load_model():
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)


@st.cache_data
def get_skills():
    return load_skills(str(SKILLS_PATH))


@st.cache_data
def get_metrics():
    if METRICS_PATH.exists():
        return json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    return {}


@st.cache_data
def load_sample_jd() -> str:
    return SAMPLE_JD_PATH.read_text(encoding="utf-8") if SAMPLE_JD_PATH.exists() else ""


model = load_model()
skills_list = get_skills()
metrics = get_metrics()


def render_hero():
    st.markdown(
        """
        <div class="hero">
            <h1>📄 Smart Resume Classifier + Skill Extractor</h1>
            <p>
                A polished end-to-end NLP + ML project that predicts likely job roles, extracts skills,
                compares a resume with a job description, and highlights missing skills in one dashboard.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )



def file_to_text(file) -> str:
    suffix = Path(file.name).suffix.lower()
    if suffix == ".pdf":
        return extract_text_from_pdf(file)
    if suffix == ".txt":
        return extract_text_from_txt(file)
    return ""



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
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba([text])[0]
        classes = model.classes_ if hasattr(model, "classes_") else model.named_steps["clf"].classes_
        df = pd.DataFrame({"Role": classes, "Probability": probs}).sort_values("Probability", ascending=False).head(top_n)
        df["Confidence %"] = (df["Probability"] * 100).round(2)
        return df[["Role", "Confidence %"]]
    return pd.DataFrame()


inject_css()
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
    st.markdown("### Local Run")
    st.code("python -m streamlit run app.py", language="bash")
    st.caption("Use `python -m streamlit` so Streamlit runs inside your venv.")

left, right = st.columns([1.15, 0.85], gap="large")

with left:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">1) Upload Resume</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload a resume in PDF or TXT format", type=["pdf", "txt"], label_visibility="collapsed")
    st.caption("Best results come from text-based PDFs, not scanned images.")
    st.markdown("</div>", unsafe_allow_html=True)

    default_jd = load_sample_jd() if use_sample_jd else ""
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">2) Paste Job Description</div>', unsafe_allow_html=True)
    job_description = st.text_area(
        "Paste job description",
        value=default_jd,
        height=210,
        label_visibility="collapsed",
        placeholder="Paste a Data Scientist / ML Engineer / Analyst job description here...",
    )
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">What this app does</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="subtle">
        • Predicts the most likely job role from resume text<br>
        • Extracts skills using a predefined skill dictionary<br>
        • Compares resume skills vs job description skills<br>
        • Highlights missing skills for quick gap analysis
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Suggested demo flow</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="subtle">
        1. Upload a resume<br>
        2. Paste a target job description<br>
        3. Show the predicted role<br>
        4. Explain matched vs missing skills<br>
        5. Discuss how recruiters could use the tool
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

if uploaded_file is None:
    st.info("Upload a resume to generate predictions, extracted skills, and skill gap analysis.")
else:
    resume_text = file_to_text(uploaded_file)
    resume_clean = clean_text(resume_text)

    if not resume_clean.strip():
        st.error("Could not extract readable text from the uploaded file. Try a text-based PDF or a TXT file.")
    else:
        predicted_role = model.predict([resume_clean])[0]
        top_predictions = get_top_predictions(resume_clean)
        confidence_display = "N/A"
        if not top_predictions.empty:
            confidence_display = f"{top_predictions.iloc[0]['Confidence %']:.2f}%"
        resume_skills = extract_skills(resume_clean, skills_list)

        jd_clean = clean_text(job_description) if job_description.strip() else ""
        jd_skills = extract_skills(jd_clean, skills_list) if jd_clean else []
        match_score = jaccard_similarity(resume_skills, jd_skills) if jd_skills else 0.0
        gap = skill_gap_analysis(resume_skills, jd_skills) if jd_skills else {"matched": [], "missing": [], "extra": sorted(resume_skills)}

        m1, m2, m3, m4 = st.columns(4, gap="medium")
        with m1:
            styled_metric("Predicted Role", predicted_role, "Top classification output")
        with m2:
            styled_metric("Model Confidence", confidence_display, "From class probabilities")
        with m3:
            styled_metric("Extracted Skills", str(len(resume_skills)), "Skills found in the resume")
        with m4:
            styled_metric("JD Match Score", f"{match_score:.2%}", "Overlap between resume and JD skills")

        tab1, tab2, tab3, tab4 = st.tabs(["Analysis Dashboard", "Skills Breakdown", "Resume Preview", "Model Details"])

        with tab1:
            col_a, col_b = st.columns([0.95, 1.05], gap="large")
            with col_a:
                st.markdown("#### Top predicted roles")
                if not top_predictions.empty:
                    chart_df = top_predictions.set_index("Role")
                    st.bar_chart(chart_df["Confidence %"])
                    st.dataframe(top_predictions, use_container_width=True, hide_index=True)
                else:
                    st.write("Probability output is not available for this classifier.")
            with col_b:
                st.markdown("#### Quick interpretation")
                st.success(f"This resume is most aligned with **{predicted_role}**.")
                if jd_skills:
                    st.write(f"The resume matches **{len(gap['matched'])}** target skills and misses **{len(gap['missing'])}** skills from the job description.")
                else:
                    st.write("Paste a job description to unlock match score and missing-skills analysis.")
                if gap["missing"]:
                    st.warning("Top missing skills: " + ", ".join(gap["missing"][:8]))

        with tab2:
            c1, c2 = st.columns(2, gap="large")
            with c1:
                st.markdown("#### Resume skills")
                st.markdown(pill_group(resume_skills), unsafe_allow_html=True)
                st.markdown("#### Matched skills")
                st.markdown(pill_group(gap["matched"], tone="green"), unsafe_allow_html=True)
            with c2:
                st.markdown("#### Missing skills")
                st.markdown(pill_group(gap["missing"], tone="red"), unsafe_allow_html=True)
                st.markdown("#### Extra resume skills")
                st.markdown(pill_group(gap["extra"], tone="slate"), unsafe_allow_html=True)

        with tab3:
            st.text_area("Extracted resume text", resume_text[:8000], height=360)
            if job_description.strip():
                st.text_area("Job description text", job_description[:5000], height=220)

        with tab4:
            st.markdown("#### Pipeline")
            st.code(
                "TF-IDF Vectorizer (1-2 grams, English stop words) -> Logistic Regression",
                language="text",
            )
            if metrics:
                st.json({"accuracy": metrics.get("accuracy"), "available_roles": clean_classes})

st.markdown("---")
st.caption("Built with Streamlit, scikit-learn, pandas, and pypdf. Azure-ready startup files are included in the repo.")
