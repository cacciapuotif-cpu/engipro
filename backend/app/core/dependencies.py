"""
FastAPI dependencies for authentication and authorization.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import User, UserRole
from app.services.auth import AuthService

security = HTTPBearer()


async def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthCredentials = Depends(security),
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Args:
        db: Database session
        credentials: HTTP Bearer token
    
    Returns:
        Current user
    
    Raises:
        HTTPException: If token invalid or user not found
    """
    token = credentials.credentials
    
    try:
        user = AuthService.get_user_by_token(db, token)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user (already authenticated).
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        Current user if active
    
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    return current_user


def require_role(*roles: UserRole):
    """
    Dependency factory for role-based access control.
    
    Args:
        *roles: Allowed user roles
    
    Returns:
        Dependency function that checks user role
    """
    async def check_role(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        """Check if user has required role."""
        if current_user.role not in [role.value for role in roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User role '{current_user.role}' is not allowed",
            )
        return current_user
    
    return check_role
