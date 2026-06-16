import os

from src.settings import get_settings


APP_NAME = "ResumeIQ"
APP_VERSION = "0.35.0"
APP_STAGE = "portfolio-polish"


def get_version_info() -> dict:
    settings = get_settings()
    return {
        "app_name": APP_NAME,
        "app_version": APP_VERSION,
        "app_stage": APP_STAGE,
        "deployment_env": str(settings.app_env or "local").strip() or "local",
        "git_commit": os.getenv("RESUMEIQ_GIT_COMMIT", "local").strip() or "local",
    }
