"""Application settings and configuration management."""

from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Google Cloud
    gcp_project_id: str = "your-project-id"
    google_api_key: str = ""
    google_adk_model: str = "gemini-2.0-flash-exp"
    google_application_credentials: str = "./config/gcp-credentials.json"
    gcs_bucket_name: str = "loanai-customer-documents-dev"

    # ADK Configuration
    adk_model: str = "gemini-2.0-flash-exp"
    adk_temperature: float = 0.1
    adk_max_tokens: int = 4096
    adk_top_p: float = 0.9

    # API Keys
    brave_search_api_key: str = ""
    clearbit_api_key: str = ""

    # Application
    environment: str = "development"
    debug: bool = True
    log_level: str = "DEBUG"

    # Feature Flags
    enable_document_ai: bool = True
    enable_mcp_verification: bool = True
    enable_consensus_building: bool = True

    # Processing
    max_agent_discussion_rounds: int = 3
    consensus_threshold: float = 0.6
    timeout_seconds: int = 300

    # Database
    database_url: Optional[str] = None
    db_host: Optional[str] = None
    db_port: Optional[int] = None
    db_user: Optional[str] = None
    db_password: Optional[str] = None
    db_name: Optional[str] = None

    class Config:
        """Pydantic config."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Allow extra fields in .env file


# Global settings instance
settings = Settings()
