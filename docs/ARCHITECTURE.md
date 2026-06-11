# ResumeIQ Architecture

ResumeIQ is organized as a local-first resume intelligence system with an optional FastAPI backend. The Streamlit UI can run independently, and the backend can be used for API snapshots, health checks, copilot retrieval, and prompt-preview workflows.

## High-Level Architecture

```text
User
  |
  v
Streamlit UI (app.py)
  |
  | optional API client
  v
FastAPI Backend (backend/)
  |
  v
Core ResumeIQ Modules (src/)
  |
  +--> SQLite + SQLAlchemy (database/)
  +--> Model artifacts and registry (artifacts/, model_registry/)
  +--> Optional MLflow local tracking (experiment_tracking/)
  +--> Logs and monitoring metadata
```

## Component Responsibilities

### Streamlit UI

`app.py` controls the dashboard flow, tabs, user inputs, privacy mode, optional backend toggle, and display of analysis results. It should remain the UI layer and avoid owning reusable analysis logic.

### FastAPI Backend

`backend/` exposes API endpoints for health/readiness, resume analysis snapshots, local RAG copilot retrieval, and GenAI prompt previews. The backend uses local modules and does not call external AI providers.

### Core Modules

`src/` contains reusable product logic:

- Resume parsing and preprocessing.
- Role prediction and prediction explanation.
- Skill extraction, JD matching, ATS-style estimates, and semantic matching.
- Candidate fit scoring and batch ranking.
- Privacy masking, responsible AI demo content, monitoring helpers.
- Local RAG copilot and safe GenAI prompt-preview utilities.

### Database Layer

`database/` contains SQLAlchemy models, session setup, initialization, and repository helpers. Current persistence focuses on summaries, recruiter review records, API request metadata, and audit-style operational events. Full resume text and full job descriptions are not intentionally stored by default.

### Model Registry

The model registry stores local metadata and model-card style information under `artifacts/model_registry/`. It documents the baseline classifier and its known evaluation caveats.

### MLflow Tracking

MLflow support is optional and local. It is intended as an experiment-tracking foundation, not a production model registry claim.

### Docker

Docker Compose runs both the FastAPI backend and Streamlit UI with shared local SQLite volume storage. External GenAI remains disabled in Docker by default.

### GitHub Actions CI

CI installs dependencies, initializes the database, runs tests, imports the FastAPI app, validates Docker Compose config, and builds Docker images.

## Data Flows

### Single Resume Analysis

```text
Upload resume
  -> parse text
  -> preprocess text
  -> predict role
  -> extract skills
  -> compare against job description
  -> calculate ATS/job-fit signals
  -> explain and display
  -> optional summary save
```

### Batch Ranking

```text
Multiple resumes
  -> parse each resume
  -> run local analysis modules
  -> calculate candidate fit signals
  -> rank for recruiter review
  -> add manual notes/status
  -> export CSV and optional summary save
```

Batch ranking is a decision-support workflow. It does not make hiring decisions.

### Recruiter Copilot

```text
Resume/JD text in current session
  -> chunk resume and job description
  -> run TF-IDF retrieval
  -> select evidence snippets
  -> produce cautious local answer
  -> optionally return through FastAPI /copilot/ask
```

The copilot is local retrieval only. It does not call an external LLM.

### Prompt Preview

```text
Inputs and evidence
  -> safety checks
  -> privacy-aware prompt construction
  -> prompt preview object
  -> no external generation call
```

Prompt preview is a planning foundation for future optional GenAI features. Current behavior creates prompt objects only.

## Local Fallback Design

Streamlit remains the primary local workflow. If FastAPI is unavailable, the app continues using local analysis modules. When FastAPI is enabled and reachable, Streamlit can show backend snapshots while keeping local results available.

## Privacy-Aware Design

- Full resume text and full job descriptions are not intentionally stored in the database by default.
- Privacy-safe display mode masks common identifiers where supported.
- Resume evidence can be masked for display while keeping retrieval/scoring logic unchanged.
- Operational logs focus on metadata such as endpoint, status code, latency, and success state.
- Sensitive text is not intentionally logged.

## Architecture Principle

ResumeIQ separates UI, API, analysis logic, persistence, and documentation. This makes the project easier to test, explain, extend, and present as a portfolio-ready AI/ML engineering system.
