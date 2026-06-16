# ResumeIQ Setup Guide

This guide explains how to run ResumeIQ locally, with FastAPI, with Docker, and with tests.

## Prerequisites

- Python 3.11 recommended.
- Git.
- Docker Desktop optional, for Docker Compose workflow.
- A terminal with access to the project directory.

No external AI API keys are required for current features.

## Local Setup

From the repository root:

```bash
python -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Initialize the local database:

```bash
python -m database.init_db
```

Create or refresh local baseline model registry metadata:

```bash
python scripts/register_baseline_model.py
```

Run Streamlit:

```bash
streamlit run app.py --server.fileWatcherType none
```

Open:

```text
http://localhost:8501
```

## Backend Setup

Run the FastAPI backend in a second terminal:

```bash
uvicorn backend.main:app --reload --port 8000
```

Open:

```text
http://localhost:8000/docs
```

In Streamlit, use the sidebar backend toggle to check and optionally use the FastAPI snapshot. If the backend is offline, local Streamlit analysis remains available.

## Database Initialization

ResumeIQ uses SQLite by default:

```bash
python -m database.init_db
```

Default local database path:

```text
resumeiq.db
```

The database stores summaries and metadata. Full resume text and full job descriptions are not intentionally stored by default.

## Model Registry Initialization

Create local model registry files:

```bash
python scripts/register_baseline_model.py
```

Default registry path:

```text
artifacts/model_registry/model_registry.json
```

## MLflow Experiment Logging

MLflow tracking is optional and local. If dependencies are available, log the baseline experiment with:

```bash
python scripts/log_baseline_experiment.py
```

The default tracking URI is:

```text
file:./mlruns
```

## Docker Commands

Build and run both services:

```bash
docker compose up --build
```

Open:

- Streamlit UI: `http://localhost:8501`
- FastAPI docs: `http://localhost:8000/docs`

Stop containers:

```bash
docker compose down
```

Reset Docker volume data:

```bash
docker compose down -v
```

Validate Compose config:

```bash
docker compose config
```

## Running Tests

```bash
pytest
```

CI also validates database initialization, FastAPI import, Docker Compose config, and Docker image builds.

## Deployment Version Check

ResumeIQ exposes lightweight deployment metadata so local and deployed environments can be compared:

- The Streamlit sidebar includes collapsed **Developer Notes** with version, stage, environment, and commit metadata.
- FastAPI exposes the same non-secret metadata at `GET /version`.
- Azure may show an older UI when its deployment workflow has not run after recent commits.
- Set `RESUMEIQ_GIT_COMMIT` in the deployment environment to the deployed commit SHA or another traceable commit label.
- `RESUMEIQ_APP_ENV` identifies the runtime environment, such as `local`, `docker`, or `azure`.
- If the Azure workflow is manual-only, pushing commits to GitHub will not automatically update Azure.

These checks provide deployment visibility only. They do not confirm that Azure is currently deployed.

## Azure Deployment Metadata

Recommended Azure App Service environment variables:

```text
RESUMEIQ_APP_ENV=azure
RESUMEIQ_GIT_COMMIT=<short-git-commit>
PORT=8000
WEBSITES_PORT=8000
```

- `RESUMEIQ_APP_ENV` controls whether ResumeIQ reports `local`, `docker`, or `azure`.
- `RESUMEIQ_GIT_COMMIT` helps confirm which commit is deployed.
- `PORT` and `WEBSITES_PORT` help Azure route the Streamlit container on port `8000`.
- Metadata is shown only under collapsed Developer Notes in Streamlit and through FastAPI `GET /version`.
- Do not store secrets in these metadata variables.

## Common Troubleshooting

### Port 8000 already in use

Another backend process may be running. Stop it or use a different port:

```bash
uvicorn backend.main:app --reload --port 8001
```

If you change the backend port, update `RESUMEIQ_API_BASE_URL` for Streamlit.

### Port 8501 already in use

Streamlit may already be running. Stop the old process or run Streamlit on another port:

```bash
streamlit run app.py --server.port 8502 --server.fileWatcherType none
```

### Docker daemon not running

Start Docker Desktop, then retry:

```bash
docker compose config
docker compose up --build
```

### Dependency install issue

Upgrade pip and reinstall:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Use Python 3.11 when possible because CI is configured for Python 3.11.

### Database file ignored

Local database files are intentionally ignored by Git. Recreate the schema with:

```bash
python -m database.init_db
```

### Backend offline but Streamlit still works

This is expected. ResumeIQ is local-first. FastAPI is optional, and Streamlit can run the primary workflow without the backend.

### Model registry not initialized

Run:

```bash
python scripts/register_baseline_model.py
```

### MLflow not available

MLflow tracking is optional and local. Install/run MLflow only when needed for experiment tracking.
