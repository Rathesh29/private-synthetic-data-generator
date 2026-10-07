"""
Dataset and DatasetColumn ORM models.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from app.database.session import Base

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=True)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    row_count = Column(Integer, default=0, nullable=False)
    column_count = Column(Integer, default=0, nullable=False)
    status = Column(String(50), default="UPLOADED", nullable=False) # UPLOADED, PROCESSED, ERROR
    is_preprocessed = Column(Boolean, default=False, nullable=False)
    quality_score = Column(Float, default=100.0, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    owner = relationship("User", back_populates="datasets")
    columns = relationship("DatasetColumn", back_populates="dataset", cascade="all, delete-orphan")
    preprocessing_jobs = relationship("PreprocessingJob", back_populates="dataset", cascade="all, delete-orphan")
    generation_jobs = relationship("GenerationJob", back_populates="dataset", cascade="all, delete-orphan")

class DatasetColumn(Base):
    __tablename__ = "dataset_columns"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    column_name = Column(String(255), nullable=False)
    data_type = Column(String(50), nullable=False) # numerical, categorical, datetime, identifier
    is_identifier = Column(Boolean, default=False, nullable=False) # e.g. employee_id, ssn, name
    is_target = Column(Boolean, default=False, nullable=False)
    is_nullable = Column(Boolean, default=False, nullable=False)
    missing_count = Column(Integer, default=0, nullable=False)
    unique_count = Column(Integer, default=0, nullable=False)
    sample_values = Column(JSON, default=list, nullable=False)
    stats = Column(JSON, default=dict, nullable=False) # mean, std, min, max, median, quartiles or categories

    dataset = relationship("Dataset", back_populates="columns")
