"""
Configuration management using Pydantic Settings.
All configuration is loaded from environment variables.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # LDAP Configuration
    # LDAP server hostname (use service name in Docker Compose, or IP/hostname in production)
    ldap_host: str = "ldap-service"
    ldap_port: int = 389
    ldap_base_dn: str = "dc=serini,dc=local"
    ldap_admin_dn: str = "cn=admin,dc=serini,dc=local"
    # WARNING: Change this password in production environments
    ldap_admin_password: str = "SecureAdminPass123!"
    
    # JWT Configuration
    # SECURITY: Generate secure random keys for production using: openssl rand -hex 32
    jwt_secret_key: str = "change-this-to-a-secure-random-secret-key-in-production"
    jwt_refresh_secret_key: str = "change-this-to-another-secure-random-secret-key-in-production"
    jwt_algorithm: str = "HS256"
    # Access tokens expire after 60 minutes for security
    access_token_expire_minutes: int = 60
    # Refresh tokens expire after 7 days, allowing users to stay logged in
    refresh_token_expire_days: int = 7
    
    # CORS Configuration
    # Comma-separated list of allowed origins for CORS (update for production deployment)
    cors_origins: str = Field(default="http://localhost:5173")
    
    # Ollama LLM Configuration
    # Base URL for Ollama service (use service name in Docker Compose)
    ollama_base_url: str = Field(default="http://ollama:11434")
    # LLM model to use (llama3.2:3b provides good balance of speed and quality)
    ollama_model: str = Field(default="llama3.2:3b")
    
    # Environment
    # Current environment: development, staging, or production
    environment: str = Field(default="development")
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def ldap_server_uri(self) -> str:
        """Construct LDAP server URI."""
        return f"ldap://{self.ldap_host}:{self.ldap_port}"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
