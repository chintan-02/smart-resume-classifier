from functools import lru_cache
from typing import Any

from src.app_config import SKILLS_PATH
from src.ats_scorer import calculate_ats_score
from src.jd_matcher import analyze_job_description_match
from src.prediction_service import load_model_artifacts, predict_resume_role
from src.preprocessing import preprocess_resume_text
from src.skill_extractor import load_skills
from src.monitoring import get_logger, log_event


API_DISCLAIMER = "ResumeIQ is a decision-support tool. This API response is not a hiring decision."
logger = get_logger(__name__)


@lru_cache(maxsize=1)
def _get_model_artifacts() -> tuple[Any | None, Any | None]:
    try:
        return load_model_artifacts()
    except Exception:
        return None, None


@lru_cache(maxsize=1)
def _get_skills() -> list[str]:
    try:
        return load_skills(SKILLS_PATH)
    except Exception:
        return []


def _base_response(privacy_mode: bool) -> dict:
    return {
        "status": "success",
        "predicted_role": None,
        "model_confidence": None,
        "ats_score": None,
        "jd_match_score": None,
        "matched_skills": [],
        "missing_skills": [],
        "priority_actions": ["Review combined signals before making decisions."],
        "privacy_mode": privacy_mode,
        "disclaimer": API_DISCLAIMER,
    }


def _add_action(actions: list[str], message: str) -> None:
    if message not in actions:
        actions.append(message)


def analyze_resume_text(
    resume_text: str,
    job_description: str | None = None,
    privacy_mode: bool = False,
) -> dict:
    log_event(
        logger,
        "analysis_started",
        "Resume analysis started.",
        {
            "source": "fastapi",
            "privacy_mode": privacy_mode,
            "has_jd": bool((job_description or "").strip()),
        },
    )
    response = _base_response(privacy_mode)
    try:
        clean_resume_text = preprocess_resume_text(resume_text)
        job_description = job_description or ""

        model, vectorizer = _get_model_artifacts()
        if model is None:
            _add_action(
                response["priority_actions"],
                "Prediction model artifacts are unavailable; review other signals manually.",
            )
        else:
            try:
                prediction_result = predict_resume_role(clean_resume_text, model, vectorizer)
                response["predicted_role"] = prediction_result.get("role") or None
                response["model_confidence"] = prediction_result.get("confidence")
                log_event(
                    logger,
                    "prediction_completed",
                    "Prediction signal completed.",
                    {
                        "source": "fastapi",
                        "predicted_role": response.get("predicted_role"),
                        "model_confidence": response.get("model_confidence"),
                        "privacy_mode": privacy_mode,
                    },
                )
            except Exception:
                _add_action(
                    response["priority_actions"],
                    "Prediction signal could not be calculated for this request.",
                )

        if not job_description.strip():
            _add_action(response["priority_actions"], "Add a job description to calculate job-match signals.")
            log_event(
                logger,
                "analysis_completed",
                "Resume analysis completed without job description.",
                {
                    "source": "fastapi",
                    "predicted_role": response.get("predicted_role"),
                    "model_confidence": response.get("model_confidence"),
                    "privacy_mode": privacy_mode,
                    "success": True,
                },
            )
            return response

        skills_list = _get_skills()
        match_result = None
        try:
            match_result = analyze_job_description_match(clean_resume_text, job_description, skills_list)
            gap = match_result.get("gap", {}) or {}
            response["jd_match_score"] = match_result.get("match_score")
            response["matched_skills"] = gap.get("matched", [])
            response["missing_skills"] = gap.get("missing", [])
        except Exception:
            _add_action(
                response["priority_actions"],
                "Job-description match signal could not be calculated for this request.",
            )

        try:
            gap = (match_result or {}).get("gap", {}) or {}
            ats_result = calculate_ats_score(
                resume_text=resume_text,
                job_description=job_description,
                resume_skills=(match_result or {}).get("resume_skills", []),
                jd_skills=(match_result or {}).get("jd_skills", []),
                matched_skills=gap.get("matched", []),
                missing_skills=gap.get("missing", []),
                parser_result=None,
                existing_match_score=(match_result or {}).get("match_score"),
            )
            response["ats_score"] = ats_result.get("ats_score")
            for action in ats_result.get("improvements", [])[:3]:
                _add_action(response["priority_actions"], action)
        except Exception:
            _add_action(
                response["priority_actions"],
                "ATS compatibility signal could not be calculated for this request.",
            )

        log_event(
            logger,
            "analysis_completed",
            "Resume analysis completed.",
            {
                "source": "fastapi",
                "predicted_role": response.get("predicted_role"),
                "model_confidence": response.get("model_confidence"),
                "ats_score": response.get("ats_score"),
                "jd_match_score": response.get("jd_match_score"),
                "privacy_mode": privacy_mode,
                "success": True,
            },
        )
        return response
    except Exception:
        log_event(
            logger,
            "analysis_failed",
            "Resume analysis failed safely.",
            {
                "source": "fastapi",
                "privacy_mode": privacy_mode,
                "success": False,
            },
            level="warning",
        )
        raise
