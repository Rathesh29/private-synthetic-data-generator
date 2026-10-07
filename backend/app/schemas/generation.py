"""
Synthetic Generation Pydantic Schemas.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from app.models.job import JobStatus, GenerationMethod

class GenerationJobCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    dataset_id: int
    method: GenerationMethod = GenerationMethod.DP_SGD_NEURAL
    num_records: int = Field(default=1000, ge=10, le=100000)
    
    # Differential Privacy Hyperparameters (for DP_SGD_NEURAL)
    epsilon_target: Optional[float] = Field(default=1.0, ge=0.01, le=50.0)
    delta_target: Optional[float] = Field(default=1e-5, ge=1e-8, le=1e-2)
    clipping_norm: Optional[float] = Field(default=1.0, ge=0.1, le=10.0)
    noise_multiplier: Optional[float] = Field(default=1.1, ge=0.1, le=10.0)
    epochs: int = Field(default=20, ge=1, le=200)
    batch_size: int = Field(default=64, ge=8, le=1024)
    learning_rate: float = Field(default=0.001, ge=0.00001, le=0.1)

class GenerationJobResponse(BaseModel):
    id: int
    name: str
    dataset_id: int
    user_id: int
    model_version_id: Optional[int] = None
    method: GenerationMethod
    num_records: int
    status: JobStatus
    progress_percentage: float
    error_message: Optional[str] = None
    result_row_count: int
    
    epsilon_target: Optional[float] = None
    delta_target: Optional[float] = None
    epsilon_spent: float
    delta_spent: float
    clipping_norm: Optional[float] = None
    noise_multiplier: Optional[float] = None
    epochs: int
    batch_size: int
    learning_rate: float
    
    has_formal_dp_guarantee: bool
    guarantee_disclaimer: Optional[str] = None
    
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class GenerationJobProgress(BaseModel):
    job_id: int
    status: JobStatus
    progress_percentage: float
    current_epoch: int
    total_epochs: int
    current_loss: Optional[float] = None
    epsilon_spent: float
    delta_spent: float
