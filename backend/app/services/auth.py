"""
Authentication service - business logic for user auth operations.
"""
from datetime import timedelta
from sqlalchemy.orm import Session
from app.models import User, UserRole
from app.schemas import UserCreate, UserLogin, TokenResponse
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    validate_password,
)
from app.core.config import settings


class AuthService:
    """Authentication service."""
    
    @staticmethod
    def register(db: Session, user_data: UserCreate) -> User:
        """
        Register a new user.
        
        Args:
            db: Database session
            user_data: User registration data
        
        Returns:
            Created user
        
        Raises:
            ValueError: If email already exists or password invalid
        """
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ValueError(f"User with email {user_data.email} already exists")
        
        # Validate password
        validate_password(user_data.password)
        
        # Create new user
        user = User(
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            full_name=user_data.full_name,
            role=user_data.role,
            is_active=True,
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def login(db: Session, credentials: UserLogin) -> TokenResponse:
        """
        Login user and return tokens.
        
        Args:
            db: Database session
            credentials: User login credentials
        
        Returns:
            Access and refresh tokens
        
        Raises:
            ValueError: If credentials invalid or user inactive
        """
        # Find user by email
        user = db.query(User).filter(User.email == credentials.email).first()
        if not user:
            raise ValueError("Invalid email or password")
        
        # Check if user is active
        if not user.is_active:
            raise ValueError("User account is inactive")
        
        # Verify password
        if not verify_password(credentials.password, user.hashed_password):
            raise ValueError("Invalid email or password")
        
        # Generate tokens
        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id))
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
    
    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> TokenResponse:
        """
        Refresh access token using refresh token.
        
        Args:
            db: Database session
            refresh_token: Refresh token string
        
        Returns:
            New access token and same refresh token
        
        Raises:
            ValueError: If refresh token invalid or expired
        """
        # Decode refresh token
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise ValueError("Invalid refresh token")
        
        user_id = payload.get("sub")
        
        # Verify user still exists
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user or not user.is_active:
            raise ValueError("User not found or inactive")
        
        # Generate new access token
        access_token = create_access_token(subject=str(user.id))
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
    
    @staticmethod
    def get_user_by_token(db: Session, token: str) -> User:
        """
        Get user from access token.
        
        Args:
            db: Database session
            token: JWT access token
        
        Returns:
            User object
        
        Raises:
            ValueError: If token invalid or user not found
        """
        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            raise ValueError("Invalid access token")
        
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == int(user_id)).first()
        
        if not user:
            raise ValueError("User not found")
        
        return user
