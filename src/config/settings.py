"""
Configuration Management using Pydantic Settings.
Handles environment-specific settings with type validation.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    """Application settings with type validation and defaults."""
    
    # LLM Configuration
    groq_api_key: str = Field(..., description="Groq API key for LLM access")
    groq_model: str = Field(
        default="llama-3.3-70b-versatile",
        description="Groq model to use"
    )
    
    # Environment
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Current environment"
    )
    debug: bool = Field(default=False, description="Debug mode")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: str = Field(default="logs/app.log", description="Log file path")
    
    # Error Handling
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum retry attempts for failed operations"
    )
    timeout_seconds: float = Field(
        default=30.0,
        gt=0,
        description="Timeout for LLM API calls in seconds"
    )
    
    # Mock Data (for development/demo)
    use_mock_data: bool = Field(
        default=False,
        description="Use mock data instead of real LLM calls"
    )
    mock_server_url: str = Field(
        default="http://localhost:8001",
        description="URL of mock data server"
    )
    
    # Model configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields in .env
    )
    
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"


# Singleton instance of setting class
settings = Settings()


# For testing/debugging
if __name__ == "__main__":
    print("Configuration loaded successfully!")
    print(f"Environment: {settings.environment}")
    print(f"Debug: {settings.debug}")
    print(f"Log Level: {settings.log_level}")
    print(f"Max Retries: {settings.max_retries}")
    print(f"Timeout: {settings.timeout_seconds}s")
    print(f"Groq Model: {settings.groq_model}")
    print(f"Is Production: {settings.is_production}")