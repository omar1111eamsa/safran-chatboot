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
from .llm_service import OllamaService

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
    Chat endpoint with Ollama LLM + RAG hybrid approach.
    
    Flow:
    1. Check if it's a greeting or conversational question → Ollama alone
    2. Search RAG knowledge base for relevant answer (threshold 0.75)
    3. If relevant (similarity ≥ 0.75), use Ollama with RAG context
    4. If not relevant, use Ollama alone for general conversation
    """
    from .llm_service import is_greeting, is_conversational
    
    logger.info(
        f"Chat request from {current_user.username} "
        f"({current_user.employee_type}): {request.message}"
    )
    
    # Initialize Ollama service
    ollama = OllamaService()
    
    # Step 1: Check if it's a greeting or conversational question
    if is_greeting(request.message) or is_conversational(request.message):
        logger.info("Detected greeting/conversational - using Ollama alone")
        response = ollama.generate_response(
            question=request.message,
            context=None,
            profile=current_user.employee_type
        )
        
        return ChatResponse(
            question=request.message,
            answer=response,
            profile=current_user.employee_type,
            domain=None  # No domain for greetings
        )
    
    # Step 2: Search RAG knowledge base with adjusted threshold for better variation detection
    rag_answer, domain, similarity, profile_allowed = rag_engine.search_knowledge(
        question=request.message,
        employee_type=current_user.employee_type,
        threshold=0.65  # Adjusted from 0.75 to better detect question variations
    )
    
    # Check for profile mismatch
    if not profile_allowed:
        logger.warning(f"Access denied for user {current_user.username} (profile: {current_user.employee_type})")
        return ChatResponse(
            question=request.message,
            answer="Désolé, cette information n'est pas disponible pour votre profil. Pour plus d'informations, veuillez contacter le service RH.",
            profile=current_user.employee_type,
            domain=None
        )
    
    # Step 3: Generate response
    if rag_answer and similarity >= 0.65:
        # RAG found relevant answer - return it directly with minimal formatting
        # This preserves the exact facts from the knowledge base
        logger.info(f"Using RAG answer directly (similarity: {similarity:.3f})")
        
        # Add minimal polite formatting without changing facts
        formatted_answer = f"Pour répondre à votre question : {rag_answer}"
        
        return ChatResponse(
            question=request.message,
            answer=formatted_answer,
            profile=current_user.employee_type,
            domain=domain
        )
    else:
        # No RAG answer or low similarity - use Ollama for general response
        logger.info("No RAG match - using Ollama for general response")
        response = ollama.generate_response(
            question=request.message,
            context=None,
            profile=current_user.employee_type
        )
        domain = None
    
    return ChatResponse(
        question=request.message,
        answer=response,
        profile=current_user.employee_type,
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
