# Azure App Service deployment guide

## Recommended path

Deploy this Streamlit app to **Azure App Service on Linux**.

## 1. Prepare the repo

Make sure these files are committed:

- `app.py`
- `requirements.txt`
- `deployment/startup.sh`
- `artifacts/`
- `data/`

## 2. Push the repo to GitHub

```bash
git init
git add .
git commit -m "Azure-ready Streamlit resume classifier"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/smart-resume-classifier-skill-extractor.git
git push -u origin main
```

## 3. Create Azure App Service

In Azure Portal:

- Create **Web App**
- Publish: **Code**
- Runtime stack: **Python 3.11**
- Operating system: **Linux**
- Pricing plan: choose Free/Basic for testing

## 4. Configure startup command

In Azure Portal → your Web App → **Settings > Configuration > General settings**

Set **Startup Command** to:

```text
bash deployment/startup.sh
```

## 5. Deploy from GitHub

In Azure Portal:

- Go to **Deployment Center**
- Source: **GitHub**
- Authorize GitHub
- Select repo and branch
- Save and let deployment finish

## 6. Restart and test

After deployment:

- Restart the Web App
- Open the default Azure URL
- If the app fails, check **Log stream** and **Advanced Tools / Kudu**

## Useful manual startup command

If you prefer not to use `startup.sh`, you can place this directly in Startup Command:

```text
python -m streamlit run app.py --server.port 8000 --server.address 0.0.0.0
```

## Common issues

- **Wrong port**: Azure expects the app to listen on port `8000`
- **Wrong host**: use `--server.address 0.0.0.0`
- **Missing packages**: verify `requirements.txt`
- **Broken paths**: keep `app.py` in repo root
- **Python mismatch**: use Python 3.11 locally and in Azure
