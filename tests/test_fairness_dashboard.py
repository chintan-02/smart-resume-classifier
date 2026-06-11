from src.fairness_dashboard import (
    calculate_fairness_summary,
    get_responsible_ai_checklist,
    get_synthetic_fairness_data,
)


def test_synthetic_fairness_data_returns_rows():
    rows = get_synthetic_fairness_data()

    assert rows
    assert all(isinstance(row, dict) for row in rows)


def test_synthetic_groups_are_demo_only():
    rows = get_synthetic_fairness_data()
    groups = {row.get("group") for row in rows}

    assert groups == {"Demo Group A", "Demo Group B", "Demo Group C", "Demo Group D"}


def test_synthetic_groups_do_not_use_protected_labels():
    protected_terms = {
        "male",
        "female",
        "age",
        "race",
        "ethnicity",
        "religion",
        "disability",
        "immigrant",
        "nationality",
    }
    rows = get_synthetic_fairness_data()

    for row in rows:
        group_text = str(row.get("group", "")).lower()
        assert all(term not in group_text for term in protected_terms)


def test_fairness_summary_contains_expected_keys():
    summary = calculate_fairness_summary(get_synthetic_fairness_data())

    assert "total_demo_applicants" in summary
    assert "recommendation_rate_gap" in summary
    assert "avg_fit_score_gap" in summary
    assert "monitoring_status" in summary


def test_responsible_ai_checklist_contains_core_items():
    titles = {item.get("title") for item in get_responsible_ai_checklist()}

    assert "No protected-attribute scoring" in titles
    assert "Privacy-safe display mode" in titles
    assert "Human review workflow" in titles
