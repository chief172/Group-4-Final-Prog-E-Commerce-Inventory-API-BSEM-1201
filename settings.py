"""
Application Settings and Configuration

This module centralizes all configuration settings including:
- Database configuration
- JWT authentication settings
- Environment-specific settings
- CORS and security settings
"""

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional, List
import os

# Load environment variables
load_dotenv()

# ============================================================================
# ENVIRONMENT VARIABLES (Raw access for compatibility)
# ============================================================================

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "")

# JWT Authentication
SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Application
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# Email (for async I/O demonstration)
USE_REAL_EMAIL = os.getenv("USE_REAL_EMAIL", "false").lower() == "true"
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# CORS Settings
CORS_ALLOWED_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:5500,http://127.0.0.1:5500"
).split(",")

# Rate Limiting (optional)
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", "60"))  # seconds

# ============================================================================
# PYDANTIC SETTINGS MODEL (Type-safe configuration)
# ============================================================================

class Settings(BaseModel):
    """
    Application settings with validation.
    Uses Pydantic for type checking and validation.
    """
    
    # Database
    database_url: str = Field(
        default=DATABASE_URL,
        description="PostgreSQL database URL (must use asyncpg driver)"
    )
    
    # JWT
    secret_key: str = Field(
        default=SECRET_KEY,
        min_length=32,
        description="Secret key for JWT signing (minimum 32 characters)"
    )
    algorithm: str = Field(
        default=ALGORITHM,
        description="JWT signing algorithm"
    )
    access_token_expire_minutes: int = Field(
        default=ACCESS_TOKEN_EXPIRE_MINUTES,
        gt=0,
        le=1440,
        description="Access token expiration in minutes"
    )
    
    # Application
    environment: str = Field(
        default=ENVIRONMENT,
        pattern="^(development|staging|production)$",
        description="Application environment"
    )
    debug: bool = Field(
        default=DEBUG,
        description="Debug mode flag"
    )
    
    # Email
    use_real_email: bool = Field(
        default=USE_REAL_EMAIL,
        description="Use real SMTP or simulate email sending"
    )
    smtp_host: str = Field(
        default=SMTP_HOST,
        description="SMTP server hostname"
    )
    smtp_port: int = Field(
        default=SMTP_PORT,
        description="SMTP server port"
    )
    smtp_user: str = Field(
        default=SMTP_USER,
        description="SMTP username"
    )
    smtp_password: str = Field(
        default=SMTP_PASSWORD,
        description="SMTP password"
    )
    
    # CORS
    cors_allowed_origins: List[str] = Field(
        default=CORS_ALLOWED_ORIGINS,
        description="Allowed CORS origins"
    )
    
    # Rate Limiting
    rate_limit_requests: int = Field(
        default=RATE_LIMIT_REQUESTS,
        description="Maximum requests per time period"
    )
    rate_limit_period: int = Field(
        default=RATE_LIMIT_PERIOD,
        description="Rate limiting time period in seconds"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment == "development"
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == "production"
    
    def validate_config(self) -> List[str]:
        """
        Validate configuration and return list of warnings/issues.
        
        Returns:
            List of warning messages (empty if all good)
        """
        warnings = []
        
        # Check secret key strength
        if len(self.secret_key) < 32:
            warnings.append(
                f"SECRET_KEY is only {len(self.secret_key)} characters long. "
                "Recommended: at least 32 characters."
            )
        
        # Check database URL has async driver
        if "asyncpg" not in self.database_url:
            warnings.append(
                "DATABASE_URL should use asyncpg driver. "
                "Use: postgresql+asyncpg://user:pass@localhost/dbname"
            )
        
        # Check email config in production
        if self.is_production() and self.use_real_email:
            if not self.smtp_user or not self.smtp_password:
                warnings.append(
                    "Email is enabled but SMTP credentials are missing. "
                    "Set SMTP_USER and SMTP_PASSWORD."
                )
        
        return warnings


# ============================================================================
# SETTINGS INSTANCE
# ============================================================================

def get_settings() -> Settings:
    """
    Get the application settings instance.
    
    Returns:
        Settings: Application settings object
        
    Example:
        settings = get_settings()
        print(settings.secret_key)
    """
    settings = Settings()
    
    # Validate and print warnings
    warnings = settings.validate_config()
    for warning in warnings:
        print(f"⚠️  CONFIG WARNING: {warning}")
    
    return settings


# Global settings instance
settings = get_settings()


# ============================================================================
# DEPENDENCY INJECTION FOR SETTINGS
# ============================================================================

async def get_settings_dependency() -> Settings:
    """
    Dependency injection for application settings.
    
    Usage:
        @router.get("/config")
        async def get_config(settings: Settings = Depends(get_settings_dependency)):
            return {"environment": settings.environment}
    """
    return settings


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def is_async_database_configured() -> bool:
    """Check if async database is properly configured."""
    return "asyncpg" in DATABASE_URL


def get_environment_display() -> str:
    """Get formatted environment name for display."""
    env_display = {
        "development": "🔧 Development",
        "staging": "🧪 Staging",
        "production": "🚀 Production"
    }
    return env_display.get(ENVIRONMENT, "❓ Unknown")


def print_config_summary() -> None:
    """Print a summary of the current configuration."""
    print("\n" + "=" * 60)
    print("📋 CONFIGURATION SUMMARY")
    print("=" * 60)
    print(f"Environment:           {get_environment_display()}")
    print(f"Debug Mode:            {'✅ On' if DEBUG else '❌ Off'}")
    print(f"Database Driver:       {'✅ asyncpg' if is_async_database_configured() else '❌ sync driver'}")
    print(f"JWT Algorithm:         {ALGORITHM}")
    print(f"Token Expiry:          {ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
    print(f"CORS Origins:          {len(CORS_ALLOWED_ORIGINS)} origins configured")
    print(f"Email:                 {'📧 Real SMTP' if USE_REAL_EMAIL else '📝 Simulated'}")
    print(f"Rate Limit:            {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_PERIOD}s")
    print("=" * 60 + "\n")