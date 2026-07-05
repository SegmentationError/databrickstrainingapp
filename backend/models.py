"""
ORM models mirroring metadata_schema.sql. Kept intentionally thin — these are
for the metadata store (Lakebase/Postgres) only. The actual Delta table data
is never modeled here; it's queried/written through databricks_client.py.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Boolean, TIMESTAMP, BigInteger, Integer,
    ForeignKey, CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class RegisteredTable(Base):
    __tablename__ = "registered_tables"

    table_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    catalog_name = Column(String, nullable=False)
    schema_name = Column(String, nullable=False)
    table_name = Column(String, nullable=False)
    primary_key_column = Column(String, nullable=False)
    column_definitions = Column(JSONB, nullable=False)
    approver_user_id = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_by = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)


class CsvValidationJob(Base):
    __tablename__ = "csv_validation_jobs"

    job_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    table_id = Column(UUID(as_uuid=True), ForeignKey("registered_tables.table_id"), nullable=False)
    uploaded_by = Column(String, nullable=False)
    source_file_ref = Column(String, nullable=False)
    column_mapping = Column(JSONB)
    status = Column(String, nullable=False, default="processing")
    rows_total = Column(Integer)
    rows_matched = Column(Integer)
    rows_unmatched = Column(Integer)
    rows_type_error = Column(Integer)
    error_report_ref = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    completed_at = Column(TIMESTAMP(timezone=True))

    __table_args__ = (
        CheckConstraint("status IN ('processing','completed','failed')"),
    )


class UpdateRequest(Base):
    __tablename__ = "update_requests"

    request_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    table_id = Column(UUID(as_uuid=True), ForeignKey("registered_tables.table_id"), nullable=False)
    mode = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")

    requester_user_id = Column(String, nullable=False)
    approver_user_id = Column(String)
    rejection_reason = Column(String)

    change_set = Column(JSONB, nullable=False)
    row_count_affected = Column(Integer, nullable=False)

    csv_validation_job_id = Column(UUID(as_uuid=True), ForeignKey("csv_validation_jobs.job_id"))

    pre_apply_table_version = Column(BigInteger)
    post_apply_table_version = Column(BigInteger)
    error_message = Column(String)

    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    reviewed_at = Column(TIMESTAMP(timezone=True))
    applied_at = Column(TIMESTAMP(timezone=True))

    table = relationship("RegisteredTable")

    __table_args__ = (
        CheckConstraint("mode IN ('bulk','row_edit','csv')"),
        CheckConstraint(
            "status IN ('pending','approved','rejected','applying','applied','failed')"
        ),
        CheckConstraint(
            "approver_user_id IS NULL OR approver_user_id <> requester_user_id",
            name="approver_not_requester",
        ),
    )


class AuditLog(Base):
    __tablename__ = "audit_log"

    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String, nullable=False)
    request_id = Column(UUID(as_uuid=True), ForeignKey("update_requests.request_id"))
    table_id = Column(UUID(as_uuid=True), ForeignKey("registered_tables.table_id"), nullable=False)
    actor_user_id = Column(String, nullable=False)
    detail = Column(JSONB)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(
            "event_type IN ('submitted','approved','rejected','applied','failed','restored')"
        ),
    )
