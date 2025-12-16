"""
Configuration management using Pydantic Settings.
All configuration is loaded from environment variables.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # LDAP Configuration
    ldap_host: str = "ldap-service"
    ldap_port: int = 389
    ldap_base_dn: str = "dc=serini,dc=local"
    ldap_admin_dn: str = "cn=admin,dc=serini,dc=local"
    ldap_admin_password: str = "SecureAdminPass123!"
    
    # JWT Configuration
    jwt_secret_key: str = "change-this-to-a-secure-random-secret-key-in-production"
    jwt_refresh_secret_key: str = "change-this-to-another-secure-random-secret-key-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7
    
    # CORS Configuration
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    
    # Environment
    environment: str = "development"
    
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
