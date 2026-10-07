"""
Authentication Service.
Handles user registration, verification, token generation, and role checks.
"""

from datetime import datetime, timezone
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserLogin, TokenResponse, UserResponse
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from app.repositories.user_repo import UserRepository
from app.repositories.audit_repo import AuditRepository
from app.models.audit import AuditLog

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.audit_repo = AuditRepository(db)

    def register(self, user_in: UserCreate, ip_address: Optional[str] = None) -> UserResponse:
        existing = self.user_repo.get_by_email(user_in.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email address already exists."
            )

        hashed_pwd = get_password_hash(user_in.password)
        user = User(
            email=user_in.email.lower(),
            hashed_password=hashed_pwd,
            full_name=user_in.full_name,
            role=user_in.role or UserRole.HR_ANALYST,
            is_active=True
        )
        created_user = self.user_repo.create(user)

        # Audit log
        self.audit_repo.create_log(AuditLog(
            user_id=created_user.id,
            user_email=created_user.email,
            action="USER_REGISTERED",
            resource_type="USER",
            resource_id=str(created_user.id),
            details={"role": created_user.role.value},
            ip_address=ip_address
        ))

        return UserResponse.model_validate(created_user)

    def authenticate(self, credentials: UserLogin, ip_address: Optional[str] = None) -> TokenResponse:
        user = self.user_repo.get_by_email(credentials.email)
        if not user or not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive."
            )

        # Update last login
        user.last_login_at = datetime.now(timezone.utc)
        self.user_repo.update(user)

        # Generate tokens
        access_token = create_access_token(subject=user.id, role=user.role.value)
        refresh_token = create_refresh_token(subject=user.id)

        # Audit log
        self.audit_repo.create_log(AuditLog(
            user_id=user.id,
            user_email=user.email,
            action="LOGIN_SUCCESS",
            resource_type="USER",
            resource_id=str(user.id),
            details={"role": user.role.value},
            ip_address=ip_address
        ))

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=UserResponse.model_validate(user)
        )
