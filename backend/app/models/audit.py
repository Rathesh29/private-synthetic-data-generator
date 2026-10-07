"""
AuditLog and ExportHistory ORM models.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from app.database.session import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    user_email = Column(String(255), nullable=True)
    action = Column(String(100), nullable=False) # e.g. LOGIN, UPLOAD_DATASET, PREPROCESS, RUN_GENERATION, DOWNLOAD_SYNTHETIC
    resource_type = Column(String(50), nullable=False) # DATASET, JOB, MODEL, USER, SYSTEM
    resource_id = Column(String(100), nullable=True)
    details = Column(JSON, default=dict, nullable=False)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="audit_logs")

class ExportHistory(Base):
    __tablename__ = "export_history"

    id = Column(Integer, primary_key=True, index=True)
    generation_job_id = Column(Integer, ForeignKey("generation_jobs.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    format = Column(String(20), default="CSV", nullable=False)
    record_count = Column(Integer, nullable=False)
    checksum = Column(String(128), nullable=True)
    exported_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    generation_job = relationship("GenerationJob", back_populates="export_histories")
