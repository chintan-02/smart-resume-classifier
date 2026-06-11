# ResumeIQ Model Registry Foundation

ResumeIQ uses a local JSON-based model registry to document baseline model metadata, evaluation notes, and responsible AI caveats.

The registry is intentionally lightweight:

- stores model metadata and evaluation summaries
- stores a baseline model card
- does not store model binaries
- does not store full resume text
- does not store raw PII

MLflow or a cloud model registry can be added later when the project is ready for experiment tracking and deployment governance.
