"""
EvaluationReport ORM model.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON, Text, DateTime
from sqlalchemy.orm import relationship
from app.database.session import Base

class EvaluationReport(Base):
    __tablename__ = "evaluation_reports"

    id = Column(Integer, primary_key=True, index=True)
    generation_job_id = Column(Integer, ForeignKey("generation_jobs.id", ondelete="CASCADE"), nullable=False)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    
    overall_utility_score = Column(Float, nullable=False) # 0 to 100
    privacy_risk_score = Column(Float, nullable=False)    # Low/Medium/High indicator (0 - 100 scale, lower is better)
    
    metrics_summary = Column(JSON, default=dict, nullable=False)
    # Statistical comparison by column (mean, median, std, min, max, JS-divergence, Wasserstein dist)
    column_metrics = Column(JSON, default=list, nullable=False)
    # Correlation matrix similarity & difference
    correlation_metrics = Column(JSON, default=dict, nullable=False)
    # Distribution comparisons (histograms, categorical value counts for real vs synthetic)
    distribution_comparisons = Column(JSON, default=dict, nullable=False)
    # Nearest neighbor distance analysis
    nearest_neighbor_risk = Column(JSON, default=dict, nullable=False)
    # Membership inference risk assessment (simulated shadow model attack)
    membership_inference_risk = Column(JSON, default=dict, nullable=False)
    # Disclaimers and assumptions
    limitations_disclosure = Column(JSON, default=dict, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    generation_job = relationship("GenerationJob", back_populates="evaluation_reports")
