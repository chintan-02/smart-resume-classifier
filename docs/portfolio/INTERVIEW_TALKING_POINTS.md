# Interview Talking Points

Use these points to explain ResumeIQ naturally in interviews, project reviews, or professor discussions.

For public demos, use demo/sample data only. ResumeIQ requires human review, does not currently make external GenAI calls, uses privacy-safe masking as a helpful but not guaranteed anonymization layer, and is not a final hiring decision system.

## 1. What Problem ResumeIQ Solves

- Resume review can be slow, inconsistent, and hard to explain.
- Recruiters often need to compare skills, job-description alignment, resume quality, and missing information.
- ResumeIQ turns resume content into structured review signals so a human can make a more informed review.

## 2. Why I Built It

- I wanted a portfolio project that goes beyond a basic ML notebook.
- I wanted to practice full AI product engineering: UI, backend, database, ML, testing, Docker, CI, documentation, and responsible AI.
- I chose resumes because they are familiar, text-heavy, and require careful ethical boundaries.

## 3. Architecture Decisions

- Streamlit handles the user-facing dashboard and recruiter workflow.
- FastAPI exposes backend endpoints for analysis, copilot evidence search, and prompt preview.
- Core logic lives in reusable modules instead of putting everything in `app.py`.
- The Streamlit app can still work locally if the backend is unavailable.

## 4. ML/NLP Methods Used

- TF-IDF and Logistic Regression provide a baseline resume category classifier.
- Rule-based logic supports skill extraction, ATS-style estimates, writing quality checks, and structure advice.
- Semantic matching compares resume and job-description content for stronger alignment signals.
- Local evidence retrieval supports the recruiter copilot without external AI calls.

## 5. Backend/API Design

- FastAPI provides clear endpoints for health, readiness, resume analysis, local copilot search, and prompt preview.
- The API design separates backend behavior from the Streamlit UI.
- Health and readiness endpoints make the system easier to test, debug, and deploy later.

## 6. Database Design

- SQLite and SQLAlchemy provide a lightweight database foundation.
- The database stores structured summaries and metadata instead of intentionally storing full resume text by default.
- This keeps the project practical while respecting privacy concerns.

## 7. Responsible AI Decisions

- ResumeIQ is decision support, not automated hiring.
- The app avoids final hire/reject language.
- Human review is required for any real-world action.
- The fairness dashboard uses synthetic/demo data only.

## 8. Privacy Decisions

- Public screenshots and demos should use sample resumes and sample job descriptions.
- Privacy-safe mode masks common personal identifiers in supported displays.
- Masking is helpful, but not guaranteed full anonymization.
- No external GenAI calls are currently made.

## 9. Testing and CI

- Pytest validates key project behavior.
- GitHub Actions runs automated checks.
- Docker validation helps confirm the app can be started consistently across environments.

## 10. Docker and Deployment Readiness

- Docker Compose runs the Streamlit UI and FastAPI backend together.
- Docker support makes local development and future deployment more repeatable.
- I avoid claiming full production deployment unless the app is actually deployed and monitored.

## 11. What I Would Improve Next

- Improve model evaluation with better datasets, calibration, and error analysis.
- Add stronger privacy controls before any external AI integration.
- Expand tests around edge cases, parsing failures, and API behavior.
- Improve monitoring, observability, and deployment hardening.

## 12. What I Learned

- A strong AI project needs more than model accuracy.
- Architecture, privacy, explainability, testing, and deployment all matter.
- Responsible AI wording matters because resume tools can affect real people.
- Building in small steps makes a large project easier to debug and explain.
