"""
Model Version Pydantic Schemas.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class ModelVersionResponse(BaseModel):
    id: int
    name: str
    version_tag: str
    architecture: str
    description: Optional[str] = None
    dataset_id: Optional[int] = None
    training_config: Dict[str, Any] = {}
    epsilon_spent: float
    delta_spent: float
    has_formal_dp: bool
    training_loss_history: List[Dict[str, Any]] = []
    utility_score: float
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
