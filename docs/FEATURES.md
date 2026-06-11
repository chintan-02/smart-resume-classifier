# ResumeIQ Features

This document explains ResumeIQ features in product terms and engineering terms. Each feature is a decision-support signal and should be reviewed by a human.

## 1. Candidate Analysis

**What it does:** Parses uploaded resumes, predicts a likely resume category, extracts skills, and summarizes high-level signals.

**Why it matters:** Gives recruiters, evaluators, and project reviewers a fast overview of the resume content and model output.

**Current status:** Implemented in the Streamlit dashboard and supported by reusable modules under `src/`.

**Limitation:** The baseline classifier is not a production hiring model. Confidence should be treated as one signal.

## 2. Resume Quality

**What it does:** Reviews generic or vague resume sentences, provides local rewrite suggestions, and gives structure/format guidance.

**Why it matters:** Helps candidates improve clarity, specificity, and recruiter readability.

**Current status:** Implemented with local rule/template-based logic.

**Limitation:** Suggestions do not invent metrics, achievements, employers, or experience.

## 3. Job Match Intelligence

**What it does:** Compares resume skills and text against a target job description using keyword, ATS-style, taxonomy, and semantic signals.

**Why it matters:** Helps explain where a resume aligns with a target role and where gaps may exist.

**Current status:** Implemented locally in the dashboard.

**Limitation:** Scores are estimates based only on the provided resume and job description.

## 4. Recruiter Workspace

**What it does:** Supports batch resume ranking, recruiter notes, shortlist status, CSV export, and local evidence search.

**Why it matters:** Demonstrates a realistic recruiter workflow beyond single-resume analysis.

**Current status:** Implemented with local analysis, optional summary saving, and session-local review controls.

**Limitation:** Rankings are decision-support signals and should not be used as automated screening decisions.

## 5. Privacy & Responsible AI

**What it does:** Provides privacy-safe display mode, synthetic/demo fairness dashboard content, and responsible AI boundaries.

**Why it matters:** Resume data can contain sensitive personal information. The project explicitly documents safe use.

**Current status:** Implemented as UI controls, masking utilities, and documentation.

**Limitation:** Privacy-safe mode reduces visible PII but does not guarantee full anonymization.

## 6. Model Transparency

**What it does:** Shows model confidence, prediction explanations, model registry metadata, model-card notes, and optional MLflow experiment tracking.

**Why it matters:** Helps evaluators understand that the model is inspectable and has known limitations.

**Current status:** Implemented as local transparency foundations.

**Limitation:** The baseline model reports very high validation accuracy and should be investigated for possible leakage, small validation split, class imbalance, or overfitting.

## 7. Backend/API

**What it does:** Provides FastAPI endpoints for health, readiness, resume analysis, copilot retrieval, and GenAI prompt preview.

**Why it matters:** Shows how ResumeIQ can be separated into frontend and backend layers.

**Current status:** Implemented as an optional backend. Streamlit local fallback remains available.

**Limitation:** The backend is a foundation, not a hardened production service.

## 8. Database

**What it does:** Stores analysis summaries, batch review metadata, recruiter review records, audit-style events, and API request metadata.

**Why it matters:** Demonstrates persistence without storing full sensitive resume/JD content by default.

**Current status:** Implemented with SQLite and SQLAlchemy.

**Limitation:** SQLite is appropriate for local development and demos. PostgreSQL or another managed database would be more appropriate for production.

## 9. Docker/CI

**What it does:** Runs Streamlit and FastAPI through Docker Compose and validates tests/builds in GitHub Actions.

**Why it matters:** Demonstrates reproducible development and CI discipline.

**Current status:** Dockerfiles, Compose config, and CI workflow are implemented.

**Limitation:** The project does not claim a production deployment from the current Docker setup.

## 10. RAG Copilot

**What it does:** Chunks resume/JD text, retrieves relevant evidence using local TF-IDF logic, and returns cautious recruiter-style answers.

**Why it matters:** Demonstrates evidence-based retrieval without using external LLMs.

**Current status:** Implemented in Streamlit and FastAPI `/copilot/ask`.

**Limitation:** It is local retrieval only. It does not generate free-form LLM answers.

## 11. GenAI Planning / Prompt Preview

**What it does:** Builds safe prompt-preview objects for future resume bullet, cover letter, recruiter email, LinkedIn message, interview prep, RAG answer, summary, and gap explanation tasks.

**Why it matters:** Shows responsible planning for future GenAI without prematurely sending private data to external providers.

**Current status:** Prompt preview is implemented locally and through FastAPI `/genai/prompt-preview`.

**Limitation:** External GenAI generation is disabled by default. No external AI provider call is made.
