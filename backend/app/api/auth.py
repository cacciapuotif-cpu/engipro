"""
Authentication API routes.
"""
from fastapi import Request, Path, APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_active_user, security
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, ConfigDict
from app.core.security import decode_token
from app.core.redis_client import revoke_token
from app.models import User
from app.schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    RefreshTokenRequest,
)
from app.services.auth import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        db: Database session
    
    Returns:
        Created user
    
    Raises:
        HTTPException: If email already exists or password invalid
    """
    try:
        user = AuthService.register(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    credentials: UserLogin,
    db: Session = Depends(get_db),
):
    """
    Login user and return tokens.
    
    Args:
        credentials: User email and password
        db: Database session
    
    Returns:
        Access and refresh tokens
    
    Raises:
        HTTPException: If credentials invalid
    """
    try:
        tokens = AuthService.login(db, credentials)
        request.state.user_id = int(decode_token(tokens.access_token)["sub"])
        return tokens
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """
    Refresh access token using refresh token.
    
    Args:
        request: Refresh token request
        db: Database session
    
    Returns:
        New access token
    
    Raises:
        HTTPException: If refresh token invalid
    """
    try:
        tokens = AuthService.refresh_access_token(db, request.refresh_token)
        return tokens
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get current authenticated user profile.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        Current user data
    """
    return current_user


class LogoutRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    refresh_token: str | None = None


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    body: LogoutRequest | None = None,
    current_user: User = Depends(get_current_active_user),
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> None:
    refresh_payload = None
    if body and body.refresh_token:
        refresh_payload = decode_token(body.refresh_token)
        if (not refresh_payload or refresh_payload.get("type") != "refresh"
                or refresh_payload.get("sub") != str(current_user.id)
                or not refresh_payload.get("jti")):
            raise HTTPException(401, "Refresh token non valido")
    payload = decode_token(credentials.credentials)
    if payload:
        revoke_token(payload)
    if refresh_payload:
        revoke_token(refresh_payload)
