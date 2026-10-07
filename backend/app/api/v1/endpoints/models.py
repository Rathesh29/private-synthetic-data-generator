"""
Model Version Management Endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.deps import get_current_user
from app.schemas.model_version import ModelVersionResponse
from app.repositories.privacy_repo import PrivacyRepository

router = APIRouter(prefix="/models", tags=["Model Management"])

@router.get("", response_model=List[ModelVersionResponse])
def list_models(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = PrivacyRepository(db)
    models = repo.get_all_models(skip=skip, limit=limit)
    return [ModelVersionResponse.model_validate(m) for m in models]

@router.get("/{model_id}", response_model=ModelVersionResponse)
def get_model(
    model_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = PrivacyRepository(db)
    model = repo.get_model_version(model_id)
    if not model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found")
    return ModelVersionResponse.model_validate(model)
