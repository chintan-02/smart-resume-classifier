# ResumeIQ — Privacy-Aware Resume Intelligence Platform

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Scikit-learn](https://img.shields.io/badge/ML-Scikit--learn-F7931E?style=flat-square&logo=scikitlearn&logoColor=white)
![Docker](https://img.shields.io/badge/Development-Docker_Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active_Development-F59E0B?style=flat-square)

**An NLP decision-support platform for resume analysis, job-description matching, skill intelligence, recruiter review, and responsible AI workflows.**

[Live Demo](https://resume-classifier-chintan.azurewebsites.net/) ·
[Portfolio Case Study](https://chintan-patel-ai.netlify.app/case-studies/resumeiq)

</div>

---

> [!IMPORTANT]
> ResumeIQ is a portfolio and educational decision-support system. It does not make hiring decisions, recommend employment actions automatically, or replace recruiter judgment. Human review is required before using any output in an application or hiring workflow.

---

## Product Overview

ResumeIQ converts resume content and job descriptions into structured, reviewable signals.

The platform combines:

- document parsing
- NLP preprocessing
- baseline role classification
- ATS-style compatibility signals
- keyword and semantic matching
- normalized skill extraction
- sentence-quality analysis
- practical rewrite guidance
- batch review workflows
- privacy-aware displays
- responsible AI controls

The goal is not to produce a single authoritative hiring score. The goal is to help candidates and reviewers understand:

- what information was detected
- how closely a resume aligns with a job description
- which skills are present or missing
- where wording or structure may be improved
- which signals require human interpretation

---

## Project Status

ResumeIQ is an active portfolio engineering project with a working Streamlit application and supporting FastAPI, database, testing, Docker, CI, and Azure foundations.

### Built and Available

- PDF, DOCX, and TXT resume parsing
- local text preprocessing
- baseline role classification
- ATS-style structure and content signals
- job-description keyword matching
- semantic resume-to-job matching
- normalized skill extraction
- skill-gap analysis
- resume-quality review
- generic or AI-like sentence detection
- humanized rewrite suggestions
- resume-structure guidance
- candidate-fit signals for human review
- batch resume ranking
- recruiter notes and shortlist workflow
- privacy-safe display mode
- responsible AI dashboard using synthetic or demonstration data
- Streamlit user interface
- Azure-hosted demonstration

### Engineering Foundations

- FastAPI backend
- typed API contracts
- health, readiness, and version endpoints
- SQLite and SQLAlchemy persistence
- local model registry
- MLflow integration foundation
- structured application logging
- Docker Compose development setup
- pytest test suite
- GitHub Actions continuous integration
- local retrieval-based recruiter copilot foundation
- safe GenAI prompt-preview endpoint
- fallback behavior when the optional backend is unavailable

### Experimental or Limited

- recruiter copilot uses local retrieval foundations rather than a production RAG service
- fairness views use synthetic or demonstration data only
- prompt preview builds and validates prompts but does not call an external GenAI provider
- baseline model evaluation requires additional leakage, class-balance, and validation review
- Azure deployment represents a portfolio demonstration, not a production hiring platform

### Planned

- stronger and independently validated classification models
- improved semantic matching
- formal evaluation and governance reports
- React or Next.js frontend exploration
- authentication and role-based access control
- PostgreSQL or another managed database
- encrypted document lifecycle management
- production monitoring and observability
- optional external GenAI only with explicit consent and PII safeguards
- deployment and security hardening

> Planned capabilities are roadmap targets and are not presented as completed experience.

---

## Core Workflow

```text
Upload Resume
      ↓
Parse PDF / DOCX / TXT
      ↓
Clean and Normalize Text
      ↓
Run Baseline Role Classification
      ↓
Extract and Normalize Skills
      ↓
Analyze Structure and Writing Quality
      ↓
Compare Resume with Job Description
      ↓
Calculate Keyword, Semantic, ATS, and Fit Signals
      ↓
Present Evidence and Improvement Guidance
      ↓
Human Review
```

ResumeIQ turns unstructured resume text into multiple supporting signals rather than relying on one opaque score.

---

## Main Capabilities

### Multi-Format Resume Parsing

ResumeIQ accepts:

- PDF
- DOCX
- TXT

The extracted text is cleaned and normalized before downstream analysis.

Parsing is treated as a separate engineering concern because extraction quality directly affects classification, matching, and skill analysis.

---

### Baseline Role Classification

A local scikit-learn pipeline predicts a likely resume category or role from processed text.

The baseline demonstrates:

- text preprocessing
- TF-IDF feature construction
- supervised classification
- local inference
- model registration
- prediction confidence presentation

The model is used as a portfolio baseline, not as an authoritative statement about a candidate’s profession or suitability.

> Headline accuracy is intentionally not promoted because unusually high validation performance requires further investigation for leakage, split quality, class imbalance, duplication, and overfitting.

---

### ATS-Style Compatibility Signals

ResumeIQ reviews practical resume signals such as:

- contact-section presence
- standard section coverage
- document structure
- measurable achievements
- skill visibility
- job-description keyword coverage
- content completeness
- common formatting or extraction issues

This is an educational compatibility estimate. It is not connected to a specific commercial ATS and should not be represented as an official ATS score.

---

### Job-Description Matching

The platform compares resume content with a supplied job description using multiple approaches:

- direct keyword overlap
- normalized skill comparison
- missing-skill detection
- semantic similarity
- role-alignment signals
- evidence-backed fit summaries

Separating these signals makes the output easier to inspect than a single unexplained percentage.

---

### Skill Intelligence

The skill pipeline normalizes related terms into a consistent taxonomy.

Examples may include:

```text
scikit learn → scikit-learn
postgres → postgresql
ml → machine learning
natural language processing → nlp
```

This supports:

- detected-skill summaries
- matched-skill lists
- missing-skill analysis
- role-alignment review
- batch candidate comparison

---

### Resume Quality and Writing Review

ResumeIQ identifies potential writing and structure issues such as:

- generic statements
- weak action verbs
- repetitive wording
- missing measurable outcomes
- vague responsibility descriptions
- incomplete section structure
- sentences that may sound overly templated

Rewrite suggestions are presented for review. They are not automatically applied to the resume.

---

### Batch Ranking and Recruiter Workflow

The project includes foundations for reviewing multiple resumes against the same job description.

The workflow can support:

- batch comparison
- sortable fit signals
- reviewer notes
- shortlist status
- structured candidate-review records

These outputs are decision-support aids only. They must not be used as fully automated screening decisions.

---

### Privacy-Safe Display Mode

Where supported, privacy-safe mode masks common personal identifiers in displays and exports.

Examples include:

- names
- email addresses
- phone numbers
- location details
- other common contact information

Masking reduces accidental exposure during demonstrations, but it is not presented as complete enterprise-grade de-identification.

---

### Responsible AI Dashboard

The project includes responsible-AI views built with synthetic or demonstration data.

These views are intended to explain:

- human-review requirements
- decision-support boundaries
- model limitations
- possible bias and fairness concerns
- privacy considerations
- why protected characteristics should not be scored

The dashboard does not claim that production fairness has been proven.

---

## Architecture

```text
Streamlit Interface
       │
       ├── Local Analysis Path
       │      ├── Resume Parsing
       │      ├── Preprocessing
       │      ├── Role Classification
       │      ├── ATS Signals
       │      ├── Skill Intelligence
       │      ├── Semantic Matching
       │      └── Quality Review
       │
       └── Optional FastAPI Client
              ↓
          FastAPI Backend
              ├── Health / Readiness / Version
              ├── Resume Analysis Snapshot
              ├── Local Recruiter Copilot Retrieval
              └── Safe GenAI Prompt Preview
                     ↓
       SQLite + SQLAlchemy
       Model Registry / MLflow Foundation
       Structured Logging
```

### Current runtime behavior

The Streamlit application remains usable when the FastAPI backend is unavailable.

When the backend is enabled and reachable, the interface can display API-backed snapshots while preserving the local analysis workflow as a fallback.

This architecture demonstrates API and persistence foundations without incorrectly presenting the current application as a fully distributed production platform.

For additional details, see [Architecture Documentation](docs/ARCHITECTURE.md).

---

## Application Layers

| Layer | Responsibility |
|---|---|
| Streamlit UI | Uploads, analysis workflow, review screens, and result presentation |
| Parsing | PDF, DOCX, and TXT text extraction |
| NLP preprocessing | Cleaning, normalization, and feature preparation |
| Classification | Local baseline role prediction |
| Matching | Keyword, skill, and semantic job-description comparison |
| Quality analysis | Structure, writing, and generic-sentence review |
| Recruiter workflow | Batch comparison, notes, and shortlist foundations |
| FastAPI | Optional API-backed analysis, readiness, copilot, and prompt-preview routes |
| Persistence | SQLite and SQLAlchemy foundations |
| Model operations | Local registry and MLflow foundations |
| Delivery | Docker Compose, GitHub Actions, and Azure demonstration |

---

## FastAPI Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Return API root and status information |
| `GET` | `/health` | Basic backend health check |
| `GET` | `/ready` | Check configuration, database, registry, MLflow, retrieval, and prompt-builder readiness |
| `GET` | `/version` | Return version and build metadata |
| `POST` | `/analyze-resume` | Return a local resume and job-description analysis snapshot |
| `POST` | `/copilot/ask` | Search local recruiter-copilot evidence |
| `POST` | `/genai/prompt-preview` | Build a safety-checked prompt preview without an external GenAI call |

Interactive API documentation is available locally at:

```text
http://localhost:8000/docs
```

See [API Documentation](docs/API.md).

---

## GenAI and Recruiter Copilot Status

### Local Recruiter Copilot

The recruiter-copilot foundation supports local evidence retrieval from project data or review context.

Current positioning:

- local retrieval support
- evidence-oriented response structure
- no claim of production RAG evaluation
- human review required
- no autonomous hiring actions

### GenAI Prompt Preview

The prompt-preview workflow currently:

- builds a structured prompt
- applies safety checks
- reports blocking reasons
- avoids external provider calls
- requires no API key

External GenAI is disabled by default.

A future provider integration would require:

- explicit user consent
- PII detection and redaction
- secure provider configuration
- clear data-retention disclosure
- fallback behavior
- output review
- audit logging
- documented evaluation

---

## Privacy and Responsible AI

ResumeIQ follows these core boundaries:

1. Outputs support human review rather than replace it.
2. Protected attributes should not be used for candidate scoring.
3. Full resume and job-description text should not be stored unnecessarily.
4. Personal information should be masked in demonstration views where supported.
5. Fairness visualizations must be clearly identified as synthetic when they are not based on audited production data.
6. External GenAI should remain disabled until consent, privacy, security, and governance requirements are implemented.
7. Scores must be explained as estimates or signals rather than objective hiring truth.

### Current safeguards

- human review required
- external GenAI disabled by default
- prompt-preview blocking reasons
- privacy-safe display mode
- synthetic-data label for fairness views
- no intentional protected-attribute scoring
- documented limitations
- responsible AI documentation

See [Responsible AI Documentation](docs/RESPONSIBLE_AI.md).

---

## Data Handling Boundaries

ResumeIQ is designed to avoid unnecessary persistence of raw personal content.

Current design intentions include:

- no intentional storage of full resume text by default
- no intentional storage of complete job descriptions by default
- use of structured analysis records where persistence is required
- masking common PII in selected displays and exports
- use of fictional or synthetic data for public responsible-AI demonstrations

This is not a formal privacy certification. A production deployment would still require:

- retention policies
- encryption
- access controls
- consent management
- deletion workflows
- audit review
- organizational privacy approval

---

## Technology Stack

| Area | Technologies |
|---|---|
| Language | Python |
| User interface | Streamlit |
| Backend | FastAPI, Pydantic |
| Machine learning | scikit-learn, TF-IDF |
| Data processing | pandas, NumPy |
| Semantic matching | local embedding and similarity foundations |
| Persistence | SQLite, SQLAlchemy |
| Model operations | local model registry, MLflow foundation |
| Testing | pytest |
| Containerization | Docker, Docker Compose |
| CI | GitHub Actions |
| Deployment | Azure App Service demonstration |
| Retrieval | local recruiter-copilot evidence search |

---

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/chintan-02/smart-resume-classifier.git
cd smart-resume-classifier
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize the local database

```bash
python -m database.init_db
```

### 5. Register the baseline model

```bash
python scripts/register_baseline_model.py
```

### 6. Start the Streamlit application

```bash
streamlit run app.py --server.fileWatcherType none
```

Open:

```text
http://localhost:8501
```

---

## Run the FastAPI Backend

```bash
uvicorn backend.main:app --reload --port 8000
```

Open the API documentation:

```text
http://localhost:8000/docs
```

---

## Run with Docker Compose

```bash
docker compose up --build
```

Services:

| Service | Local URL |
|---|---|
| Streamlit UI | `http://localhost:8501` |
| FastAPI backend | `http://localhost:8000` |
| FastAPI documentation | `http://localhost:8000/docs` |

---

## Testing

Run the test suite:

```bash
pytest
```

The repository includes tests and engineering checks around project modules such as:

- parsing and preprocessing
- scoring and analysis helpers
- database repositories
- API foundations
- model and registry utilities
- responsible-AI behavior
- recruiter workflow foundations

GitHub Actions provides continuous-integration checks for repository changes.

---

## Live Demonstration

The current Azure-hosted demonstration is available at:

[https://resume-classifier-chintan.azurewebsites.net/](https://resume-classifier-chintan.azurewebsites.net/)

The hosted application is a portfolio demonstration. Availability and behavior may depend on the current Azure deployment configuration.

---

## Evaluation Positioning

ResumeIQ intentionally avoids publishing an unverified headline accuracy figure.

The current baseline model has shown validation results that require deeper review. Before presenting a production-quality metric, the project should investigate:

- train-validation leakage
- duplicate or near-duplicate resumes
- split strategy
- small validation subsets
- class imbalance
- category overlap
- overfitting
- confidence calibration
- out-of-distribution behavior

Future evaluation should include:

- stratified cross-validation
- per-class precision, recall, and F1
- confusion matrix
- macro and weighted F1
- calibration analysis
- error analysis
- leakage checks
- semantic-matching benchmarks
- responsible-AI review

This is more credible than promoting a high number without sufficient validation evidence.

---

## Current Limitations

- baseline classifier requires stronger independent evaluation
- ATS-style score is an educational estimate
- semantic matching requires additional benchmarking
- Streamlit remains the primary portfolio interface
- FastAPI is an optional supporting backend rather than the only source of truth
- SQLite is used for local persistence
- authentication and RBAC are not production-ready
- privacy-safe masking is not guaranteed to detect every identifier
- fairness views use synthetic or demonstration data
- external GenAI calls are disabled
- recruiter copilot is a local foundation without formal RAG evaluation
- no production monitoring or drift detection
- Azure deployment is a demonstration environment
- not approved for real automated hiring workflows

---

## Roadmap

### Evaluation and Model Quality

- complete leakage and duplicate analysis
- implement stronger train-validation methodology
- compare Logistic Regression, SVM, Naive Bayes, tree-based models, and semantic approaches
- add per-class and calibration reporting
- benchmark semantic job matching
- improve confidence interpretation

### Product and Platform

- evaluate React or Next.js frontend migration
- strengthen FastAPI-first contracts
- add authentication and RBAC
- migrate persistence to PostgreSQL where justified
- add encrypted file and record lifecycle management
- add monitoring, observability, and deployment hardening

### Responsible GenAI

- add explicit consent workflow
- implement robust PII redaction
- add provider configuration through secure environment variables
- add output review and audit records
- evaluate grounded generation and fallback behavior
- keep external generation optional

---

## Engineering Skills Demonstrated

This project demonstrates practical experience with:

- multi-format document parsing
- NLP preprocessing
- TF-IDF text classification
- local model inference
- resume and job-description matching
- semantic-similarity foundations
- skill normalization
- rule-based quality signals
- batch ranking and reviewer workflows
- FastAPI backend design
- Pydantic contracts
- SQLAlchemy persistence
- Docker Compose
- pytest
- GitHub Actions
- Azure deployment
- local retrieval foundations
- privacy-aware product design
- responsible AI documentation
- honest model-evaluation positioning
- human-in-the-loop workflow design

---

## Documentation

Core project documentation:

- [Setup](docs/SETUP.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Features](docs/FEATURES.md)
- [API](docs/API.md)
- [Responsible AI](docs/RESPONSIBLE_AI.md)
- [Roadmap](docs/ROADMAP.md)
- [Development Notes](docs/DEVELOPMENT_NOTES.md)

---

## Accuracy and Honesty

This README separates working product capabilities, engineering foundations, experimental features, and planned work.

ResumeIQ does not claim to:

- replicate a commercial ATS
- measure candidate quality objectively
- guarantee employment outcomes
- make automated hiring decisions
- have production-validated fairness
- have production-validated model accuracy
- provide enterprise-grade PII anonymization
- operate as a completed external-GenAI system

The strongest value of the project is the complete engineering workflow: document parsing, NLP analysis, model integration, semantic matching, backend foundations, persistence, testing, deployment, privacy-aware design, and responsible AI boundaries.

---

## Author

**Chintan Patel**

- [Portfolio](https://chintan-patel-ai.netlify.app/)
- [LinkedIn](https://www.linkedin.com/in/chintan-patel-ai/)
- [GitHub](https://github.com/chintan-02)

---

## License and Use

This repository is intended for portfolio, educational, research, and software-engineering demonstration purposes.

It should not be used as an automated employment-screening or hiring-decision system without formal model validation, privacy controls, security review, fairness assessment, governance, monitoring, and human oversight.
