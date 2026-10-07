"""
Dataset Repository.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.dataset import Dataset, DatasetColumn

class DatasetRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, dataset_id: int) -> Optional[Dataset]:
        return self.db.query(Dataset).filter(Dataset.id == dataset_id).first()

    def get_all(self, skip: int = 0, limit: int = 100, user_id: Optional[int] = None) -> List[Dataset]:
        query = self.db.query(Dataset)
        if user_id is not None:
            query = query.filter(Dataset.user_id == user_id)
        return query.order_by(Dataset.created_at.desc()).offset(skip).limit(limit).all()

    def count(self) -> int:
        return self.db.query(Dataset).count()

    def create(self, dataset: Dataset) -> Dataset:
        self.db.add(dataset)
        self.db.commit()
        self.db.refresh(dataset)
        return dataset

    def update(self, dataset: Dataset) -> Dataset:
        self.db.commit()
        self.db.refresh(dataset)
        return dataset

    def delete(self, dataset: Dataset) -> None:
        self.db.delete(dataset)
        self.db.commit()

    def add_columns(self, columns: List[DatasetColumn]) -> None:
        self.db.add_all(columns)
        self.db.commit()

    def get_columns_by_dataset_id(self, dataset_id: int) -> List[DatasetColumn]:
        return self.db.query(DatasetColumn).filter(DatasetColumn.dataset_id == dataset_id).all()
