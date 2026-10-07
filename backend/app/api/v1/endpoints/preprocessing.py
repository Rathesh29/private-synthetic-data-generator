"""
Preprocessing API Endpoints.
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.deps import require_analyst_or_admin
from app.models.user import User
from app.schemas.preprocessing import PreprocessingConfig, PreprocessingJobResponse
from app.services.preprocessing_service import PreprocessingService

router = APIRouter(prefix="/preprocessing", tags=["Data Preprocessing"])

@router.post("/run/{dataset_id}", response_model=PreprocessingJobResponse)
def run_preprocessing(
    dataset_id: int,
    config: PreprocessingConfig,
    request: Request,
    current_user: User = Depends(require_analyst_or_admin),
    db: Session = Depends(get_db)
):
    service = PreprocessingService(db)
    ip = request.client.host if request.client else None
    return service.run_preprocessing(dataset_id=dataset_id, config=config, user=current_user, ip_address=ip)
