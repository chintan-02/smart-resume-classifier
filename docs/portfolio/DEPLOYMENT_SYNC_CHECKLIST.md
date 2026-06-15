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

Confirm that `/version` reports ResumeIQ version `0.35.0` and the Step 35A build label.

## 3. Check local Streamlit

```bash
streamlit run app.py --server.fileWatcherType none
```

Open the local app and verify that the sidebar contains the **App Version** expander.

## 4. Check the Azure website

Open the configured Azure website URL and check whether the sidebar contains the **App Version** expander. Compare its version, build label, environment, and Git commit label with the local values.

## 5. Interpret a missing version display

If Azure does not show the **App Version** expander, Azure is running a build older than Step 35A.

## 6. Check GitHub Actions

- Confirm that ResumeIQ CI is green for the latest intended commit.
- Check whether the Azure deployment workflow is automatic or manual-only.
- With a manual-only workflow, new GitHub commits do not automatically deploy to Azure.

## 7. Deploy the intended revision

Either manually run the Azure deployment workflow or redeploy from the latest intended `main` branch commit. After deployment, repeat the backend and sidebar checks.
