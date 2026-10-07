"""
Private Synthetic Data Generator for HR Records - Main FastAPI Application.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging_config import logger
from app.api.v1.router import api_router
from app.database.seed import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB and seed demo accounts & datasets
    logger.info("Starting up Private Synthetic Data Generator backend...")
    init_db()
    logger.info("Database initialized and verified.")
    yield
    # Shutdown
    logger.info("Shutting down backend...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Production-grade Privacy-Preserving Synthetic Data Generator for sensitive HR records. "
        "Integrates DP-SGD, Rényi Differential Privacy accounting, empirical distribution modeling, "
        "and empirical privacy/utility assessment metrics."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS + ["*"], # Allows dev ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception on {request.method} {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please contact the administrator."}
    )
