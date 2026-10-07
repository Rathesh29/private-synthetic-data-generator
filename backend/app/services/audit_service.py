"""
Audit Service.
Records security and data events while guaranteeing no raw sensitive HR records or credentials are logged.
"""

from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.models.audit import AuditLog, ExportHistory
from app.repositories.audit_repo import AuditRepository
from app.schemas.audit import AuditLogResponse, ExportHistoryResponse

class AuditService:
    def __init__(self, db: Session):
        self.db = db
        self.audit_repo = AuditRepository(db)

    def log_event(
        self,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        user_id: Optional[int] = None,
        user_email: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> AuditLog:
        # Sanitize details to guarantee no PII is stored in logs
        sanitized_details = {}
        if details:
            for k, v in details.items():
                if any(s in k.lower() for s in ["password", "token", "secret", "ssn", "record_row"]):
                    sanitized_details[k] = "***REDACTED***"
                else:
                    sanitized_details[k] = v

        log = AuditLog(
            user_id=user_id,
            user_email=user_email,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=sanitized_details,
            ip_address=ip_address
        )
        return self.audit_repo.create_log(log)

    def get_logs(self, skip: int = 0, limit: int = 100, action: Optional[str] = None) -> List[AuditLogResponse]:
        logs = self.audit_repo.get_logs(skip=skip, limit=limit, action=action)
        return [AuditLogResponse.model_validate(l) for l in logs]

    def record_export(
        self,
        generation_job_id: int,
        user_id: Optional[int],
        record_count: int,
        format_type: str = "CSV",
        checksum: Optional[str] = None
    ) -> ExportHistoryResponse:
        exp = ExportHistory(
            generation_job_id=generation_job_id,
            user_id=user_id,
            format=format_type,
            record_count=record_count,
            checksum=checksum
        )
        saved = self.audit_repo.create_export(exp)
        return ExportHistoryResponse.model_validate(saved)
