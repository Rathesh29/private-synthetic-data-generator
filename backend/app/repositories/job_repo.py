"""
Job Repository for Preprocessing and Generation Jobs.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.job import PreprocessingJob, GenerationJob, JobStatus
from app.models.evaluation import EvaluationReport

class JobRepository:
    def __init__(self, db: Session):
        self.db = db

    # Preprocessing Jobs
    def create_preprocessing_job(self, job: PreprocessingJob) -> PreprocessingJob:
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_preprocessing_job(self, job_id: int) -> Optional[PreprocessingJob]:
        return self.db.query(PreprocessingJob).filter(PreprocessingJob.id == job_id).first()

    def update_preprocessing_job(self, job: PreprocessingJob) -> PreprocessingJob:
        self.db.commit()
        self.db.refresh(job)
        return job

    # Generation Jobs
    def create_generation_job(self, job: GenerationJob) -> GenerationJob:
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_generation_job(self, job_id: int) -> Optional[GenerationJob]:
        return self.db.query(GenerationJob).filter(GenerationJob.id == job_id).first()

    def get_generation_jobs(self, skip: int = 0, limit: int = 100, user_id: Optional[int] = None) -> List[GenerationJob]:
        query = self.db.query(GenerationJob)
        if user_id is not None:
            query = query.filter(GenerationJob.user_id == user_id)
        return query.order_by(GenerationJob.created_at.desc()).offset(skip).limit(limit).all()

    def update_generation_job(self, job: GenerationJob) -> GenerationJob:
        self.db.commit()
        self.db.refresh(job)
        return job

    def count_generation_jobs(self) -> int:
        return self.db.query(GenerationJob).count()

    def count_by_status(self) -> dict:
        statuses = [JobStatus.PENDING, JobStatus.PROCESSING, JobStatus.COMPLETED, JobStatus.FAILED]
        counts = {}
        for s in statuses:
            counts[s.value] = self.db.query(GenerationJob).filter(GenerationJob.status == s).count()
        return counts

    # Evaluation Reports
    def create_evaluation_report(self, report: EvaluationReport) -> EvaluationReport:
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def get_evaluation_report_by_job_id(self, job_id: int) -> Optional[EvaluationReport]:
        return self.db.query(EvaluationReport).filter(EvaluationReport.generation_job_id == job_id).first()
