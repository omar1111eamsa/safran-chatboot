"""
FastAPI main application.
HR Chatbot API with LDAP authentication and RAG-powered Q&A.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .models import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    ChatRequest,
    ChatResponse,
    UserProfile,
    HealthResponse
)
from .auth import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    get_current_user
)
from .ldap_service import ldap_service
from .rag import rag_engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting HR Chatbot API...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"LDAP Server: {settings.ldap_server_uri}")
    
    # Initialize RAG engine
    try:
        rag_engine.load()
        logger.info("RAG engine initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RAG engine: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down HR Chatbot API...")


# Create FastAPI app
app = FastAPI(
    title="HR Chatbot API",
    description="API for HR Chatbot with LDAP authentication and RAG-powered Q&A",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ================================
# Health Check Endpoint
# ================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        environment=settings.environment
    )


# ================================
# Authentication Endpoints
# ================================

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Authenticate user with LDAP and return JWT tokens.
    
    Args:
        request: Login credentials
        
    Returns:
        Access and refresh tokens
        
    Raises:
        HTTPException: If authentication fails
    """
    # Authenticate against LDAP
    if not ldap_service.authenticate_user(request.username, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    token_data = {"sub": request.username}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    logger.info(f"User {request.username} logged in successfully")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@app.post("/api/auth/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token.
    
    Args:
        request: Refresh token
        
    Returns:
        New access and refresh tokens
        
    Raises:
        HTTPException: If refresh token is invalid
    """
    payload = verify_refresh_token(request.refresh_token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de rafraîchissement invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de rafraîchissement invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create new tokens
    token_data = {"sub": username}
    access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token(token_data)
    
    logger.info(f"Tokens refreshed for user {username}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token
    )


# ================================
# User Profile Endpoint
# ================================

@app.get("/api/profile", response_model=UserProfile)
async def get_profile(current_user: UserProfile = Depends(get_current_user)):
    """
    Get current user profile.
    
    Args:
        current_user: Authenticated user from JWT token
        
    Returns:
        User profile information
    """
    return current_user


# ================================
# Chat Endpoint
# ================================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Process user question and return answer from RAG engine.
    
    Args:
        request: User question
        current_user: Authenticated user from JWT token
        
    Returns:
        Answer from knowledge base
    """
    logger.info(
        f"Chat request from {current_user.username} "
        f"({current_user.employee_type}/{current_user.title}): {request.message}"
    )
    
    # Get answer from RAG engine
    answer, domain = rag_engine.get_answer(
        question=request.message,
        employee_type=current_user.employee_type,
        title=current_user.title
    )
    
    return ChatResponse(
        question=request.message,
        answer=answer,
        profile=f"{current_user.employee_type}/{current_user.title}",
        domain=domain
    )


# ================================
# Root Endpoint
# ================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "HR Chatbot API",
        "version": "1.0.0",
        "docs": "/docs"
    }
