# ResumeIQ Deployment Sync Checklist

Use this checklist to compare the local app, FastAPI backend, GitHub repository, and Azure website.

## 1. Check the latest local commits

```bash
git log --oneline -5
```

Compare the latest commit with the commit shown in GitHub and, when configured, the deployed app metadata.

## 2. Check the local backend

Start FastAPI:

```bash
uvicorn backend.main:app --reload --port 8000
```

Check version and readiness metadata:

```bash
curl http://127.0.0.1:8000/version
curl http://127.0.0.1:8000/ready
```

Confirm that `/version` reports ResumeIQ version `0.35.0`, stage `portfolio-polish`, environment, and commit metadata. `/ready` should include `version_info: available`.

## 3. Check local Streamlit

```bash
streamlit run app.py --server.fileWatcherType none
```

Open the local app and verify that the sidebar contains collapsed **Developer Notes**.

Expected local metadata:

- Environment: `local`
- Commit: `local`

## 4. Check the Azure website

Set Azure App Service environment variables:

- `RESUMEIQ_APP_ENV=azure`
- `RESUMEIQ_GIT_COMMIT=<latest-short-commit>`
- `PORT=8000`
- `WEBSITES_PORT=8000`

Restart Azure App Service.

Open the configured Azure website URL and check the sidebar **Developer Notes** expander. Compare its version, stage, environment, and commit with the intended GitHub commit.

Expected Azure metadata:

- Environment: `azure`
- Commit: latest short commit

If the deployed backend route is available, also check:

```bash
curl https://<azure-app-url>/version
```

## 5. Interpret missing metadata

If Azure does not show **Developer Notes** or `/version` does not include the latest environment/commit metadata, Azure may be running an older deployment or missing environment variables.

## 6. Check GitHub Actions

- Confirm that ResumeIQ CI is green for the latest intended commit.
- Check whether the Azure deployment workflow is automatic or manual-only.
- With a manual-only workflow, new GitHub commits do not automatically deploy to Azure.

## 7. Deploy the intended revision

Either manually run the Azure deployment workflow or redeploy from the latest intended `main` branch commit. After deployment, repeat the backend and sidebar checks.
