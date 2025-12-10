# app/auth/jwt.py
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union
from jose import jwt, JWTError
from fastapi import HTTPException, status
from uuid import UUID
import secrets

from app.core.config import get_settings
from app.schemas.token import TokenType

settings = get_settings()

def create_token(
    user_id_or_data: Union[str, UUID, int, dict],
    token_type: TokenType,
    username: Optional[str] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT token (access or refresh).
    Accepts either:
    - user_id + username as separate args (new style)
    - dict with 'sub' key (old style for backward compatibility)
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        if token_type == TokenType.ACCESS:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )

    # Handle both old style (dict) and new style (primitives)
    if isinstance(user_id_or_data, dict):
        # Old style: {"sub": "user_id"}
        user_id = user_id_or_data.get("sub")
        username = user_id_or_data.get("username", "unknown")
    else:
        # New style: user_id and username as separate args
        user_id = user_id_or_data
        if username is None:
            username = "unknown"

    # Convert UUID or int to string for JWT
    if isinstance(user_id, (UUID, int)):
        user_id = str(user_id)

    to_encode = {
        "sub": user_id,
        "username": username,
        "type": token_type.value,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "jti": secrets.token_hex(16)
    }

    secret = (
        settings.JWT_SECRET_KEY 
        if token_type == TokenType.ACCESS 
        else settings.JWT_REFRESH_SECRET_KEY
    )

    try:
        return jwt.encode(to_encode, secret, algorithm=settings.ALGORITHM)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not create token: {str(e)}"
        )

def decode_token(
    token: str,
    token_type: TokenType,
    verify_exp: bool = True
) -> dict[str, Any]:
    """
    Decode and verify a JWT token.
    Returns the decoded payload as a dict.
    """
    try:
        secret = (
            settings.JWT_SECRET_KEY 
            if token_type == TokenType.ACCESS 
            else settings.JWT_REFRESH_SECRET_KEY
        )
        
        payload = jwt.decode(
            token,
            secret,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": verify_exp}
        )
        
        if payload.get("type") != token_type.value:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )