"""
Preprocessing Service.
Executes data preprocessing pipelines and stores metadata for reproducibility.
"""

from datetime import datetime, timezone
import os
import pandas as pd
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.job import PreprocessingJob, JobStatus
from app.models.user import User
from app.schemas.preprocessing import PreprocessingConfig, PreprocessingJobResponse
from app.repositories.dataset_repo import DatasetRepository
from app.repositories.job_repo import JobRepository
from app.repositories.audit_repo import AuditRepository
from app.models.audit import AuditLog
from app.ml.preprocessor import TabularDataPreprocessor

class PreprocessingService:
    def __init__(self, db: Session):
        self.db = db
        self.dataset_repo = DatasetRepository(db)
        self.job_repo = JobRepository(db)
        self.audit_repo = AuditRepository(db)

    def run_preprocessing(
        self,
        dataset_id: int,
        config: PreprocessingConfig,
        user: User,
        ip_address: str = None
    ) -> PreprocessingJobResponse:
        dataset = self.dataset_repo.get_by_id(dataset_id)
        if not dataset:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")

        job = PreprocessingJob(
            dataset_id=dataset.id,
            user_id=user.id,
            status=JobStatus.PROCESSING,
            config=config.model_dump(),
            summary={}
        )
        saved_job = self.job_repo.create_preprocessing_job(job)

        try:
            # Load dataset
            if not os.path.exists(dataset.file_path):
                raise ValueError("Source dataset file missing from storage.")

            if dataset.file_path.endswith(".csv"):
                df = pd.read_csv(dataset.file_path)
            else:
                df = pd.read_excel(dataset.file_path)

            preprocessor = TabularDataPreprocessor(config.model_dump())
            preprocessor.fit(df, custom_identifiers=config.identifier_columns)
            summary = preprocessor.get_summary()

            saved_job.status = JobStatus.COMPLETED
            saved_job.summary = summary
            saved_job.completed_at = datetime.now(timezone.utc)
            self.job_repo.update_preprocessing_job(saved_job)

            # Mark dataset as preprocessed
            dataset.is_preprocessed = True
            dataset.status = "PROCESSED"
            self.dataset_repo.update(dataset)

            self.audit_repo.create_log(AuditLog(
                user_id=user.id,
                user_email=user.email,
                action="DATASET_PREPROCESSED",
                resource_type="JOB",
                resource_id=str(saved_job.id),
                details={"dataset_id": dataset.id, "config": config.model_dump()},
                ip_address=ip_address
            ))

            return PreprocessingJobResponse.model_validate(saved_job)

        except Exception as e:
            saved_job.status = JobStatus.FAILED
            saved_job.error_message = str(e)
            saved_job.completed_at = datetime.now(timezone.utc)
            self.job_repo.update_preprocessing_job(saved_job)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Preprocessing failed: {str(e)}"
            )
