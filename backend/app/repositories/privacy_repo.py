"""
Privacy Repository: Manages PrivacyAccounting and ModelVersions.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.model_version import ModelVersion, PrivacyAccounting

class PrivacyRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_model_version(self, model: ModelVersion) -> ModelVersion:
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def get_model_version(self, model_id: int) -> Optional[ModelVersion]:
        return self.db.query(ModelVersion).filter(ModelVersion.id == model_id).first()

    def get_all_models(self, skip: int = 0, limit: int = 100) -> List[ModelVersion]:
        return self.db.query(ModelVersion).order_by(ModelVersion.created_at.desc()).offset(skip).limit(limit).all()

    def count_models(self) -> int:
        return self.db.query(ModelVersion).count()

    def create_privacy_record(self, record: PrivacyAccounting) -> PrivacyAccounting:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_privacy_records(self, skip: int = 0, limit: int = 100) -> List[PrivacyAccounting]:
        return self.db.query(PrivacyAccounting).order_by(PrivacyAccounting.created_at.desc()).offset(skip).limit(limit).all()

    def get_total_epsilon_spent(self) -> float:
        total = self.db.query(func.sum(PrivacyAccounting.epsilon_spent)).scalar()
        return round(float(total or 0.0), 4)

    def count_active_guarantee_models(self) -> int:
        return self.db.query(ModelVersion).filter(ModelVersion.has_formal_dp == True).count()
