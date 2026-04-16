# Smart Resume Classifier + Skill Extractor

A polished beginner-friendly NLP + ML project that classifies resumes into job roles, extracts skills, compares a resume against a job description, and highlights missing skills in a clean Streamlit dashboard.

## What is new in this version

- Upgraded UI with a polished dark dashboard layout
- Better analysis flow with tabs, cards, and role-confidence chart
- Azure-ready deployment files included
- Local setup instructions updated to avoid virtual-environment path issues
- Jupyter notebook retained for learning and assignment submission

## Features

- Upload resume in **PDF** or **TXT**
- Extract text from resume
- Predict job role using **TF-IDF + Logistic Regression**
- Extract skills using keyword matching
- Compare resume with job description
- Compute **match score**
- Show **missing skills**, matched skills, and extra skills
- Includes **Jupyter Notebook** for explanation and **Streamlit app** for demo/deployment

## Project Structure

```bash
smart-resume-classifier-skill-extractor/
│
├── app.py
├── train.py
├── utils.py
├── requirements.txt
├── README.md
├── runtime.txt
├── LICENSE
├── .gitignore
│
├── artifacts/
│   ├── resume_classifier.pkl
│   └── metrics.json
│
├── assets/
│   └── dashboard_preview.txt
│
├── data/
│   ├── resume_dataset.csv
│   ├── sample_job_description.txt
│   └── skills_list.txt
│
├── deployment/
│   ├── startup.sh
│   ├── azure_deploy_guide.md
│   └── Dockerfile
│
├── notebooks/
│   └── Resume_Classifier_Project.ipynb
│
└── .streamlit/
    └── config.toml
```

## Tech Stack

- Python
- Pandas
- NumPy
- scikit-learn
- pypdf
- Streamlit
- Jupyter Notebook

## Run Locally

```bash
cd smart-resume-classifier-skill-extractor
python3.11 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open in your browser:

```text
http://localhost:8501
```

## Retrain the Model

```bash
python train.py
```

## Open the Notebook

```bash
jupyter notebook
```

Then open:

```text
notebooks/Resume_Classifier_Project.ipynb
```

## Azure Deployment Files Included

The `deployment/` folder includes:

- `startup.sh` → runs Streamlit on `0.0.0.0:8000`
- `azure_deploy_guide.md` → step-by-step Azure App Service deployment
- `Dockerfile` → optional container deployment path for Azure

## GitHub Upload Steps

```bash
git init
git add .
git commit -m "Initial commit - Smart Resume Classifier project"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/smart-resume-classifier-skill-extractor.git
git push -u origin main
```

## Presentation Flow

- Problem: recruiters spend time screening resumes manually
- Solution: automate role prediction and skill extraction
- NLP: cleaning, TF-IDF features, keyword-based skills
- ML: Logistic Regression classifier
- Output: predicted role, extracted skills, JD match score, missing skills
- Deployment: Streamlit locally, Azure App Service in the cloud

## Notes

This project uses a small educational sample dataset so the repo runs immediately. For a stronger portfolio version, replace `data/resume_dataset.csv` with a larger public resume dataset and retrain the model.
