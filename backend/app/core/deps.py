"""
Authentication & Authorization Dependencies.
Enforces JWT validation and Role-Based Access Control (RBAC).
"""

from typing import List, Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.security import decode_token
from app.database.session import get_db
from app.models.user import User, UserRole
from app.repositories.user_repo import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
        
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    user_repo = UserRepository(db)
    user = user_repo.get_by_id(int(user_id_str))
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )

    return user

def require_roles(allowed_roles: List[UserRole]) -> Callable[[User], User]:
    """Factory creating dependency to check user role."""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Action forbidden for role '{current_user.role.value}'. Requires one of: {[r.value for r in allowed_roles]}"
            )
        return current_user
    return role_checker

# Predefined role dependencies
require_admin = require_roles([UserRole.ADMIN])
require_analyst_or_admin = require_roles([UserRole.ADMIN, UserRole.HR_ANALYST])
require_any_authenticated = get_current_user
