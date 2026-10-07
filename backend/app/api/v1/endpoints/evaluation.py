"""
Evaluation and Comparison Endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.deps import get_current_user
from app.schemas.evaluation import EvaluationReportResponse
from app.services.generation_service import GenerationService

router = APIRouter(prefix="/evaluation", tags=["Evaluation & Utility"])

@router.get("/job/{job_id}", response_model=EvaluationReportResponse)
def get_job_evaluation(
    job_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = GenerationService(db)
    return service.get_job_evaluation(job_id)
