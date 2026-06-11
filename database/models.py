from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text

from database.db import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    source = Column(String, nullable=True)
    resume_filename = Column(String, nullable=True)
    predicted_role = Column(String, nullable=True)
    model_confidence = Column(Float, nullable=True)
    ats_score = Column(Float, nullable=True)
    jd_match_score = Column(Float, nullable=True)
    semantic_score = Column(Float, nullable=True)
    overall_fit_score = Column(Float, nullable=True)
    fit_label = Column(String, nullable=True)
    recommendation = Column(String, nullable=True)
    privacy_mode = Column(Boolean, default=False, nullable=False)
    notes = Column(Text, nullable=True)


class BatchRankingRun(Base):
    __tablename__ = "batch_ranking_runs"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    job_description_hash = Column(String, nullable=True)
    total_resumes = Column(Integer, default=0, nullable=False)
    average_fit_score = Column(Float, nullable=True)
    recommended_count = Column(Integer, default=0, nullable=False)
    privacy_mode = Column(Boolean, default=False, nullable=False)
    notes = Column(Text, nullable=True)


class CandidateReviewRecord(Base):
    __tablename__ = "candidate_review_records"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    batch_run_id = Column(Integer, nullable=True)
    candidate_label = Column(String, nullable=True)
    resume_filename = Column(String, nullable=True)
    rank = Column(Integer, nullable=True)
    overall_fit_score = Column(Float, nullable=True)
    fit_label = Column(String, nullable=True)
    recommendation = Column(String, nullable=True)
    manual_review_status = Column(String, nullable=True)
    recruiter_note = Column(Text, nullable=True)
    priority_actions = Column(Text, nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    event_type = Column(String, nullable=False)
    event_source = Column(String, nullable=True)
    message = Column(Text, nullable=False)
    metadata_json = Column(Text, nullable=True)


class ApiRequestLog(Base):
    __tablename__ = "api_request_logs"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    status_code = Column(Integer, nullable=True)
    latency_ms = Column(Float, nullable=True)
    success = Column(Boolean, default=True, nullable=False)
    message = Column(Text, nullable=True)
