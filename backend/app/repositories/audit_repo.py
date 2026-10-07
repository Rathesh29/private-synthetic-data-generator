"""
Audit and Export Repository.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.audit import AuditLog, ExportHistory

class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_log(self, log: AuditLog) -> AuditLog:
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def get_logs(self, skip: int = 0, limit: int = 100, action: Optional[str] = None) -> List[AuditLog]:
        query = self.db.query(AuditLog)
        if action:
            query = query.filter(AuditLog.action == action)
        return query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()

    def count_logs(self) -> int:
        return self.db.query(AuditLog).count()

    def create_export(self, export: ExportHistory) -> ExportHistory:
        self.db.add(export)
        self.db.commit()
        self.db.refresh(export)
        return export

    def get_exports(self, skip: int = 0, limit: int = 100) -> List[ExportHistory]:
        return self.db.query(ExportHistory).order_by(ExportHistory.exported_at.desc()).offset(skip).limit(limit).all()
