"""
Audit and Export Logs Endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.deps import require_admin
from app.schemas.audit import AuditLogResponse, ExportHistoryResponse
from app.services.audit_service import AuditService
from app.repositories.audit_repo import AuditRepository

router = APIRouter(prefix="/audit", tags=["Security & Auditing"])

@router.get("/logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    action: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    service = AuditService(db)
    return service.get_logs(skip=skip, limit=limit, action=action)

@router.get("/exports", response_model=List[ExportHistoryResponse])
def get_export_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    repo = AuditRepository(db)
    exports = repo.get_exports(skip=skip, limit=limit)
    return [ExportHistoryResponse.model_validate(e) for e in exports]
