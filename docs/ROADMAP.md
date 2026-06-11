# ResumeIQ Roadmap

This roadmap describes current project status and likely next engineering phases. It is not a production deployment claim.

## Completed

- Core resume intelligence.
- Resume parsing for PDF, DOCX, and TXT.
- Role prediction baseline using TF-IDF and Logistic Regression.
- Skill extraction and job-description matching.
- ATS-style compatibility estimate.
- Resume quality review and local rewrite suggestions.
- Resume structure advisor.
- Skill taxonomy and role-specific fit signals.
- Semantic JD-resume matching.
- Candidate fit scoring.
- Premium Streamlit UI/UX restructure.
- Recruiter workspace with batch ranking, notes, shortlist status, and CSV export.
- Privacy-safe display mode.
- Privacy/responsible AI dashboard using synthetic/demo data only.
- FastAPI backend foundation.
- Optional Streamlit-to-FastAPI connection with local fallback.
- SQLite + SQLAlchemy database foundation.
- Analysis/review summary saving.
- Backend request logging and monitoring metadata foundation.
- Pytest test foundation.
- Docker development setup.
- GitHub Actions CI with Docker build check.
- Local model registry and model-card foundation.
- Optional local MLflow experiment tracking.
- Local RAG recruiter copilot.
- RAG copilot FastAPI endpoint.
- GenAI planning layer.
- Safe GenAI prompt builder.
- GenAI prompt-preview FastAPI endpoint.
- Final UI/UX and product-flow polish.
- Documentation and architecture polish.

## Next

- Optional external GenAI integration with consent, PII redaction, provider configuration, timeout handling, and local fallback.
- Better model evaluation and retraining pipeline.
- Stronger calibration and real-resume validation.
- MLflow model registry upgrade.
- Deployment modernization.
- Authentication and role-based access control.
- PostgreSQL migration.
- Production monitoring and alerting.
- More robust semantic models.
- Expanded test coverage for full end-to-end workflows.
- Screenshots and demo assets for portfolio presentation.

## Guiding Principles

- Keep ResumeIQ local-first unless external services are explicitly added with consent and safeguards.
- Treat all scores as estimates or decision-support signals.
- Avoid automated hiring decisions.
- Avoid storing or logging raw sensitive resume/JD content.
- Keep documentation honest about what is implemented, planned, and limited.
