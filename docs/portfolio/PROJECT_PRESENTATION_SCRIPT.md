# Project Presentation Script

Use this as a 3-5 minute spoken script for a professor, recruiter, or technical interviewer.

ResumeIQ uses demo/sample data for public presentation, requires human review, does not currently make external GenAI calls, uses privacy-safe masking as a helpful but not guaranteed anonymization layer, and is not a final hiring decision system.

## Script

ResumeIQ is an AI resume intelligence platform that analyzes resumes against job descriptions and turns unstructured resume content into clear, reviewable signals.

The problem I wanted to solve is that resume screening can be time-consuming, inconsistent, and difficult to explain. A recruiter or hiring team may need to compare many resumes, understand skill gaps, review writing quality, and document why a resume looks like a stronger or weaker match. I wanted to build something that supports that review process without replacing human judgment.

The solution is ResumeIQ. It gives structured decision-support signals, not automated hiring decisions. The app can parse resumes, estimate ATS-style compatibility, compare resumes with a job description, extract skills, identify missing skills, review resume quality, and support batch ranking with recruiter notes and shortlist workflow.

On the AI and NLP side, ResumeIQ uses local Python workflows. It includes a TF-IDF and Logistic Regression baseline for resume category prediction, rule-based skill extraction and scoring, semantic job-description matching, local evidence retrieval for the recruiter copilot, and explainability-focused model details. I treat the model output as one signal, not as a final answer.

From an engineering perspective, the project is built as more than a notebook. The user interface is in Streamlit, reusable logic is organized into modules, and the backend is built with FastAPI. The project also includes SQLite and SQLAlchemy for database foundations, Docker Compose for local development, tests with pytest, GitHub Actions CI, application logging, a model registry foundation, and MLflow experiment tracking.

Responsible AI is an important part of the project. ResumeIQ includes privacy-safe display mode, but I describe it carefully because masking is helpful and not guaranteed full anonymization. The app avoids scoring protected attributes, uses synthetic/demo data for fairness dashboards, and clearly states that human review is required. It is designed as a decision-support tool, not a tool that hires or rejects people.

I also added a GenAI foundation, but external AI is disabled right now. The current feature is a safe prompt preview that shows what would be sent in a future consent-first workflow. Before adding external generation, the project would need explicit user consent, stronger PII handling, provider configuration, timeout handling, fallback behavior, and human review.

The goal is not to replace recruiters, but to help them review resumes more consistently and transparently. For me, ResumeIQ demonstrates full-stack AI product thinking: local ML and NLP, backend APIs, database design, testing, DevOps, responsible AI boundaries, and clear documentation.
