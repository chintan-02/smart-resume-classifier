# Screenshot Capture Plan

This plan explains how to capture clean, privacy-safe ResumeIQ screenshots for GitHub, LinkedIn, a portfolio website, professor discussion, and interviews.

ResumeIQ is a decision-support project. Screenshots must use demo/sample data only, human review is required, external GenAI calls are not currently enabled, privacy-safe masking is helpful but not guaranteed full anonymization, and the app is not a final hiring decision system.

## 1. Start the App Locally

From the project root:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m database.init_db
python scripts/register_baseline_model.py
streamlit run app.py --server.fileWatcherType none
```

Open:

```text
http://localhost:8501
```

## 2. Start the Backend

In a second terminal:

```bash
uvicorn backend.main:app --reload --port 8000
```

Open the API docs:

```text
http://localhost:8000/docs
```

## 3. Verify Backend Health

Open:

```text
http://localhost:8000/health
```

Expected result: a healthy status response from the FastAPI backend.

You can also check readiness:

```text
http://localhost:8000/ready
```

## 4. Screenshot Setup

- Use a 1440px or wider browser window when possible.
- Use 100% browser zoom unless a page needs slight adjustment.
- Hide browser bookmarks and unrelated browser extensions.
- Turn privacy-safe mode ON before public screenshots.
- Use sample/fake resume content only.
- Use sample/fake job description content only.
- Do not show real personal emails, phone numbers, addresses, links, or private resume data.
- Do not show private local paths, API keys, `.env` values, logs, database files, or candidate information.
- Crop screenshots if needed to remove private paths or unrelated desktop content.
- Keep image file sizes reasonable before adding them to the repository.
- Store final screenshots in `docs/assets/screenshots/` only when intentionally adding reviewed images later.

## Recommended Screenshots

### 1. `01_landing_candidate_overview.png`

Show the hero section, upload area, and main dashboard purpose.

Caption: "ResumeIQ candidate overview and decision-support dashboard."

### 2. `02_resume_quality.png`

Show resume quality, structure advisor, and writing signals.

Caption: "Resume quality and improvement insights."

### 3. `03_job_match_intelligence.png`

Show ATS/JD match, semantic match, and skill gaps.

Caption: "Job description alignment and skill-gap analysis."

### 4. `04_recruiter_workspace_batch_ranking.png`

Show batch ranking and shortlist workflow.

Caption: "Recruiter workspace for comparing multiple resumes."

### 5. `05_recruiter_copilot_local_evidence.png`

Show local RAG evidence search with evidence snippets.

Caption: "Local retrieval-based recruiter copilot with evidence snippets."

### 6. `06_genai_prompt_preview.png`

Show the safe prompt builder preview.

Caption: "Safe GenAI prompt preview foundation with external AI disabled."

### 7. `07_model_transparency.png`

Show model details, confidence/explainability, registry, and MLflow foundation.

Caption: "Model transparency, registry, and experiment tracking foundation."

### 8. `08_privacy_responsible_ai.png`

Show privacy-safe mode and the responsible AI dashboard.

Caption: "Privacy and responsible AI safeguards."

### 9. `09_fastapi_swagger_docs.png`

Show FastAPI Swagger docs with the main endpoints.

Caption: "FastAPI backend endpoints for analysis, copilot, and prompt preview."

### 10. `10_github_actions_ci.png`

Show a green GitHub Actions CI run.

Caption: "Automated test and Docker validation through GitHub Actions."

### 11. `11_docker_compose_running.png`

Show Docker Compose running, Docker Desktop, or concise terminal output.

Caption: "Docker Compose development setup for Streamlit and FastAPI."

## Quality Checklist

- Privacy-safe mode is ON.
- Demo/sample data is visible, not real resume data.
- No personal emails, phone numbers, addresses, or private links are visible.
- No terminal output exposes secrets or private files.
- The screenshot clearly shows one feature area.
- The image is cropped and compressed enough for repository use.
- The caption describes decision support, not hiring automation.
