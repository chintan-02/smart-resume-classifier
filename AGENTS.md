# Project Instructions for Codex

You are helping improve this project as a portfolio-ready AI/ML application while also teaching me how to think like a Software Engineer, AI/ML Engineer, and MLOps Engineer.

This project is called ResumeIQ — AI Resume Intelligence & Job Application Assistant.

Previous project name:
Smart Resume Classifier + Skill Extractor

Repository name:
smart-resume-classifier

ResumeIQ is the current product name used for the app UI, README, portfolio, resume, GitHub description, and future deployment positioning. The previous name is kept only for historical context because the original project started as a resume classifier and skill extractor.

The app analyzes resumes, predicts a resume/job category, extracts skills, compares resume content with a job description, checks ATS-style compatibility, detects generic or AI-like writing, and gives resume improvement guidance.

The goal is not only to finish features, but also to help me understand architecture, debugging, clean code, AI/ML thinking, and production-ready project development.

---

## General Rules

* Modify only the files needed for the requested task.
* Do not redesign the whole app unless explicitly asked.
* Do not create future roadmap folders or files early.
* Reuse existing project structure, styles, functions, and naming patterns.
* Keep code clean, simple, modular, and beginner-readable.
* Avoid unnecessary complexity.
* Prefer small, focused changes instead of large refactors.
* Do not break the existing workflow.
* Preserve current functionality unless the task specifically asks to change it.
* Keep the app portfolio-ready and recruiter-friendly.

---

## My Learning Style

Assume I am still learning software engineering and AI/ML engineering.

When explaining changes, use two levels:

### 1. Simple Explanation

Explain the idea in beginner-friendly language.

Example:
Instead of only saying:
“We need to refactor this into a reusable function.”

Also explain:
“This means we are taking repeated code and putting it into one small reusable block, so we do not copy-paste the same logic again and again.”

### 2. Technical Explanation

Also teach the correct technical term.

Example:

* Simple: Put repeated code in one place.
* Technical: Create a reusable function to reduce duplication and improve maintainability.

---

## How Codex Should Help

When solving coding problems:

1. Explain what the problem is in simple words.
2. Explain the technical reason.
3. Make the smallest safe fix.
4. Explain why the fix works.
5. Mention what mistake to avoid next time.
6. Mention what files changed.
7. Mention how to test the change.

Do not only solve the problem. Teach me how to think through the problem.

---

## Architecture Rules

Before adding a new feature, think about where the code belongs.

### Simple Meaning

Do not put everything inside app.py.

app.py should mainly control the Streamlit screen and user flow.

Reusable logic should live inside src/.

### Technical Meaning

Keep the UI layer, business logic, parsing logic, scoring logic, and ML logic separated.

Current project structure includes:

```text
app.py
train.py
requirements.txt
src/
  resume_parser.py
  preprocessing.py
  prediction_service.py
  skill_extractor.py
  jd_matcher.py
  ats_scorer.py
  sentence_quality.py
  ui/
    __init__.py
    ui_styles.py
    ui_components.py
```

Do not move existing modules into new architecture folders until a future step asks for it.

---

## ResumeIQ Project-Specific Rules

This is a resume intelligence and ATS-style analysis project.

The app can give feedback, but it must not make final hiring decisions.

Use safe wording like:

* “Recommended for review”
* “Strong match”
* “Needs improvement”
* “Low match based on available resume content”
* “This sentence may sound generic, vague, or AI-like”

Avoid unsafe wording like:

* “Hire this person”
* “Reject this person”
* “This candidate is not suitable”
* “This person is better than another person”
* “This resume is definitely AI-generated”

This project is a decision-support tool, not an automated hiring decision system.

---

## Resume Scoring Rules

* Keep scoring explainable.
* Do not invent fake resume metrics.
* Do not invent fake work experience.
* Do not invent fake tools, companies, achievements, or measurable results.
* If suggesting stronger resume bullets, use placeholders when needed:

  * [add measurable result]
  * [tool/library]
  * [business impact]
  * [project name]
* ATS Compatibility Score must be described as an estimate, not an official ATS platform score.
* Job match score must be based only on available resume and job description content.
* Do not score protected attributes.
* Do not make automatic hiring decisions.

---

## AI/ML Rules

* Do not add external APIs unless the task explicitly asks for it.
* Use local and rule-based logic first.
* Explain what is rule-based, what is model-based, and what is only a recommendation.
* Do not add model comparison too early.
* Do not retrain models unless the task asks for it.
* Do not claim model performance without evidence.
* The current TF-IDF + Logistic Regression baseline is useful for demonstration, but the 100% validation accuracy is a red flag to investigate later.
* Low confidence on real resumes should be fixed later using better evaluation, model comparison, and calibration.

Relevant future ML concepts:

* preprocessing
* feature engineering
* model evaluation
* inference
* confidence score
* calibration
* overfitting
* bias
* fairness
* monitoring

---

## Privacy and Responsible AI Rules

Resume data can contain personal information.

Be careful with:

* names
* email addresses
* phone numbers
* addresses
* LinkedIn/GitHub links
* work history
* education history

Do not send resume data to external APIs unless a future step adds:

* user consent
* PII masking
* timeout handling
* fallback behavior
* privacy-safe prompts

Do not build features that discriminate based on personal or sensitive characteristics.

---

## UI/UX Rules

The app should feel like a clean, premium, recruiter-friendly product.

For UI work:

* Keep the interface simple and understandable.
* Avoid clutter.
* Use clear tabs and sections.
* Use cards, badges, alerts, and summaries carefully.
* Keep dark theme readable.
* Do not make UI flashy or distracting.
* Do not break existing Streamlit workflow.
* Reuse src/ui/ui_styles.py and src/ui/ui_components.py after Step 4A.

Current Step 4A tabs:

1. Overview
2. ATS & Job Match
3. Resume Quality
4. Skills Intelligence
5. Rewrite Suggestions
6. Resume Preview
7. Model Details

Rewrite Suggestions tab should stay as a coming-soon section until Step 4B.

---

## Current Completed Steps

Step 0 completed:

* Modular src/ structure.
* Commit: 334917a

Step 1 completed:

* Advanced resume parser.
* PDF/DOCX/TXT extraction.
* DOCX table extraction.
* Template/incomplete resume detection.
* Commit: c47cd9a

Step 2 completed:

* ATS Compatibility Score.
* File: src/ats_scorer.py
* Commit: 3b5db2e

Step 3 completed:

* AI-like/generic sentence detection.
* File: src/sentence_quality.py
* Commit: 2c97b72

Step 4A completed:

* Premium UI/UX restructure.
* Files:

  * src/ui/__init__.py
  * src/ui/ui_styles.py
  * src/ui/ui_components.py
* Dashboard organized into recruiter-friendly tabs.

Current next step:
Step 4B — Humanized Resume Rewrite Suggestions

Do not skip ahead unless asked.

---

## Future Roadmap Order

Follow the roadmap step by step.

Step 4B:
Humanized Resume Rewrite Suggestions

Step 5:
Resume Improvement Report

Step 5.5:
Resume Structure & Format Advisor

Step 6:
Skill Taxonomy Engine

Step 7:
Semantic JD-Resume Matching

Step 8:
Multi-Score Candidate Fit System

Step 9:
Role-Specific Scoring Profiles

Step 10:
Batch Resume Ranking

Step 11:
Recruiter Notes and Shortlist Workflow

Step 12:
Prediction Explainability

Step 13:
Privacy-Safe / Anonymized Screening

Step 14:
Fairness Dashboard using synthetic/demo data only

Step 15:
FastAPI Backend

Step 16:
Streamlit-FastAPI Connection

Step 17:
Database Design

Step 18:
Audit Logs

Step 19:
Unit Tests

Step 20:
API Tests

Step 21:
Code Quality Tools

Step 22:
Model Comparison and Evaluation

Step 23:
MLflow Experiment Tracking

Step 24:
Docker

Step 25:
GitHub Actions CI/CD

Step 26:
Application Logging

Step 27:
Model Monitoring

Step 28:
Resume/JD Vector Store for RAG

Step 29:
RAG Recruiter Copilot

Step 29.5:
GenAI Job Application Assistant

Step 30:
README Upgrade

Step 31:
Screenshots and Demo Assets

Step 32:
Resume, LinkedIn, GitHub Positioning

---

## Testing Rules

After changes, explain:

1. What command to run
2. What files changed
3. What result I should expect
4. What possible risks exist

Common commands:

```bash
streamlit run app.py
```

```bash
python train.py
```

```bash
git status
```

```bash
git diff
```

Do not run heavy commands unless needed.

---

## Git Rules

Before coding, understand the current task.

After coding, summarize:

* files changed
* what changed
* why it changed
* how to test
* any assumptions

Do not commit automatically unless I ask.

---

## What Not To Do

* Do not add external APIs now.
* Do not add OpenAI/LLM calls now.
* Do not add database now.
* Do not add FastAPI now.
* Do not add Docker now.
* Do not add model comparison now.
* Do not create all future folders now.
* Do not invent fake resume content.
* Do not make hiring decisions.
* Do not claim official ATS accuracy.
* Do not make large unrelated refactors.
* Do not remove existing working features.

---

## Important Rule

Do not only solve the problem.

Teach me how to think through the problem so I can become better at software engineering, AI/ML engineering, architecture, debugging, and building portfolio-ready projects.
