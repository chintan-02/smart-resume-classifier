# Development Notes

These notes help keep ResumeIQ clean, safe, and portfolio-ready as new features are added.

## Coding Conventions

- Keep changes small and focused.
- Reuse existing modules and naming patterns.
- Keep `app.py` focused on Streamlit UI and user flow.
- Put reusable logic in `src/`.
- Put API route logic in `backend/routers/`.
- Put request/response models in `backend/schemas/`.
- Put persistence logic in `database/`.
- Prefer readable functions over clever abstractions.
- Add tests when behavior changes.

## Safe Wording Rules

Use safe decision-support language:

- "Decision-support signal"
- "Local estimate"
- "Recommended for review"
- "Review after targeted improvements"
- "Needs follow-up"
- "Human review required"

Avoid unsafe or overstated wording:

- "Hire"
- "Reject"
- "Best candidate"
- "Worst candidate"
- "Guaranteed ATS score"
- "Final decision"
- "Automated screening decision"
- "Definitely AI-generated"

## What Not to Log

Do not intentionally log:

- Full resume text.
- Full job descriptions.
- Raw PII.
- Emails, phone numbers, addresses, LinkedIn URLs, GitHub URLs.
- API keys, tokens, passwords, or secrets.

Operational logs should focus on metadata such as endpoint, method, status code, latency, success state, and request IDs.

## What Not to Store

Do not store full sensitive documents by default. Current database storage should remain focused on:

- Analysis summaries.
- Batch ranking summaries.
- Recruiter review metadata.
- API request metadata.
- Audit-style operational events.

If future storage of full documents is needed, design privacy, retention, consent, access control, and deletion behavior first.

## Adding Future Modules

Use this rough placement guide:

- UI display and layout: `app.py` or `src/ui/`.
- Resume/JD analysis logic: `src/`.
- Backend endpoints: `backend/routers/`.
- Pydantic schemas: `backend/schemas/`.
- Database writes/queries: `database/repositories.py`.
- Settings and environment flags: `src/settings.py`.
- Tests: `tests/`.
- Documentation: `docs/`.

## Tests Before Commit

Run:

```bash
pytest
docker compose config
```

If Docker files, requirements, or service startup behavior changed, also run:

```bash
docker compose build api
docker compose build streamlit
```

For UI changes, manually run:

```bash
streamlit run app.py --server.fileWatcherType none
```

For backend changes, manually run:

```bash
uvicorn backend.main:app --reload --port 8000
```

## Azure Startup Performance

Azure App Service may cold start after idle time, so ResumeIQ keeps the first Streamlit page load lightweight.

- Optional ML/NLP helpers are imported only when their sections or actions need them.
- Streamlit cache is used for stable resources such as model artifacts, skills, and static planning metadata.
- The initial page can load before the classifier, parser, semantic matcher, MLflow helpers, model registry, RAG copilot, or synthetic fairness demo are needed.
- First analysis may still take longer than first page load because model artifacts and resume parsing load on demand.
- If available on the App Service plan, Always On can reduce cold-start delays.

## Commit Hygiene

- Do not commit generated local databases.
- Do not commit `.env` files.
- Do not commit `mlruns/` unless intentionally changing tracked examples.
- Do not commit screenshots unless they are final, small, and reviewed.
- Do not commit cache folders such as `__pycache__/`.
- Keep commits grouped by task.
- Write commit messages that explain the user-facing or engineering purpose.

## Local Generated Files to Avoid Committing

- `resumeiq.db`
- `test_resumeiq_ci.db`
- `.env`
- `mlruns/`
- `__pycache__/`
- local logs
- temporary screenshots
- temporary notebooks or exports

## External GenAI Rules

Current ResumeIQ GenAI behavior is prompt preview only. Do not add external AI calls unless a future task explicitly asks for it.

Future external GenAI work must include:

- Explicit user consent.
- PII redaction/masking.
- Provider configuration through environment variables.
- Timeout handling.
- Local fallback.
- Generated-content disclaimer.
- Tests for blocked/allowed paths.
- Documentation updates.

Never commit API keys.

## Privacy Review Checklist

Before merging privacy-sensitive work, ask:

- Does this log raw text?
- Does this store raw text?
- Does this display PII when privacy mode is on?
- Does this send data outside the local app?
- Does this imply an automated hiring decision?
- Does this claim full anonymization or bias-free behavior?

If the answer is uncertain, pause and design the boundary before coding.
