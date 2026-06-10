from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

ARTIFACT_DIR = BASE_DIR / "artifacts"
DATA_DIR = BASE_DIR / "data"

MODEL_PATH = ARTIFACT_DIR / "resume_classifier.pkl"
VECTORIZER_PATH = ARTIFACT_DIR / "vectorizer.pkl"
SKILLS_PATH = DATA_DIR / "skills_list.txt"
METRICS_PATH = ARTIFACT_DIR / "metrics.json"
SAMPLE_JD_PATH = DATA_DIR / "sample_job_description.txt"

SUPPORTED_FILE_TYPES = ["pdf", "txt", "docx"]
SUPPORTED_FILE_EXTENSIONS = {".pdf", ".txt", ".docx"}

APP_TITLE = "ResumeIQ"
APP_PAGE_ICON = "📄"
APP_LAYOUT = "wide"
APP_INITIAL_SIDEBAR_STATE = "expanded"
