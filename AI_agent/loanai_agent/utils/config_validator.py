"""Configuration validation for fail-fast startup."""

import os
from typing import Dict, List, Optional

from pydantic import ValidationError

from config.settings import settings
from loanai_agent.utils import ConfigurationException, get_logger

logger = get_logger(__name__)


class ConfigurationValidator:
    """Validates all application configuration at startup."""

    def __init__(self):
        """Initialize configuration validator."""
        self.validation_errors: List[str] = []
        self.validation_warnings: List[str] = []

    def validate_all(self, fail_fast: bool = True) -> bool:
        """Validate all configuration settings.
        
        Args:
            fail_fast: If True, raise exception on first error
            
        Returns:
            True if all validations pass
            
        Raises:
            ConfigurationException: If validation fails and fail_fast=True
        """
        logger.info("Starting configuration validation...")
        
        # Run all validation checks
        self._validate_google_api()
        self._validate_gcp_settings()
        self._validate_database_settings()
        self._validate_file_paths()
        self._validate_model_settings()
        self._validate_environment()
        
        # Report results
        self._report_results()
        
        if self.validation_errors:
            error_msg = f"Configuration validation failed with {len(self.validation_errors)} error(s)"
            if fail_fast:
                raise ConfigurationException(error_msg)
            return False
        
        logger.info("✓ Configuration validation passed")
        return True

    def _validate_google_api(self) -> None:
        """Validate Google API configuration."""
        logger.debug("Validating Google API configuration...")
        
        if not settings.google_api_key:
            self.validation_errors.append(
                "GOOGLE_API_KEY is not set. LLM features will not work."
            )
        elif len(settings.google_api_key) < 20:
            self.validation_errors.append(
                "GOOGLE_API_KEY appears to be invalid (too short)"
            )
        else:
            logger.debug("✓ Google API key is configured")

    def _validate_gcp_settings(self) -> None:
        """Validate Google Cloud Platform settings."""
        logger.debug("Validating GCP settings...")
        
        # Check GCP Project ID
        if not settings.gcp_project_id:
            self.validation_warnings.append(
                "GCP_PROJECT_ID is not set. GCS features may not work."
            )
        else:
            logger.debug(f"✓ GCP Project ID: {settings.gcp_project_id}")
        
        # Check GCS Bucket
        if not settings.gcs_bucket_name:
            self.validation_warnings.append(
                "GCS_BUCKET_NAME is not set. Document storage will not work."
            )
        else:
            logger.debug(f"✓ GCS Bucket: {settings.gcs_bucket_name}")
        
        # Check credentials file
        creds_path = settings.google_application_credentials
        if not creds_path:
            self.validation_errors.append(
                "GOOGLE_APPLICATION_CREDENTIALS is not set"
            )
        else:
            # Make path absolute if relative
            if not os.path.isabs(creds_path):
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                creds_path = os.path.join(base_dir, creds_path)
            
            if not os.path.exists(creds_path):
                self.validation_errors.append(
                    f"GCP credentials file not found: {creds_path}"
                )
            else:
                logger.debug(f"✓ GCP credentials file found: {creds_path}")

    def _validate_database_settings(self) -> None:
        """Validate database configuration."""
        logger.debug("Validating database settings...")
        
        # Database settings from config
        db_host = getattr(settings, 'db_host', None)
        db_port = getattr(settings, 'db_port', None)
        db_name = getattr(settings, 'db_name', None)
        db_user = getattr(settings, 'db_user', None)
        db_password = getattr(settings, 'db_password', None)
        
        missing_db_settings = []
        if not db_host:
            missing_db_settings.append("DB_HOST")
        if not db_port:
            missing_db_settings.append("DB_PORT")
        if not db_name:
            missing_db_settings.append("DB_NAME")
        if not db_user:
            missing_db_settings.append("DB_USER")
        if not db_password:
            missing_db_settings.append("DB_PASSWORD")
        
        if missing_db_settings:
            self.validation_warnings.append(
                f"Database settings not fully configured: {', '.join(missing_db_settings)}"
            )
        else:
            logger.debug(f"✓ Database configured: {db_host}:{db_port}/{db_name}")

    def _validate_file_paths(self) -> None:
        """Validate critical file paths."""
        logger.debug("Validating file paths...")
        
        # Check if logs directory exists or can be created
        logs_dir = "logs"
        if not os.path.exists(logs_dir):
            try:
                os.makedirs(logs_dir)
                logger.debug(f"✓ Created logs directory: {logs_dir}")
            except Exception as e:
                self.validation_warnings.append(
                    f"Cannot create logs directory: {e}"
                )
        else:
            logger.debug(f"✓ Logs directory exists: {logs_dir}")

    def _validate_model_settings(self) -> None:
        """Validate model and agent configuration."""
        logger.debug("Validating model settings...")
        
        # Check model settings
        model_name = getattr(settings, 'default_model', 'gemini-2.0-flash-exp')
        logger.debug(f"✓ Default model: {model_name}")
        
        # Check temperature settings
        temperature = getattr(settings, 'model_temperature', 0.1)
        if not 0.0 <= temperature <= 2.0:
            self.validation_warnings.append(
                f"Model temperature {temperature} is outside recommended range (0.0-2.0)"
            )
        else:
            logger.debug(f"✓ Model temperature: {temperature}")

    def _validate_environment(self) -> None:
        """Validate environment settings."""
        logger.debug("Validating environment...")
        
        # Check environment
        env = getattr(settings, 'environment', 'development')
        valid_envs = ['development', 'staging', 'production']
        
        if env not in valid_envs:
            self.validation_warnings.append(
                f"Environment '{env}' not in {valid_envs}"
            )
        else:
            logger.debug(f"✓ Environment: {env}")
        
        # Production-specific checks
        if env == 'production':
            if settings.google_api_key and 'demo' in settings.google_api_key.lower():
                self.validation_errors.append(
                    "Using demo API key in production environment"
                )
            
            if getattr(settings, 'debug', False):
                self.validation_warnings.append(
                    "Debug mode is enabled in production"
                )

    def _report_results(self) -> None:
        """Report validation results."""
        if self.validation_errors:
            logger.error("=" * 60)
            logger.error(f"Configuration Validation Errors ({len(self.validation_errors)}):")
            logger.error("=" * 60)
            for i, error in enumerate(self.validation_errors, 1):
                logger.error(f"  {i}. ❌ {error}")
            logger.error("=" * 60)
        
        if self.validation_warnings:
            logger.warning("=" * 60)
            logger.warning(f"Configuration Warnings ({len(self.validation_warnings)}):")
            logger.warning("=" * 60)
            for i, warning in enumerate(self.validation_warnings, 1):
                logger.warning(f"  {i}. ⚠️  {warning}")
            logger.warning("=" * 60)

    def get_validation_report(self) -> Dict[str, any]:
        """Get detailed validation report.
        
        Returns:
            Dictionary with validation results
        """
        return {
            "passed": len(self.validation_errors) == 0,
            "errors": self.validation_errors,
            "warnings": self.validation_warnings,
            "error_count": len(self.validation_errors),
            "warning_count": len(self.validation_warnings),
        }


def validate_configuration(fail_fast: bool = True) -> bool:
    """Convenience function to validate configuration.
    
    Args:
        fail_fast: If True, raise exception on first error
        
    Returns:
        True if validation passes
        
    Raises:
        ConfigurationException: If validation fails and fail_fast=True
    """
    validator = ConfigurationValidator()
    return validator.validate_all(fail_fast=fail_fast)


def get_validation_report() -> Dict[str, any]:
    """Get validation report without raising exceptions.
    
    Returns:
        Dictionary with validation results
    """
    validator = ConfigurationValidator()
    validator.validate_all(fail_fast=False)
    return validator.get_validation_report()
