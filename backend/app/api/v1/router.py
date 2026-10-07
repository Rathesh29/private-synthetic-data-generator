"""
API v1 Router Aggregation.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    datasets,
    preprocessing,
    generation,
    privacy,
    models,
    evaluation,
    audit,
    dashboard
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(datasets.router)
api_router.include_router(preprocessing.router)
api_router.include_router(generation.router)
api_router.include_router(privacy.router)
api_router.include_router(models.router)
api_router.include_router(evaluation.router)
api_router.include_router(audit.router)
api_router.include_router(dashboard.router)
