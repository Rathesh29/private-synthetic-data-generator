"""
Dashboard Statistics Endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.deps import get_current_user
from app.schemas.dashboard import DashboardStatsResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_statistics(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = DashboardService(db)
    return service.get_dashboard_stats()
