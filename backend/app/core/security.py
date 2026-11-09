"""
Security utilities: password hashing, JWT tokens, etc.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings


# Password hashing context
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    """Hash password using Argon2."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create JWT access token.
    
    Args:
        subject: User ID or claim to encode
        expires_delta: Token expiration time
    
    Returns:
        Encoded JWT token
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {
        "sub": subject,
        "jti": str(uuid4()),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def create_refresh_token(subject: str) -> str:
    """
    Create JWT refresh token.
    
    Args:
        subject: User ID
    
    Returns:
        Encoded JWT refresh token
    """
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    
    to_encode = {
        "sub": subject,
        "jti": str(uuid4()),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    Decode and verify JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except JWTError:
        return None


def validate_password(password: str) -> bool:
    """
    Validate password requirements.
    
    Args:
        password: Password to validate
    
    Returns:
        True if password meets requirements
    """
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        raise ValueError(f"La password deve contenere almeno {settings.PASSWORD_MIN_LENGTH} caratteri")
    if len(password) > settings.PASSWORD_MAX_LENGTH:
        raise ValueError(f"La password deve contenere al massimo {settings.PASSWORD_MAX_LENGTH} caratteri")
    requirements = (
        (any(c.isupper() for c in password), "una lettera maiuscola"),
        (any(c.islower() for c in password), "una lettera minuscola"),
        (any(c.isdigit() for c in password), "una cifra"),
        (any(not c.isalnum() and not c.isspace() for c in password), "un carattere speciale"),
    )
    missing = [description for present, description in requirements if not present]
    if missing:
        raise ValueError("La password deve contenere: " + ", ".join(missing))
    return True
