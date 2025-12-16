"""
JWT authentication and authorization.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .config import settings
from .models import UserProfile
from .ldap_service import ldap_service

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()


def create_access_token(data: dict) -> str:
    """
    Create JWT access token.
    
    Args:
        data: Payload data to encode in token
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire, "type": "access"})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Create JWT refresh token.
    
    Args:
        data: Payload data to encode in token
        
    Returns:
        Encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_refresh_secret_key,
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def verify_access_token(token: str) -> Optional[Dict]:
    """
    Verify and decode access token.
    
    Args:
        token: JWT token to verify
        
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        
        if payload.get("type") != "access":
            return None
            
        return payload
        
    except JWTError as e:
        logger.warning(f"Token verification failed: {str(e)}")
        return None


def verify_refresh_token(token: str) -> Optional[Dict]:
    """
    Verify and decode refresh token.
    
    Args:
        token: JWT refresh token to verify
        
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_refresh_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        
        if payload.get("type") != "refresh":
            return None
            
        return payload
        
    except JWTError as e:
        logger.warning(f"Refresh token verification failed: {str(e)}")
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserProfile:
    """
    Dependency to get current authenticated user from JWT token.
    Also retrieves user profile from LDAP.
    
    Args:
        credentials: HTTP Authorization credentials
        
    Returns:
        UserProfile object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = verify_access_token(token)
    
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    # Retrieve user profile from LDAP
    profile_data = ldap_service.get_user_profile(username)
    if profile_data is None:
        raise credentials_exception
    
    return UserProfile(**profile_data)
