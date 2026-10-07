"""
Synthetic Generation API Endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.deps import get_current_user, require_analyst_or_admin
from app.models.user import User
from app.schemas.generation import GenerationJobCreate, GenerationJobResponse
from app.services.generation_service import GenerationService

router = APIRouter(prefix="/generation", tags=["Synthetic Generation"])

@router.post("/run", response_model=GenerationJobResponse)
def trigger_generation_job(
    job_in: GenerationJobCreate,
    request: Request,
    current_user: User = Depends(require_analyst_or_admin),
    db: Session = Depends(get_db)
):
    service = GenerationService(db)
    ip = request.client.host if request.client else None
    return service.create_and_run_generation(job_in=job_in, user=current_user, ip_address=ip)

@router.get("", response_model=List[GenerationJobResponse])
def list_generation_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = GenerationService(db)
    return service.get_all_jobs(skip=skip, limit=limit)

@router.get("/{job_id}", response_model=GenerationJobResponse)
def get_generation_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = GenerationService(db)
    return service.get_job(job_id)

@router.get("/{job_id}/export")
def download_synthetic_dataset(
    job_id: int,
    request: Request,
    current_user: User = Depends(require_analyst_or_admin),
    db: Session = Depends(get_db)
):
    service = GenerationService(db)
    ip = request.client.host if request.client else None
    file_path, filename = service.export_synthetic_dataset(job_id=job_id, user=current_user, ip_address=ip)
    
    return FileResponse(
        path=file_path,
        media_type="text/csv",
        filename=filename,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
