"""
Preprocessing Pydantic Schemas.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.models.job import JobStatus

class PreprocessingConfig(BaseModel):
    drop_identifiers: bool = True
    identifier_columns: Optional[List[str]] = None
    numerical_imputation: str = "median"  # median, mean, zero
    categorical_imputation: str = "mode"  # mode, constant
    numerical_scaling: str = "minmax"     # minmax, standard, robust
    categorical_encoding: str = "onehot"  # onehot, label
    outlier_handling: str = "clip"        # clip, none, remove
    outlier_std_dev_threshold: float = 3.0

class PreprocessingJobResponse(BaseModel):
    id: int
    dataset_id: int
    user_id: int
    status: JobStatus
    config: Dict[str, Any]
    summary: Dict[str, Any]
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
