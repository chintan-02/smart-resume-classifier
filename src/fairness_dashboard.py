def get_fairness_intro() -> dict:
    return {
        "title": "Responsible AI Fairness Dashboard",
        "description": "Synthetic/demo monitoring view for understanding fairness risks in resume screening workflows.",
        "disclaimer": (
            "This dashboard uses synthetic aggregate data only. ResumeIQ does not collect, infer, "
            "or score protected attributes from uploaded resumes."
        ),
        "safe_use": "Use this section to understand monitoring concepts, not to make hiring decisions.",
    }


def get_synthetic_fairness_data() -> list[dict]:
    return [
        {
            "group": "Demo Group A",
            "applicants": 120,
            "average_fit_score": 74,
            "recommended_for_review_rate": 62,
            "shortlist_rate": 35,
            "false_positive_proxy": 8,
            "false_negative_proxy": 11,
        },
        {
            "group": "Demo Group B",
            "applicants": 110,
            "average_fit_score": 69,
            "recommended_for_review_rate": 54,
            "shortlist_rate": 30,
            "false_positive_proxy": 10,
            "false_negative_proxy": 14,
        },
        {
            "group": "Demo Group C",
            "applicants": 95,
            "average_fit_score": 66,
            "recommended_for_review_rate": 45,
            "shortlist_rate": 24,
            "false_positive_proxy": 12,
            "false_negative_proxy": 17,
        },
        {
            "group": "Demo Group D",
            "applicants": 105,
            "average_fit_score": 71,
            "recommended_for_review_rate": 58,
            "shortlist_rate": 32,
            "false_positive_proxy": 9,
            "false_negative_proxy": 13,
        },
    ]


def calculate_fairness_summary(rows: list[dict]) -> dict:
    total_demo_applicants = sum(row.get("applicants", 0) for row in rows or [])
    recommendation_rates = [row.get("recommended_for_review_rate", 0) for row in rows or []]
    avg_fit_scores = [row.get("average_fit_score", 0) for row in rows or []]

    highest_recommended_rate = max(recommendation_rates, default=0)
    lowest_recommended_rate = min(recommendation_rates, default=0)
    recommendation_rate_gap = highest_recommended_rate - lowest_recommended_rate

    highest_avg_fit_score = max(avg_fit_scores, default=0)
    lowest_avg_fit_score = min(avg_fit_scores, default=0)
    avg_fit_score_gap = highest_avg_fit_score - lowest_avg_fit_score

    if recommendation_rate_gap >= 20:
        monitoring_status = "Needs review"
    elif recommendation_rate_gap >= 10:
        monitoring_status = "Watch"
    else:
        monitoring_status = "Stable demo signal"

    return {
        "total_demo_applicants": total_demo_applicants,
        "highest_recommended_rate": highest_recommended_rate,
        "lowest_recommended_rate": lowest_recommended_rate,
        "recommendation_rate_gap": recommendation_rate_gap,
        "highest_avg_fit_score": highest_avg_fit_score,
        "lowest_avg_fit_score": lowest_avg_fit_score,
        "avg_fit_score_gap": avg_fit_score_gap,
        "monitoring_status": monitoring_status,
    }


def get_fairness_metric_cards(summary: dict) -> list[dict]:
    return [
        {
            "title": "Demo Applicants",
            "value": str(summary.get("total_demo_applicants", 0)),
            "helper_text": "Synthetic/demo aggregate rows only",
        },
        {
            "title": "Recommendation Rate Gap",
            "value": f"{summary.get('recommendation_rate_gap', 0)} pts",
            "helper_text": "Highest minus lowest synthetic recommendation rate",
        },
        {
            "title": "Avg Fit Score Gap",
            "value": f"{summary.get('avg_fit_score_gap', 0)} pts",
            "helper_text": "Highest minus lowest synthetic average fit score",
        },
        {
            "title": "Monitoring Status",
            "value": summary.get("monitoring_status", "Stable demo signal"),
            "helper_text": "Demo monitoring concept, not a hiring decision",
        },
    ]


def get_fairness_risk_notes(summary: dict) -> list[str]:
    notes = [
        "Large gaps in recommendation rates may indicate a need for process review.",
        "Synthetic demo groups are used only to demonstrate monitoring concepts.",
        "Real fairness analysis requires legally and ethically collected data, proper governance, and expert review.",
        "ResumeIQ does not infer protected attributes from resume text.",
    ]
    if summary.get("monitoring_status") == "Needs review":
        notes.insert(0, "This synthetic demo signal would require human review before any process conclusions.")
    return notes


def get_responsible_ai_checklist() -> list[dict]:
    return [
        {
            "title": "No protected-attribute scoring",
            "status": "Implemented",
            "description": (
                "ResumeIQ does not score protected attributes such as gender, race, age, religion, "
                "disability, marital status, or immigration status."
            ),
        },
        {
            "title": "Privacy-safe display mode",
            "status": "Implemented",
            "description": "Common personal identifiers can be masked in review screens and exports.",
        },
        {
            "title": "Human review workflow",
            "status": "Implemented",
            "description": "Recruiters can review, add notes, and make manual decision-support records.",
        },
        {
            "title": "Prediction explainability",
            "status": "Implemented",
            "description": "The app shows local supporting terms and confidence interpretation for baseline predictions.",
        },
        {
            "title": "Synthetic fairness monitoring",
            "status": "Demo only",
            "description": "Fairness dashboard uses synthetic aggregate demo data only.",
        },
    ]


def get_fairness_limitations() -> list[str]:
    return [
        "Synthetic data does not prove real-world fairness.",
        "This dashboard does not replace legal, HR, or compliance review.",
        "Uploaded resumes are not grouped by protected characteristics.",
        "Fairness monitoring requires appropriate governance and consent.",
        "Automated scores should not be used as final hiring decisions.",
    ]
