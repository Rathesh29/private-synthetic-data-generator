"""
Dataset Service.
Handles dataset upload validation, schema detection, quality analysis, and lifecycle management.
Guarantees raw employee records are never exposed in log outputs.
"""

import os
import uuid
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.dataset import Dataset, DatasetColumn
from app.models.user import User
from app.repositories.dataset_repo import DatasetRepository
from app.repositories.audit_repo import AuditRepository
from app.models.audit import AuditLog
from app.schemas.dataset import DatasetResponse, DatasetDetailResponse, QualityReport

class DatasetService:
    def __init__(self, db: Session):
        self.db = db
        self.dataset_repo = DatasetRepository(db)
        self.audit_repo = AuditRepository(db)

    def validate_and_save_upload(
        self,
        file: UploadFile,
        dataset_name: str,
        description: Optional[str],
        user: User,
        ip_address: Optional[str] = None
    ) -> DatasetDetailResponse:
        # 1. Validate file extension
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format '{ext}'. Allowed formats: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )

        # 2. Read contents and check file size
        contents = file.file.read()
        file_size = len(contents)
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if file_size > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File exceeds maximum size limit of {settings.MAX_UPLOAD_SIZE_MB}MB."
            )
        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty."
            )

        # 3. Save to disk securely with uuid
        unique_name = f"{uuid.uuid4().hex}_{file.filename}"
        saved_file_path = os.path.join(settings.UPLOAD_DIR, unique_name)
        with open(saved_file_path, "wb") as f:
            f.write(contents)

        # 4. Load into DataFrame
        try:
            if ext == ".csv":
                df = pd.read_csv(saved_file_path)
            else:
                df = pd.read_excel(saved_file_path)
        except Exception as e:
            if os.path.exists(saved_file_path):
                os.remove(saved_file_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse tabular file: {str(e)}"
            )

        if df.empty or len(df.columns) == 0:
            if os.path.exists(saved_file_path):
                os.remove(saved_file_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dataset contains no rows or columns."
            )

        # 5. Data Quality Analysis
        total_rows = len(df)
        total_cols = len(df.columns)
        duplicate_rows = int(df.duplicated().sum())
        total_missing_cells = int(df.isna().sum().sum())
        missing_pct = (total_missing_cells / float(total_rows * total_cols)) * 100.0 if total_rows * total_cols > 0 else 0
        dup_pct = (duplicate_rows / float(total_rows)) * 100.0 if total_rows > 0 else 0
        
        # Quality score formula (100 - penalties)
        quality_score = max(10.0, round(100.0 - (missing_pct * 1.5) - (dup_pct * 2.0), 1))

        # 6. Create Dataset record
        dataset = Dataset(
            name=dataset_name or file.filename,
            description=description,
            original_filename=file.filename,
            file_path=saved_file_path,
            file_size_bytes=file_size,
            row_count=total_rows,
            column_count=total_cols,
            status="UPLOADED",
            is_preprocessed=False,
            quality_score=quality_score,
            user_id=user.id
        )
        saved_dataset = self.dataset_repo.create(dataset)

        # 7. Analyze each column & save DatasetColumn metadata
        columns_meta = []
        column_quality_list = []
        cols_with_missing = []
        detected_identifiers = []
        numerical_columns = []
        categorical_columns = []

        for col in df.columns:
            col_str = str(col)
            series = df[col]
            missing_count = int(series.isna().sum())
            if missing_count > 0:
                cols_with_missing.append(col_str)

            unique_count = int(series.nunique())
            col_lower = col_str.lower()
            
            # Identifier detection
            is_id = any(term in col_lower for term in ["id", "employee_id", "ssn", "uuid", "badge", "email"])
            if is_id:
                detected_identifiers.append(col_str)

            # Type detection
            if pd.api.types.is_numeric_dtype(series):
                dtype_label = "numerical"
                numerical_columns.append(col_str)
                valid_num = series.dropna()
                stats = {
                    "min": float(valid_num.min()) if not valid_num.empty else 0.0,
                    "max": float(valid_num.max()) if not valid_num.empty else 0.0,
                    "mean": round(float(valid_num.mean()), 2) if not valid_num.empty else 0.0,
                    "median": round(float(valid_num.median()), 2) if not valid_num.empty else 0.0,
                    "std": round(float(valid_num.std()), 2) if not valid_num.empty and valid_num.std() > 0 else 0.0
                }
            else:
                dtype_label = "categorical"
                categorical_columns.append(col_str)
                top_cats = series.dropna().astype(str).value_counts().head(8).to_dict()
                stats = {
                    "categories_count": unique_count,
                    "top_categories": top_cats
                }

            # Safe sample values (only non-sensitive samples)
            if is_id:
                sample_vals = ["***REDACTED_ID***"]
            else:
                sample_vals = [str(v) for v in series.dropna().head(3).tolist()]

            col_obj = DatasetColumn(
                dataset_id=saved_dataset.id,
                column_name=col_str,
                data_type=dtype_label,
                is_identifier=is_id,
                is_target=(col_lower in ["attrition", "performance_rating"]),
                is_nullable=(missing_count > 0),
                missing_count=missing_count,
                unique_count=unique_count,
                sample_values=sample_vals,
                stats=stats
            )
            columns_meta.append(col_obj)
            column_quality_list.append({
                "column_name": col_str,
                "data_type": dtype_label,
                "missing_count": missing_count,
                "missing_percentage": round((missing_count / float(total_rows)) * 100.0, 2),
                "unique_count": unique_count,
                "is_identifier": is_id
            })

        self.dataset_repo.add_columns(columns_meta)

        # 8. Audit log
        self.audit_repo.create_log(AuditLog(
            user_id=user.id,
            user_email=user.email,
            action="DATASET_UPLOADED",
            resource_type="DATASET",
            resource_id=str(saved_dataset.id),
            details={
                "dataset_name": saved_dataset.name,
                "rows": total_rows,
                "columns": total_cols,
                "quality_score": quality_score
            },
            ip_address=ip_address
        ))

        # Build quality report
        quality_rep = QualityReport(
            dataset_id=saved_dataset.id,
            overall_quality_score=quality_score,
            total_rows=total_rows,
            total_columns=total_cols,
            duplicate_rows_count=duplicate_rows,
            missing_values_count=total_missing_cells,
            columns_with_missing_values=cols_with_missing,
            detected_identifiers=detected_identifiers,
            numerical_columns=numerical_columns,
            categorical_columns=categorical_columns,
            data_type_summary={
                "numerical": len(numerical_columns),
                "categorical": len(categorical_columns),
                "identifiers": len(detected_identifiers)
            },
            column_quality=column_quality_list
        )

        resp = DatasetDetailResponse.model_validate(saved_dataset)
        resp.columns = self.dataset_repo.get_columns_by_dataset_id(saved_dataset.id)
        resp.quality_report = quality_rep
        return resp

    def get_dataset(self, dataset_id: int) -> DatasetDetailResponse:
        dataset = self.dataset_repo.get_by_id(dataset_id)
        if not dataset:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
        
        resp = DatasetDetailResponse.model_validate(dataset)
        resp.columns = self.dataset_repo.get_columns_by_dataset_id(dataset.id)
        return resp

    def get_all_datasets(self, skip: int = 0, limit: int = 100) -> List[DatasetResponse]:
        datasets = self.dataset_repo.get_all(skip=skip, limit=limit)
        return [DatasetResponse.model_validate(d) for d in datasets]

    def delete_dataset(self, dataset_id: int, user: User, ip_address: Optional[str] = None):
        dataset = self.dataset_repo.get_by_id(dataset_id)
        if not dataset:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
        
        # Check permissions: Admin or Owner
        if user.role.value != "ADMIN" and dataset.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

        # Remove physical file
        if os.path.exists(dataset.file_path):
            try:
                os.remove(dataset.file_path)
            except OSError:
                pass

        dataset_name = dataset.name
        self.dataset_repo.delete(dataset)

        self.audit_repo.create_log(AuditLog(
            user_id=user.id,
            user_email=user.email,
            action="DATASET_DELETED",
            resource_type="DATASET",
            resource_id=str(dataset_id),
            details={"dataset_name": dataset_name},
            ip_address=ip_address
        ))
