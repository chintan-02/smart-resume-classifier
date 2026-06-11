# 🚀 Smart Resume Classifier & Skill Extractor

<p align="center">
  <b>End-to-End NLP + Machine Learning Project with Deployment</b><br>
  Classify resumes, extract skills, match job descriptions, and identify skill gaps — all in a modern dashboard.
</p>

---

## 🌐 Live Demo

👉 **Try the App:**
🔗 https://resume-classifier-chintan.azurewebsites.net

---

## 👨‍💻 Author

**Chintan Patel**
🔗 GitHub: https://github.com/chintan-02
💼 LinkedIn: https://www.linkedin.com/in/chintan-patel-987765129/

---

## 📌 Project Overview

Recruiters spend significant time manually screening resumes.

👉 This project solves that problem by building an **AI-powered system** that:

* Classifies resumes into job roles
* Extracts relevant technical skills
* Compares resumes with job descriptions
* Identifies missing skills (**Skill Gap Analysis**)

All presented through a **clean, interactive dashboard UI**.

---

## ✨ Key Features

✅ Upload Resume (**PDF / TXT**)
✅ Automatic Text Extraction (NLP)
✅ Job Role Prediction (ML Model)
✅ Skill Extraction Engine
✅ Resume vs Job Description Matching
✅ Match Score Calculation
✅ Skill Gap Analysis (Missing Skills)
✅ Interactive Dashboard UI (Streamlit)

---

## 🧠 Tech Stack

| Category            | Tools                        |
| ------------------- | ---------------------------- |
| Language            | Python                       |
| Data Processing     | Pandas, NumPy                |
| NLP                 | NLTK / spaCy                 |
| Machine Learning    | scikit-learn                 |
| Feature Engineering | TF-IDF                       |
| Model               | Logistic Regression          |
| Deployment          | Streamlit, Azure App Service |
| Others              | pypdf                        |

---

## 🏗️ Project Architecture

```
Resume → Text Extraction → NLP Processing → TF-IDF → ML Model → Predictions
                                               ↓
                                   Skill Extraction Engine
                                               ↓
                              JD Matching + Skill Gap Analysis
```

---

## 📊 Screenshots

### 🖥️ Dashboard UI
![Dashboard](assets/app_screenshot.png)

Clean, modern UI for uploading resumes and navigating analysis.


### 📂 Resume Upload & User Interaction
![Upload](assets/upload_interaction.png)

Users can upload resumes and provide job descriptions to instantly analyze candidate fit in an interactive dashboard.

### 📊 Prediction Output
![Prediction](assets/prediction_output.png)

Model predicts job role with confidence score and provides recruiter-style interpretation.

### 🎯 Skill Gap Analysis
![Skill Gap](assets/skill_gap_analysis.png)

Highlights matched skills, missing skills, and areas for improvement.

---

## 📁 Project Structure

```
smart-resume-classifier-skill-extractor/
│
├── app.py
├── train.py
├── utils.py
├── requirements.txt
├── README.md
│
├── artifacts/
├── data/
├── deployment/
├── notebooks/
└── .streamlit/
```

---

## ⚙️ How It Works

1. Upload resume
2. Extract text from PDF/TXT
3. Clean & preprocess text
4. Convert text → TF-IDF features
5. Predict job role using ML model
6. Extract skills using keyword matching
7. Compare with job description
8. Generate:

   * Match Score
   * Matched Skills
   * Missing Skills

---

## 💻 Run Locally

```bash
git clone https://github.com/chintan-02/smart-resume-classifier
cd smart-resume-classifier

python3.11 -m venv venv
source venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

python -m streamlit run app.py
```

👉 Open:

```
http://localhost:8501
```

---

## 🐳 Run With Docker

Build and start the Streamlit UI and FastAPI backend:

```bash
docker compose up --build
```

Open:

* Streamlit UI: http://localhost:8501
* FastAPI docs: http://localhost:8000/docs
* Health check: http://localhost:8000/health

Stop containers:

```bash
docker compose down
```

Reset the local Docker database volume:

```bash
docker compose down -v
```

Docker uses a local SQLite database stored in a Docker volume. No external AI API keys are required. The Streamlit app connects to the backend at `http://api:8000` inside Docker and can still fall back to local analysis if the API is unavailable.

---

## Configuration & Environment Management

ResumeIQ centralizes runtime configuration in `src/settings.py`. The app uses safe local defaults, so it can run without a `.env` file.

Use `.env.example` as the template for local overrides:

```bash
cp .env.example .env
```

Key environment variables:

* `RESUMEIQ_APP_ENV` controls the runtime label, such as `local`, `docker`, or `ci`.
* `RESUMEIQ_API_BASE_URL` tells Streamlit where the FastAPI backend is available.
* `RESUMEIQ_DATABASE_URL` controls the local SQLite database path.
* `RESUMEIQ_MLFLOW_TRACKING_URI` controls optional local MLflow tracking.
* `RESUMEIQ_MODEL_REGISTRY_PATH` controls the local JSON model registry path.
* `RESUMEIQ_PRIVACY_MODE_DEFAULT` and `RESUMEIQ_SAVE_ANALYSIS_DEFAULT` control Streamlit toggle defaults.

Local defaults use `http://127.0.0.1:8000`, `sqlite:///./resumeiq.db`, and `file:./mlruns`. Docker Compose overrides the environment to use `http://api:8000` and a SQLite database inside the Docker volume. GitHub Actions sets `RESUMEIQ_APP_ENV=ci` and uses a test SQLite database.

Safety note: `.env`, local database files, and `mlruns/` are ignored by Git. No external AI API keys are required for current local features. Future provider keys should never be committed.

---

## Model Evaluation & Registry

ResumeIQ includes a local model registry foundation for baseline classifier metadata, evaluation notes, and a simple model card.

Create or refresh the local baseline registry files:

```bash
python scripts/register_baseline_model.py
```

This writes local JSON metadata under `artifacts/model_registry/`.

The baseline model currently reports very high validation accuracy. Treat that as a review signal, not production proof. It should be checked later for data leakage, small validation split, class imbalance, overfitting, and real-resume calibration.

The registry stores model metadata and evaluation summaries only. It does not store full resume text, full job descriptions, or raw PII. MLflow or a cloud model registry can be added later when experiment tracking and deployment governance are introduced.

---

## Experiment Tracking

ResumeIQ includes an optional local MLflow foundation for experiment tracking.

Default tracking URI:

```text
file:./mlruns
```

Log the current baseline experiment metadata:

```bash
python scripts/log_baseline_experiment.py
```

The `mlruns/` directory is ignored by Git. Experiment tracking logs model-level metadata and numeric metrics only. Full resumes, full job descriptions, and raw PII are not logged.

Optional local MLflow UI:

```bash
mlflow ui --backend-store-uri ./mlruns --port 5000
```

Remote MLflow tracking, model artifact logging, and deployment governance are future work.

---

## RAG Recruiter Copilot Foundation

ResumeIQ includes a local retrieval-only recruiter copilot foundation. It uses TF-IDF similarity over text chunks from the current uploaded resume and optional job description.

What it does:

* chunks the current resume and job description in memory
* retrieves relevant evidence snippets for recruiter-style questions
* shows source labels and similarity scores
* uses cautious rule-based answer templates
* masks common resume identifiers when privacy-safe display mode is enabled

What it does not do yet:

* no external LLM or AI API calls
* no API keys
* no vector database service
* no storage of full resume or job-description text
* no automated hiring decisions

The copilot is designed for evidence search only. A future step may add LLM summarization with explicit consent, PII safeguards, and fallback behavior.

---

## RAG Copilot API

ResumeIQ exposes the same local retrieval-only copilot through FastAPI:

```text
POST /copilot/ask
```

The endpoint uses resume and optional job-description text from the current request only. It does not call external AI services, does not require API keys, and does not store full resume or job-description text. When `privacy_mode` is enabled, resume evidence output is masked using local privacy utilities. Streamlit can use this API when the backend toggle is enabled and falls back to local retrieval if the backend is unavailable.

Example:

```bash
curl -X POST "http://127.0.0.1:8000/copilot/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Which skills match the job description?",
    "resume_text": "Python developer with SQL, FastAPI, Docker, and machine learning projects.",
    "job_description": "Hiring for Python, SQL, Docker, FastAPI, and ML deployment.",
    "privacy_mode": true,
    "top_k": 5
  }'
```

---

## GenAI Integration Planning

ResumeIQ includes a planning layer for future GenAI features, but external GenAI is disabled by default and no external AI calls are made currently.

Future optional features may include resume rewrites, tailored cover letters, recruiter outreach emails, LinkedIn cold messages, interview questions, RAG answer generation, recruiter summaries, and resume gap explanations.

Before any future external provider call, ResumeIQ will require:

* explicit user consent
* PII masking before external calls
* provider configuration through environment variables only
* safe fallback when a provider is unavailable
* clear generated-content disclaimers and human review

API keys must never be committed. `.env` is ignored by Git, and `.env.example` documents only safe disabled defaults.

---

## Safe GenAI Prompt Builder

ResumeIQ includes a safe prompt-builder foundation for future GenAI workflows. It builds prompt previews only. It does not call external GenAI providers, does not generate output, and does not send resume or job-description content outside the app.

Prompt previews include:

* system safety instructions
* user prompt text
* consent/external-use status
* PII redaction support
* truthfulness and human-review reminders

External use is blocked by default. Future external generation will require explicit consent, provider configuration through environment variables, PII masking, safe fallback behavior, and clear generated-content disclaimers.

---

## GenAI Prompt Preview API

ResumeIQ exposes the safe prompt builder through FastAPI:

```text
POST /genai/prompt-preview
```

This endpoint builds prompt previews only. It does not call external AI providers, does not generate output, and does not store prompt content. Consent and external GenAI configuration control `allowed_for_external_use`; by default external use is blocked. When `privacy_mode` is enabled, evidence is redacted before it appears in the prompt preview.

Streamlit can use the backend prompt preview when the FastAPI backend toggle is enabled and falls back to the local prompt builder when the backend is unavailable.

Example:

```bash
curl -X POST "http://127.0.0.1:8000/genai/prompt-preview" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "resume_bullet_rewrite",
    "original_bullet": "Built a Streamlit resume analysis app using Python.",
    "resume_evidence": ["Python, Streamlit, FastAPI project experience."],
    "job_description_evidence": ["Role asks for Python and FastAPI."],
    "privacy_mode": true,
    "consent_given": false
  }'
```

---

## Logging & Monitoring

ResumeIQ includes a local logging and monitoring foundation:

* FastAPI request IDs
* request timing headers
* safe structured logs
* database/API request metadata logging
* PII-safe logging rules

External monitoring tools such as Application Insights, Sentry, Prometheus, or Grafana are planned future integrations, not currently connected.

---

## CI/CD

ResumeIQ uses GitHub Actions to automatically run:

* dependency installation
* database initialization smoke test
* pytest test suite
* FastAPI import smoke test
* Docker Compose config validation
* Docker image build checks for the FastAPI backend and Streamlit UI

Workflow file:

```
.github/workflows/ci.yml
```

Status:

Runs on push and pull request to `main`.

Test locally before pushing:

```bash
pytest
python -m database.init_db
python - <<'PY'
from backend.main import app
print(app.title)
PY
docker compose config
docker compose build api
docker compose build streamlit
```

---

## 🔁 Retrain Model

```bash
python train.py
```

---

## 📓 Notebook (For Learning)

```bash
jupyter notebook
```

Open:

```
notebooks/Resume_Classifier_Project.ipynb
```

---

## ☁️ Deployment (Azure)

This project is deployed using **Azure App Service**.

Deployment includes:

* GitHub CI/CD integration
* Custom startup command
* Environment configuration

---

## 🚀 Future Improvements

* Deep Learning (BERT / Transformers)
* Advanced NER for skill extraction
* Multi-language resume support
* Resume ranking system
* Recruiter dashboard with analytics

---

## 📈 Why This Project Stands Out

✔ End-to-end ML pipeline
✔ Real-world use case
✔ Deployment on cloud (Azure)
✔ Clean UI/UX
✔ Business impact focused

---

## ⭐ Final Note

This project uses a **sample dataset for demonstration**.
For production-level performance, integrate a larger dataset and advanced NLP models.

---

<p align="center">
  ⭐ If you like this project, give it a star on GitHub!
</p>
