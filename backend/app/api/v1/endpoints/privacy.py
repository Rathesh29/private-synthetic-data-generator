"""
Differential Privacy Endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.deps import get_current_user
from app.schemas.privacy import PrivacyBudgetStatus, PrivacyAccountingResponse, PrivacyTradeoffEstimate
from app.services.privacy_service import PrivacyService

router = APIRouter(prefix="/privacy", tags=["Differential Privacy"])

@router.get("/budget", response_model=PrivacyBudgetStatus)
def get_privacy_budget_status(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = PrivacyService(db)
    return service.get_budget_status()

@router.get("/estimate", response_model=PrivacyTradeoffEstimate)
def estimate_privacy_tradeoff(
    noise_multiplier: float = Query(1.1, ge=0.1, le=10.0),
    clipping_norm: float = Query(1.0, ge=0.1, le=10.0),
    epochs: int = Query(20, ge=1, le=200),
    batch_size: int = Query(64, ge=8, le=1024),
    dataset_size: int = Query(1000, ge=10),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = PrivacyService(db)
    return service.estimate_tradeoff(
        noise_multiplier=noise_multiplier,
        clipping_norm=clipping_norm,
        epochs=epochs,
        batch_size=batch_size,
        dataset_size=dataset_size
    )

@router.get("/history", response_model=List[PrivacyAccountingResponse])
def get_privacy_expenditure_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = PrivacyService(db)
    return service.get_privacy_history(skip=skip, limit=limit)
