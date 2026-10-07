"""
Differential Privacy Pydantic Schemas.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class PrivacyBudgetStatus(BaseModel):
    max_epsilon_budget: float
    total_epsilon_spent: float
    remaining_epsilon_budget: float
    is_budget_depleted: bool
    budget_utilization_pct: float
    total_training_runs: int
    active_guarantee_models: int
    delta_reference: float
    accounting_method: str
    explanation: str

class PrivacyAccountingResponse(BaseModel):
    id: int
    generation_job_id: Optional[int]
    model_version_id: Optional[int]
    accountant_method: str
    epsilon_spent: float
    delta_spent: float
    sample_rate: float
    noise_multiplier: float
    clipping_norm: float
    steps_computed: int
    cumulative_epsilon: float
    cumulative_delta: float
    assumptions_statement: str
    created_at: datetime

    class Config:
        from_attributes = True

class PrivacyTradeoffEstimate(BaseModel):
    noise_multiplier: float
    clipping_norm: float
    epochs: int
    batch_size: int
    dataset_size: int
    estimated_epsilon: float
    estimated_delta: float
    projected_utility_score: float
    privacy_risk_level: str # Very Low, Low, Moderate, High
    explanation: str
