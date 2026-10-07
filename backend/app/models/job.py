"""
PreprocessingJob and GenerationJob ORM models.
"""

from datetime import datetime, timezone
import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, JSON, Text, Enum
from sqlalchemy.orm import relationship
from app.database.session import Base

class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class GenerationMethod(str, enum.Enum):
    BASELINE_STATISTICAL = "BASELINE_STATISTICAL" # Copula/Empirical Gaussian Mixture (Non-DP)
    DP_SGD_NEURAL = "DP_SGD_NEURAL"               # PyTorch Deep Generative Model with DP-SGD (Differential Privacy)

class PreprocessingJob(Base):
    __tablename__ = "preprocessing_jobs"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False)
    config = Column(JSON, default=dict, nullable=False)
    summary = Column(JSON, default=dict, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime, nullable=True)

    dataset = relationship("Dataset", back_populates="preprocessing_jobs")

class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    model_version_id = Column(Integer, ForeignKey("model_versions.id", ondelete="SET NULL"), nullable=True)
    
    method = Column(Enum(GenerationMethod), nullable=False)
    num_records = Column(Integer, default=1000, nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False)
    progress_percentage = Column(Float, default=0.0, nullable=False)
    error_message = Column(Text, nullable=True)
    
    result_file_path = Column(String(512), nullable=True)
    result_row_count = Column(Integer, default=0, nullable=False)
    
    # Differential Privacy parameters
    epsilon_target = Column(Float, nullable=True)
    delta_target = Column(Float, nullable=True)
    epsilon_spent = Column(Float, default=0.0, nullable=False)
    delta_spent = Column(Float, default=0.0, nullable=False)
    clipping_norm = Column(Float, nullable=True)
    noise_multiplier = Column(Float, nullable=True)
    epochs = Column(Integer, default=20, nullable=False)
    batch_size = Column(Integer, default=64, nullable=False)
    learning_rate = Column(Float, default=0.001, nullable=False)
    
    # Formal guarantee disclosure
    has_formal_dp_guarantee = Column(Boolean, default=False, nullable=False)
    guarantee_disclaimer = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    dataset = relationship("Dataset", back_populates="generation_jobs")
    user = relationship("User", back_populates="generation_jobs")
    model_version = relationship("ModelVersion", back_populates="generation_jobs")
    privacy_accountings = relationship("PrivacyAccounting", back_populates="generation_job", cascade="all, delete-orphan")
    evaluation_reports = relationship("EvaluationReport", back_populates="generation_job", cascade="all, delete-orphan")
    export_histories = relationship("ExportHistory", back_populates="generation_job", cascade="all, delete-orphan")
