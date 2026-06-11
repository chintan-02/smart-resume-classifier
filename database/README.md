# ResumeIQ Database Foundation

ResumeIQ uses SQLite by default for the database foundation:

```bash
sqlite:///./resumeiq.db
```

You can override the database URL with:

```bash
RESUMEIQ_DATABASE_URL
```

Initialize the database tables with:

```bash
python -m database.init_db
```

This database layer is foundation-only. The Streamlit app and FastAPI backend do not yet depend on it, and ResumeIQ does not store full resume text, full job descriptions, or raw PII by default.
