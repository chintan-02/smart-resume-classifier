# ResumeIQ Experiment Tracking

ResumeIQ uses optional local MLflow tracking for model-level experiment metadata and metrics.

This foundation is intentionally lightweight:

- uses local file-based tracking by default
- uses `file:./mlruns` as the default tracking URI
- logs sanitized parameters and numeric metrics
- does not log full resume text
- does not log full job descriptions
- does not log raw PII
- does not log model binaries in this step

Run a baseline logging smoke test:

```bash
python scripts/log_baseline_experiment.py
```

Optional local UI:

```bash
mlflow ui --backend-store-uri ./mlruns --port 5000
```

Remote MLflow tracking, artifact logging, and deployment governance can be added later.
