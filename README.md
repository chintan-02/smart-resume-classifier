# ResumeIQ — AI Resume Intelligence & Job Application Assistant

A privacy-aware AI resume intelligence platform for resume analysis, job-description matching, recruiter-ready fit signals, and responsible decision-support workflows.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?logo=streamlit&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![Pytest](https://img.shields.io/badge/Tests-Pytest-0A9EDC)

**Decision-support tool. Human review required.**

ResumeIQ is designed as a portfolio/capstone-ready engineering project under active development. It demonstrates practical software engineering, local ML/NLP workflows, responsible AI boundaries, backend API design, database foundations, Docker, CI, and documentation.

## Live Demo

[https://resume-classifier-chintan.azurewebsites.net](https://resume-classifier-chintan.azurewebsites.net/)

## Feature Highlights

- Resume parsing for PDF, DOCX, and TXT resumes.
- Role prediction using a local baseline ML model.
- ATS compatibility estimate for resume structure and content signals.
- Job-description keyword matching.
- Semantic matching between resume content and job descriptions.
- Skill taxonomy for normalized skill intelligence.
- Resume quality review.
- AI-like/generic sentence detection.
- Humanized rewrite suggestions.
- Resume structure advisor.
- Candidate fit scoring for review support, not hiring automation.
- Batch resume ranking.
- Recruiter notes and shortlist workflow.
- Privacy-safe display mode for masking common personal identifiers.
- Responsible AI dashboard using synthetic/demo data only.
- Model transparency, explainability, local model registry, and MLflow foundation.
- FastAPI backend foundation with Streamlit fallback behavior.
- SQLite + SQLAlchemy database foundation.
- Docker Compose development setup.
- GitHub Actions CI.
- Azure App Service deployment work.
- Local RAG recruiter copilot foundation for evidence search.
- Safe GenAI prompt preview foundation with external GenAI disabled by default.

## Architecture Overview

```text
Streamlit UI
    |
    | optional FastAPI client
    v
FastAPI Backend
    |
    v
ResumeIQ Analysis Modules
    |
    v
SQLite + SQLAlchemy / Model Registry / Logging
    |
    v
Azure App Service Deployment
```

The current product shape is:

```text
Streamlit UI -> optional FastAPI backend -> ResumeIQ analysis modules -> SQLite/model registry/logging -> Azure deployment
```

The Streamlit app remains usable even when the FastAPI backend is offline. When the backend is enabled and reachable, Streamlit can show API snapshots while keeping local analysis available as the fallback path. The backend and database foundations prepare the project for production-style API, persistence, audit, and deployment workflows without turning the app into an automated hiring system.

For details, see [Architecture](docs/ARCHITECTURE.md).

## How It Works

```text
Upload resume
    -> parse text
    -> preprocess content
    -> predict role
    -> extract skills
    -> compare job description
    -> compute ATS, semantic, and fit signals
    -> generate report
    -> support recruiter workflow
```

In simple terms, ResumeIQ turns an uploaded resume into structured signals that help a reviewer understand strengths, gaps, skill alignment, and writing quality. Technically, the app combines document parsing, text preprocessing, baseline ML classification, rule-based scoring, semantic matching, local retrieval, and responsible decision-support UI patterns.

## Quick Start

### Local Streamlit App

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m database.init_db
python scripts/register_baseline_model.py
streamlit run app.py --server.fileWatcherType none
```

Open the app at:

```text
http://localhost:8501
```

### FastAPI Backend

```bash
uvicorn backend.main:app --reload --port 8000
```

Open the API docs at:

```text
http://localhost:8000/docs
```

### Docker

```bash
docker compose up --build
```

Docker starts:

- Streamlit UI: `http://localhost:8501`
- FastAPI backend: `http://localhost:8000`
- FastAPI docs: `http://localhost:8000/docs`

### Tests

```bash
pytest
```

## Tech Stack

- Python
- Streamlit
- FastAPI
- scikit-learn
- pandas
- SQLite
- SQLAlchemy
- Docker
- GitHub Actions
- Azure App Service

## API Summary

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/` | API root/status message |
| `GET` | `/health` | Basic health check |
| `GET` | `/ready` | Readiness checks for config, database, registry, MLflow, RAG, and prompt builder |
| `GET` | `/version` | Version and build metadata |
| `POST` | `/analyze-resume` | Local resume/JD analysis snapshot |
| `POST` | `/copilot/ask` | Local retrieval-based recruiter copilot evidence search |
| `POST` | `/genai/prompt-preview` | Safe prompt preview only; no external GenAI call |

See [API Documentation](docs/API.md).

## Privacy and Responsible AI

ResumeIQ is a decision-support tool. Human review is required. It is not an automated hiring decision system.

- It does not intentionally store full resume text or full job descriptions by default.
- Privacy-safe mode masks common PII in displays and exports where supported.
- The fairness dashboard uses synthetic/demo data only.
- The system does not score protected attributes.
- The baseline model's high validation accuracy should be reviewed for possible data leakage, small validation split, class imbalance, or overfitting.
- External GenAI is disabled by default.
- Human review is required before any hiring or application action.

See [Responsible AI](docs/RESPONSIBLE_AI.md).

## GenAI Status

Current status:

- Local prompt previews only.
- No external AI provider calls.
- No API keys required.
- Prompt previews include safety checks and external-use blocking reasons.

Future optional external generation would require explicit consent, PII redaction, provider configuration through environment variables, safe fallback behavior, and human review.

## Project Status

ResumeIQ is a portfolio/capstone-ready engineering project under active development. It is built to demonstrate practical AI/ML product engineering, not to replace recruiter judgment or make automated hiring decisions.

## Portfolio Documentation

- [Setup](docs/SETUP.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Features](docs/FEATURES.md)
- [Responsible AI](docs/RESPONSIBLE_AI.md)
- [Roadmap](docs/ROADMAP.md)
- [Screenshots Guide](docs/SCREENSHOTS.md)
- [Deployment Sync Checklist](docs/portfolio/DEPLOYMENT_SYNC_CHECKLIST.md)
- [API](docs/API.md)
- [Development Notes](docs/DEVELOPMENT_NOTES.md)

## Optional Portfolio Artifacts

The following generated HTML learning files can be added later as optional portfolio artifacts. They are intentionally listed without links until the files exist in the repository:

- ResumeIQ Project Deep Dive HTML
- ResumeIQ Interview Cheat Sheet HTML
- ResumeIQ Professor Report HTML
- ResumeIQ Presentation Slides HTML

## Portfolio Presentation Pack

- [Screenshot Capture Plan](docs/portfolio/SCREENSHOT_CAPTURE_PLAN.md)
- [Project Presentation Script](docs/portfolio/PROJECT_PRESENTATION_SCRIPT.md)
- [LinkedIn Featured Description](docs/portfolio/LINKEDIN_FEATURED_DESCRIPTION.md)
- [Interview Talking Points](docs/portfolio/INTERVIEW_TALKING_POINTS.md)
- [One-Page Project Summary](docs/portfolio/PROJECT_ONE_PAGE_SUMMARY.md)

## Limitations

- The baseline model should be reviewed before production use.
- Very high validation accuracy can indicate leakage, overfitting, or dataset issues.
- Streamlit is currently used as a portfolio prototype.
- A production version may use a React/Next.js frontend with a FastAPI backend.
- GenAI is planned safely, but external GenAI calls are disabled by default.

## Roadmap

- React/Next.js frontend migration.
- Stronger semantic model.
- RAG recruiter copilot improvements.
- Authentication and role-based access control.
- PostgreSQL or another cloud database.
- Monitoring and deployment hardening.
- Better model evaluation and governance.
