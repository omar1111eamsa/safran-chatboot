"""
Pydantic models for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional


class LoginRequest(BaseModel):
    """Login request payload."""
    username: str = Field(..., min_length=1, description="LDAP username")
    password: str = Field(..., min_length=1, description="User password")


class TokenResponse(BaseModel):
    """Token response after successful authentication."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Refresh token request payload."""
    refresh_token: str = Field(..., description="Refresh token")


class ChatRequest(BaseModel):
    """Chat message request."""
    message: str = Field(..., min_length=1, max_length=500, description="User question")


class ChatResponse(BaseModel):
    """Chat response from RAG engine."""
    question: str
    answer: str
    profile: str
    domain: Optional[str] = None


class UserProfile(BaseModel):
    """User profile from LDAP."""
    username: str
    full_name: str
    email: str
    employee_type: str  # CDI, CDD, Intérim, Stagiaire
    title: str  # Cadre, Non-Cadre
    department: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    environment: str
