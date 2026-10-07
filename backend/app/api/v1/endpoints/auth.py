"""
Authentication Endpoints.
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.user import UserCreate, UserLogin, TokenResponse, UserResponse
from app.services.auth_service import AuthService
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, request: Request, db: Session = Depends(get_db)):
    ip = request.client.host if request.client else None
    service = AuthService(db)
    return service.register(user_in, ip_address=ip)

@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, request: Request, db: Session = Depends(get_db)):
    ip = request.client.host if request.client else None
    service = AuthService(db)
    return service.authenticate(credentials, ip_address=ip)

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)
