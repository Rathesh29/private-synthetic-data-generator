"""
Evaluation and Quality Comparison Schemas.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class EvaluationReportResponse(BaseModel):
    id: int
    generation_job_id: int
    dataset_id: int
    overall_utility_score: float
    privacy_risk_score: float
    metrics_summary: Dict[str, Any]
    column_metrics: List[Dict[str, Any]]
    correlation_metrics: Dict[str, Any]
    distribution_comparisons: Dict[str, Any]
    nearest_neighbor_risk: Dict[str, Any]
    membership_inference_risk: Dict[str, Any]
    limitations_disclosure: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True
