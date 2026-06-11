import json

from database.repositories import (
    create_analysis_run,
    create_audit_log,
    create_batch_ranking_run,
    create_candidate_review_record,
    list_recent_analysis_runs,
)


def test_create_analysis_run(test_db_session):
    row = create_analysis_run(
        test_db_session,
        {
            "source": "pytest",
            "predicted_role": "Data Scientist",
            "ats_score": 82,
            "jd_match_score": 64,
        },
    )

    assert row.id is not None
    assert row.predicted_role == "Data Scientist"
    assert row.ats_score == 82


def test_create_batch_ranking_run(test_db_session):
    row = create_batch_ranking_run(
        test_db_session,
        {
            "total_resumes": 3,
            "average_fit_score": 71.5,
        },
    )

    assert row.id is not None
    assert row.total_resumes == 3
    assert row.average_fit_score == 71.5


def test_create_candidate_review_record(test_db_session):
    row = create_candidate_review_record(
        test_db_session,
        {
            "candidate_label": "Candidate 1",
            "manual_review_status": "Needs follow-up",
            "recruiter_note": "Review project evidence.",
        },
    )

    assert row.id is not None
    assert row.candidate_label == "Candidate 1"
    assert row.manual_review_status == "Needs follow-up"


def test_create_audit_log_stores_metadata_json(test_db_session):
    row = create_audit_log(
        test_db_session,
        event_type="analysis_saved",
        message="Analysis summary saved to database",
        metadata={"source": "pytest"},
    )

    assert row.id is not None
    assert row.event_type == "analysis_saved"
    assert json.loads(row.metadata_json) == {"source": "pytest"}


def test_list_recent_analysis_runs_respects_limit(test_db_session):
    for index in range(3):
        create_analysis_run(
            test_db_session,
            {
                "source": "pytest",
                "predicted_role": f"Role {index}",
            },
        )

    rows = list_recent_analysis_runs(test_db_session, limit=2)

    assert len(rows) == 2
