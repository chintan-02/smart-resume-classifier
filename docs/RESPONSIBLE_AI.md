# Responsible AI and Privacy Notes

ResumeIQ is a decision-support tool for resume review, job-description comparison, and recruiter/candidate workflow support. It is not an automated hiring decision system.

## 1. Decision-Support Boundary

ResumeIQ provides signals such as predicted role, ATS-style estimates, skill overlap, semantic similarity, writing-quality notes, and local evidence snippets.

These outputs should support human review. They should not be used as automatic hiring, rejection, ranking, or eligibility decisions.

## 2. Human Review Required

Human review is required before any hiring or application action. Reviewers should consider the full resume, job context, candidate materials, interview evidence, and organization-specific requirements.

## 3. Privacy-Safe Display Mode

Privacy-safe display mode masks common personal identifiers in supported displays and exports. This can include:

- Candidate name when available.
- Email address.
- Phone number.
- LinkedIn URL.
- GitHub URL.
- Location/address patterns where supported by current masking utilities.

## 4. PII Masking Limitations

Privacy-safe mode reduces visible PII, but it does not guarantee full anonymization. Resumes can include unusual formatting, embedded images, uncommon identifiers, or context clues that are difficult to mask perfectly.

Do not treat masking as legal compliance or complete de-identification.

## 5. Fairness Dashboard Scope

The Responsible AI fairness dashboard uses synthetic/demo data only. It is an educational dashboard for discussing fairness concepts and monitoring ideas.

It is not a fairness certification and does not prove the system is bias-free.

## 6. No Protected-Attribute Scoring

ResumeIQ does not intentionally score protected attributes such as age, gender, race, religion, disability, marital status, or immigration status.

The project should avoid adding features that infer, rank, or filter candidates using protected or sensitive characteristics.

## 7. Model Accuracy Caveat

The baseline classifier currently reports very high validation accuracy. This should be reviewed for possible:

- Data leakage.
- Small validation split.
- Class imbalance.
- Overfitting.
- Weak calibration on real resumes.

The model is useful for demonstration and learning. It should not be presented as a production-quality hiring model without stronger evaluation.

## 8. GenAI Disabled by Default

Current GenAI-related functionality is prompt preview only. ResumeIQ does not currently send resume text or job-description content to external AI providers.

No external AI API keys are required for current local features.

## 9. Future External GenAI Requirements

Future optional external GenAI integration should require:

- Explicit user consent.
- PII redaction before provider calls.
- Provider configuration through environment variables.
- Timeout handling and local fallback behavior.
- Generated content disclaimers.
- Human review before use.
- Clear separation between prompt preview and external generation.

External GenAI should remain disabled unless these safeguards are intentionally implemented.

## 10. Logging and Storage Boundaries

ResumeIQ logs operational metadata such as endpoint, status code, latency, and success state. It should not intentionally log raw resume text, full job descriptions, or raw PII.

The local database stores summaries and workflow metadata by default. It should not be expanded to store full sensitive documents without a clear privacy design.
