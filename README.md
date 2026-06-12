# ResumeIQ — AI Resume Intelligence & Job Application Assistant

ResumeIQ is a privacy-aware resume intelligence platform that analyzes resumes against job descriptions, provides recruiter-ready fit signals, supports batch ranking and review workflows, and includes local RAG-style evidence search and safe GenAI planning foundations.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?logo=streamlit&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![Pytest](https://img.shields.io/badge/Tests-Pytest-0A9EDC)

**Decision-support tool. Human review required.**

ResumeIQ is designed as a portfolio/capstone-ready engineering project under active development. It demonstrates practical software engineering, local ML/NLP workflows, responsible AI boundaries, backend API design, database foundations, Docker, CI, and documentation.

## Feature Highlights

- Resume parsing and classification for PDF, DOCX, and TXT resumes.
- ATS compatibility estimate and job-description keyword match.
- Resume quality review, structure advice, and local rewrite suggestions.
- Skill taxonomy, role fit, and semantic JD-resume matching.
- Candidate fit scoring for review support, not hiring automation.
- Batch resume ranking with recruiter notes and shortlist workflow.
- Privacy-safe display mode for masking common personal identifiers.
- Responsible AI demo dashboard using synthetic/demo data only.
- Model transparency, explainability, local model registry, and MLflow foundation.
- Optional FastAPI backend with local Streamlit fallback.
- SQLite + SQLAlchemy database foundation for summaries and request metadata.
- Docker Compose development setup and GitHub Actions CI.
- Local RAG recruiter copilot for evidence search.
- Safe GenAI prompt preview foundation with external GenAI disabled by default.

## Architecture Overview

```text
Streamlit UI
    |
    | optional API client
    v
FastAPI Backend
    |
    v
Core ResumeIQ Modules
    |
    v
SQLite + SQLAlchemy
    |
    v
Model Registry / MLflow / Logs
```

The Streamlit app remains usable even when the FastAPI backend is offline. When the backend is enabled and reachable, Streamlit can show API snapshots while keeping local analysis available as the fallback path.

For details, see [Architecture](docs/ARCHITECTURE.md).

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

## API Summary

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/` | API root/status message |
| `GET` | `/health` | Basic health check |
| `GET` | `/ready` | Readiness checks for config, database, registry, MLflow, RAG, and prompt builder |
| `POST` | `/analyze-resume` | Local resume/JD analysis snapshot |
| `POST` | `/copilot/ask` | Local retrieval-based recruiter copilot evidence search |
| `POST` | `/genai/prompt-preview` | Safe prompt preview only; no external GenAI call |

See [API Documentation](docs/API.md).

## Privacy and Responsible AI

ResumeIQ is a decision-support system, not an automated hiring decision system.

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

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Features](docs/FEATURES.md)
- [Setup](docs/SETUP.md)
- [API](docs/API.md)
- [Responsible AI](docs/RESPONSIBLE_AI.md)
- [Roadmap](docs/ROADMAP.md)
- [Screenshots Guide](docs/SCREENSHOTS.md)
- [Development Notes](docs/DEVELOPMENT_NOTES.md)

## Portfolio Presentation Pack

- [Screenshot Capture Plan](docs/portfolio/SCREENSHOT_CAPTURE_PLAN.md)
- [Project Presentation Script](docs/portfolio/PROJECT_PRESENTATION_SCRIPT.md)
- [LinkedIn Featured Description](docs/portfolio/LINKEDIN_FEATURED_DESCRIPTION.md)
- [Interview Talking Points](docs/portfolio/INTERVIEW_TALKING_POINTS.md)
- [One-Page Project Summary](docs/portfolio/PROJECT_ONE_PAGE_SUMMARY.md)
