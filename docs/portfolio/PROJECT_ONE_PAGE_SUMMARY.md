# ResumeIQ One-Page Project Summary

## Project Name

ResumeIQ - AI Resume Intelligence & Job Application Assistant

## One-Line Description

ResumeIQ is a privacy-aware resume intelligence platform that analyzes resumes against job descriptions and provides explainable decision-support signals for human review.

## Problem

Resume screening is time-consuming, inconsistent, and often difficult to explain. Reviewers need help comparing skills, job alignment, resume quality, and supporting evidence without turning the system into an automated hiring decision tool.

## Solution

ResumeIQ organizes resume analysis into clear, recruiter-friendly insights: ATS-style estimates, job match signals, skill gaps, writing quality feedback, batch ranking, recruiter notes, and local evidence search.

## Tech Stack

Python, Streamlit, FastAPI, scikit-learn, SQLite, SQLAlchemy, pytest, Docker Compose, GitHub Actions, MLflow foundation, and local model registry foundations.

## Key Features

- Resume parsing for PDF, DOCX, and TXT files.
- Resume category prediction with a local baseline model.
- ATS-style compatibility estimate and job-description matching.
- Skill extraction, semantic matching, and skill-gap analysis.
- Resume quality, structure, and writing-signal review.
- Batch ranking, shortlist workflow, and recruiter notes.
- Local retrieval-based recruiter copilot.
- Safe GenAI prompt preview with external AI disabled.
- Model transparency, registry, and experiment tracking foundation.

## Architecture

The Streamlit UI manages the user workflow. FastAPI provides optional backend endpoints. Core resume intelligence logic lives in reusable Python modules. SQLite and SQLAlchemy provide a database foundation, while Docker Compose and CI support repeatable development checks.

## Responsible AI and Privacy

ResumeIQ is a decision-support system, not a final hiring decision system. Human review is required. Public demos and screenshots should use demo/sample data only. Privacy-safe masking helps reduce visible personal information, but it is not guaranteed full anonymization. External GenAI calls are not currently enabled.

## Testing/DevOps

The project includes pytest tests, GitHub Actions CI, Docker Compose configuration, backend health/readiness endpoints, logging foundations, a model registry foundation, and MLflow experiment tracking foundations.

## Current Status

ResumeIQ is portfolio/capstone-ready as a local AI/ML product engineering project. It demonstrates practical ML/NLP, backend design, UI workflows, responsible AI boundaries, and DevOps foundations.

## Future Roadmap

Future improvements could include stronger model evaluation, confidence calibration, more robust privacy controls, deployment hardening, monitoring, improved semantic retrieval, and consent-first external GenAI workflows.
