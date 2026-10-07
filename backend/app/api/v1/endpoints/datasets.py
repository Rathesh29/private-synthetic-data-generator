"""
Dataset Management Endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, Request, Query, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.deps import get_current_user, require_analyst_or_admin
from app.models.user import User
from app.schemas.dataset import DatasetResponse, DatasetDetailResponse, QualityReport
from app.services.dataset_service import DatasetService

router = APIRouter(prefix="/datasets", tags=["Datasets"])

@router.post("/upload", response_model=DatasetDetailResponse)
async def upload_dataset(
    request: Request,
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    current_user: User = Depends(require_analyst_or_admin),
    db: Session = Depends(get_db)
):
    service = DatasetService(db)
    ip = request.client.host if request.client else None
    return service.validate_and_save_upload(
        file=file,
        dataset_name=name or file.filename,
        description=description,
        user=current_user,
        ip_address=ip
    )

@router.get("", response_model=List[DatasetResponse])
def list_datasets(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = DatasetService(db)
    return service.get_all_datasets(skip=skip, limit=limit)

@router.get("/{dataset_id}", response_model=DatasetDetailResponse)
def get_dataset(
    dataset_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = DatasetService(db)
    return service.get_dataset(dataset_id)

@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dataset(
    dataset_id: int,
    request: Request,
    current_user: User = Depends(require_analyst_or_admin),
    db: Session = Depends(get_db)
):
    service = DatasetService(db)
    ip = request.client.host if request.client else None
    service.delete_dataset(dataset_id, user=current_user, ip_address=ip)
    return None
