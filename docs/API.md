# ResumeIQ API Documentation

ResumeIQ exposes a FastAPI backend for local analysis snapshots, health checks, local RAG copilot retrieval, and GenAI prompt previews.

Run the backend:

```bash
uvicorn backend.main:app --reload --port 8000
```

Open Swagger docs:

```text
http://localhost:8000/docs
```

## Safety Notes

- The API uses local ResumeIQ modules.
- `/copilot/ask` uses local retrieval only. No external LLM is called.
- `/genai/prompt-preview` builds a prompt preview only. No external GenAI call is made.
- API request logs store operational metadata, not raw resume/JD text by design.
- ResumeIQ is a decision-support tool. Human review is required.

## `GET /`

**Purpose:** Basic root endpoint showing that the API is running.

**Example response fields:**

```json
{
  "app": "ResumeIQ API",
  "status": "running",
  "message": "Backend foundation is active."
}
```

## `GET /health`

**Purpose:** Lightweight health check.

**Example response fields:**

```json
{
  "status": "ok",
  "service": "ResumeIQ API"
}
```

## `GET /ready`

**Purpose:** Readiness check for local modules, configuration, database, registry, MLflow, RAG copilot, prompt builder, and GenAI settings.

**Example response fields:**

```json
{
  "status": "ready",
  "checks": {
    "api": "ok",
    "config": "loaded",
    "database": "available",
    "model_registry": "available",
    "mlflow": "optional_not_installed",
    "rag_copilot": "available",
    "genai_prompt_builder": "available",
    "external_genai": "disabled"
  }
}
```

**Safety note:** Readiness checks report system status only. They do not expose resume text.

## `POST /analyze-resume`

**Purpose:** Analyze resume text and optional job description through local ResumeIQ modules.

**Example request:**

```json
{
  "resume_text": "Candidate has Python, SQL, FastAPI, Docker, Streamlit, pandas, and machine learning project experience.",
  "job_description": "We are hiring for Python, SQL, machine learning, Docker, FastAPI, and deployment skills.",
  "privacy_mode": true
}
```

**Example response fields:**

```json
{
  "status": "success",
  "predicted_role": "Data Science",
  "model_confidence": 0.72,
  "ats_score": 81.0,
  "jd_match_score": 0.64,
  "matched_skills": ["python", "sql"],
  "missing_skills": ["deployment"],
  "priority_actions": ["Review missing skills against the target job."],
  "privacy_mode": true,
  "disclaimer": "Decision-support signal only. Human review required."
}
```

**Safety note:** This endpoint saves summary metadata when database logging is available. It does not intentionally store full resume text or full job descriptions by default.

## `POST /copilot/ask`

**Purpose:** Ask a recruiter-style question and retrieve local evidence snippets from the provided resume and job description.

**Example request:**

```json
{
  "query": "Which skills match the job description?",
  "resume_text": "Candidate has Python, SQL, machine learning, FastAPI, Docker, Streamlit, pandas, and scikit-learn project experience.",
  "job_description": "We are hiring for Python, SQL, machine learning, Docker, FastAPI, and deployment skills.",
  "privacy_mode": true,
  "candidate_name": "Example Candidate",
  "top_k": 5
}
```

**Example response fields:**

```json
{
  "status": "success",
  "answer": "Based on the provided resume and job description evidence, these snippets may help compare fit.",
  "question_type": "job_match",
  "evidence": [
    {
      "rank": 1,
      "source": "resume",
      "chunk_id": "resume_1",
      "score": 0.84,
      "text": "Candidate has Python, SQL, machine learning..."
    }
  ],
  "limitations": ["Evidence is based only on provided text."],
  "disclaimer": "Local retrieval only. Human review required.",
  "privacy_mode": true,
  "source": "fastapi_local_retrieval"
}
```

**Safety note:** Local retrieval only. No external LLM is called. Resume evidence can be privacy-masked for display when `privacy_mode` is true.

## `POST /genai/prompt-preview`

**Purpose:** Build a safe prompt-preview object for future optional GenAI workflows.

**Example request:**

```json
{
  "task_type": "resume_bullet_rewrite",
  "original_bullet": "Built a Streamlit resume analysis app using Python.",
  "target_role": "Machine Learning Engineer",
  "resume_evidence": ["Python, Streamlit, FastAPI, Docker project experience."],
  "job_description_evidence": ["Role asks for Python, deployment, and API skills."],
  "privacy_mode": true,
  "candidate_name": "Example Candidate",
  "consent_given": false
}
```

**Example response fields:**

```json
{
  "status": "success",
  "task_type": "resume_bullet_rewrite",
  "prompt_preview": {
    "allowed_for_external_use": false,
    "blocked_reason": "External GenAI is disabled or consent is missing."
  },
  "external_generation_enabled": false,
  "allowed_for_external_use": false,
  "blocked_reason": "External GenAI is disabled or consent is missing.",
  "disclaimer": "This endpoint builds a prompt preview only. It does not call external GenAI providers.",
  "source": "fastapi_prompt_preview"
}
```

Supported task types include:

- `resume_bullet_rewrite`
- `cover_letter`
- `recruiter_email`
- `linkedin_message`
- `interview_questions`
- `rag_answer_generation`
- `candidate_summary`
- `resume_gap_explanation`

**Safety note:** Prompt preview only. No external GenAI call. External generation remains disabled by default.
