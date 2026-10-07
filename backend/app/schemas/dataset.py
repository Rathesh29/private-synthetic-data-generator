"""
Dataset Pydantic Schemas.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class DatasetColumnSchema(BaseModel):
    id: int
    column_name: str
    data_type: str
    is_identifier: bool
    is_target: bool
    is_nullable: bool
    missing_count: int
    unique_count: int
    sample_values: List[Any] = []
    stats: Dict[str, Any] = {}

    class Config:
        from_attributes = True

class DatasetResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    original_filename: str
    file_size_bytes: int
    row_count: int
    column_count: int
    status: str
    is_preprocessed: bool
    quality_score: float
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class QualityReport(BaseModel):
    dataset_id: int
    overall_quality_score: float
    total_rows: int
    total_columns: int
    duplicate_rows_count: int
    missing_values_count: int
    columns_with_missing_values: List[str]
    detected_identifiers: List[str]
    numerical_columns: List[str]
    categorical_columns: List[str]
    data_type_summary: Dict[str, int]
    column_quality: List[Dict[str, Any]]

class DatasetDetailResponse(DatasetResponse):
    columns: List[DatasetColumnSchema] = []
    quality_report: Optional[QualityReport] = None
