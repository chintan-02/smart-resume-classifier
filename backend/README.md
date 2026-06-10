# ResumeIQ Backend API

This backend is currently foundation-only. Streamlit UI connection will be implemented in the next step.

## Run locally

```bash
uvicorn backend.main:app --reload --port 8000
```

## Endpoints

- `GET /`
- `GET /health`
- `GET /ready`
- `POST /analyze-resume`
- `GET /docs`
