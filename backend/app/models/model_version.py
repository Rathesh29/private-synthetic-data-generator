"""
ModelVersion and PrivacyAccounting ORM models.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from app.database.session import Base

class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    version_tag = Column(String(50), nullable=False, unique=True)
    architecture = Column(String(100), nullable=False) # e.g. "DP-Tabular-VAE", "Gaussian-Copula-Baseline"
    description = Column(Text, nullable=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True)
    training_config = Column(JSON, default=dict, nullable=False)
    weights_path = Column(String(512), nullable=True)
    
    epsilon_spent = Column(Float, default=0.0, nullable=False)
    delta_spent = Column(Float, default=0.0, nullable=False)
    has_formal_dp = Column(Boolean, default=False, nullable=False)
    training_loss_history = Column(JSON, default=list, nullable=False)
    utility_score = Column(Float, default=0.0, nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime, nullable=True)

    generation_jobs = relationship("GenerationJob", back_populates="model_version")
    privacy_accountings = relationship("PrivacyAccounting", back_populates="model_version")

class PrivacyAccounting(Base):
    __tablename__ = "privacy_accounting"

    id = Column(Integer, primary_key=True, index=True)
    generation_job_id = Column(Integer, ForeignKey("generation_jobs.id", ondelete="CASCADE"), nullable=True)
    model_version_id = Column(Integer, ForeignKey("model_versions.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    accountant_method = Column(String(100), default="RDP_Subsampled_Gaussian", nullable=False)
    epsilon_spent = Column(Float, nullable=False)
    delta_spent = Column(Float, nullable=False)
    sample_rate = Column(Float, nullable=False)
    noise_multiplier = Column(Float, nullable=False)
    clipping_norm = Column(Float, nullable=False)
    steps_computed = Column(Integer, nullable=False)
    cumulative_epsilon = Column(Float, nullable=False)
    cumulative_delta = Column(Float, nullable=False)
    assumptions_statement = Column(Text, nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    generation_job = relationship("GenerationJob", back_populates="privacy_accountings")
    model_version = relationship("ModelVersion", back_populates="privacy_accountings")
