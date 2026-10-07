"""
Audit and Export Schemas.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel

class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    user_email: Optional[str]
    action: str
    resource_type: str
    resource_id: Optional[str]
    details: Dict[str, Any]
    ip_address: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class ExportHistoryResponse(BaseModel):
    id: int
    generation_job_id: int
    user_id: Optional[int]
    format: str
    record_count: int
    checksum: Optional[str]
    exported_at: datetime

    class Config:
        from_attributes = True
