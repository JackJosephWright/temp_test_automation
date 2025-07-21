"""
Settings and configuration management for Seton packages

This module provides a sophisticated configuration system that automatically
adapts between Airflow and local development environments. It handles:

1. Environment detection (Airflow vs local)
2. Variable source selection (Airflow Variables vs environment variables)
3. Google Sheet ID selection based on environment
4. Environment validation and safety checks
5. Production sheet protection

Key Patterns:
- Uses Airflow Variable.get() when running in Airflow
- Falls back to os.getenv() for local development
- Provides environment-based sheet selection
- Validates environment/sheet combinations for safety

Critical Safety Feature:
Prevents non-production environments from accessing production Google Sheets
"""

import os
from typing import Optional, Dict, Any
import warnings

try:
    # Try to import Airflow Variable - will fail in local development
    from airflow.models import Variable
    AIRFLOW_AVAILABLE = True
except ImportError:
    AIRFLOW_AVAILABLE = False
    Variable = None

# Load environment variables from .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, continue without it


class EnvironmentError(Exception):
    """Custom exception for environment-related errors"""
    pass


def is_airflow_environment() -> bool:
    """
    Detect if we're running in an Airflow environment
    
    Returns:
        bool: True if running in Airflow, False otherwise
    """
    # Check for Airflow-specific environment variables
    airflow_indicators = [
        'AIRFLOW_HOME',
        'AIRFLOW__CORE__DAGS_FOLDER', 
        'AIRFLOW__CORE__SQL_ALCHEMY_CONN'
    ]
    
    for indicator in airflow_indicators:
        if os.getenv(indicator):
            return True
    
    # Check if Airflow Variable is available and accessible
    if AIRFLOW_AVAILABLE:
        try:
            # Try to access Airflow Variable - this will fail outside Airflow
            Variable.get("test_key", default_var=None)
            return True
        except Exception:
            return False
    
    return False


def get_variable(key: str, default: Optional[str] = None, raise_if_missing: bool = False) -> Optional[str]:
    """
    Get a configuration variable from Airflow or environment
    
    This function implements the core pattern for Seton packages:
    - Use Airflow Variable.get() when in Airflow
    - Use os.getenv() when in local development
    
    Args:
        key: Variable name to retrieve
        default: Default value if variable not found
        raise_if_missing: Whether to raise exception if variable missing
        
    Returns:
        Variable value or default
        
    Raises:
        EnvironmentError: If variable missing and raise_if_missing=True
        
    Example:
        # Get sheet ID - automatically chooses source
        sheet_id = get_variable("GOOGLE_SHEET_ID_PROD")
        
        # With default value
        log_level = get_variable("LOG_LEVEL", "INFO")
    """
    value = None
    
    if is_airflow_environment() and AIRFLOW_AVAILABLE:
        # Running in Airflow - use Variable.get()
        try:
            value = Variable.get(key, default_var=default)
        except Exception as e:
            if raise_if_missing and default is None:
                raise EnvironmentError(f"Airflow variable '{key}' not found: {e}")
            value = default
    else:
        # Local development - use environment variables
        value = os.getenv(key, default)
    
    if value is None and raise_if_missing:
        env_type = "Airflow" if is_airflow_environment() else "environment"
        raise EnvironmentError(f"Required {env_type} variable '{key}' not found")
    
    return value


def get_environment() -> str:
    """
    Get the current environment (development, testing, production)
    
    Returns:
        str: Environment name
        
    Example:
        env = get_environment()
        if env == "production":
            # Use production settings
    """
    env = get_variable("ENVIRONMENT", "development")
    
    # Validate environment value
    valid_environments = ["development", "testing", "production"]
    if env not in valid_environments:
        warnings.warn(f"Unknown environment '{env}', defaulting to 'development'")
        env = "development"
    
    return env


def get_sheet_id() -> str:
    """
    Get Google Sheet ID based on current environment
    
    This function automatically selects the appropriate sheet ID:
    - development -> GOOGLE_SHEET_ID_DEV
    - testing -> GOOGLE_SHEET_ID_TEST  
    - production -> GOOGLE_SHEET_ID_PROD
    
    Returns:
        str: Google Sheet ID for current environment
        
    Raises:
        EnvironmentError: If sheet ID not configured for environment
        
    Example:
        sheet_id = get_sheet_id()  # Automatically selects correct sheet
    """
    environment = get_environment()
    
    # Map environment to sheet ID variable name
    sheet_id_map = {
        "development": "GOOGLE_SHEET_ID_DEV",
        "testing": "GOOGLE_SHEET_ID_TEST",
        "production": "GOOGLE_SHEET_ID_PROD"
    }
    
    sheet_var = sheet_id_map.get(environment)
    if not sheet_var:
        raise EnvironmentError(f"No sheet ID mapping for environment: {environment}")
    
    sheet_id = get_variable(sheet_var, raise_if_missing=True)
    return sheet_id


def get_production_sheet_id() -> Optional[str]:
    """
    Get the production Google Sheet ID for safety validation
    
    Returns:
        Optional[str]: Production sheet ID or None if not configured
    """
    return get_variable("GOOGLE_SHEET_ID_PROD")


def validate_environment_sheet_access() -> None:
    """
    Validate that non-production environments don't access production sheets
    
    This is a critical safety feature that prevents accidental data corruption
    in production Google Sheets when running in development/testing environments.
    
    Raises:
        EnvironmentError: If non-production environment tries to access production sheet
        
    Example:
        validate_environment_sheet_access()  # Call before sheet operations
    """
    environment = get_environment()
    current_sheet_id = get_sheet_id()
    production_sheet_id = get_production_sheet_id()
    
    # Skip validation if production sheet ID not configured
    if not production_sheet_id:
        return
    
    # Check if non-production environment is targeting production sheet
    if environment != "production" and current_sheet_id == production_sheet_id:
        raise EnvironmentError(
            f"🚨 CRITICAL SAFETY ERROR 🚨\n"
            f"Environment '{environment}' is attempting to access PRODUCTION Google Sheet!\n"
            f"Current sheet ID: {current_sheet_id}\n"
            f"Production sheet ID: {production_sheet_id}\n"
            f"This could result in production data corruption.\n"
            f"Please check your environment configuration."
        )


def validate_environment() -> None:
    """
    Perform comprehensive environment validation
    
    This function validates:
    1. Required environment variables are set
    2. Environment/sheet access safety
    3. Configuration consistency
    
    Raises:
        EnvironmentError: If validation fails
        
    Example:
        validate_environment()  # Call at start of main function
    """
    environment = get_environment()
    
    # Validate sheet ID is configured
    try:
        sheet_id = get_sheet_id()
    except EnvironmentError as e:
        raise EnvironmentError(f"Sheet ID validation failed: {e}")
    
    # Validate environment/sheet access safety
    validate_environment_sheet_access()
    
    # Validate Google credentials configuration
    creds_path = get_variable("GOOGLE_CREDENTIALS_PATH")
    creds_json = get_variable("GOOGLE_CREDENTIALS_JSON")
    
    if not creds_path and not creds_json:
        raise EnvironmentError(
            "Google credentials not configured. Set either:\n"
            "- GOOGLE_CREDENTIALS_PATH (path to service account JSON)\n"
            "- GOOGLE_CREDENTIALS_JSON (JSON string of credentials)"
        )
    
    # Log validation success
    print(f"✅ Environment validation passed")
    print(f"   Environment: {environment}")
    print(f"   Sheet ID: {sheet_id}")
    print(f"   Execution context: {'Airflow' if is_airflow_environment() else 'Local'}")


def get_all_settings() -> Dict[str, Any]:
    """
    Get all current settings for debugging and logging
    
    Returns:
        Dict[str, Any]: Dictionary of all current settings
        
    Note:
        Sensitive values like credentials are redacted for security
        
    Example:
        settings = get_all_settings()
        logger.info(f"Current settings: {settings}")
    """
    settings = {
        "environment": get_environment(),
        "sheet_id": get_sheet_id(),
        "is_airflow": is_airflow_environment(),
        "airflow_available": AIRFLOW_AVAILABLE,
    }
    
    # Add non-sensitive environment variables
    safe_vars = [
        "LOG_LEVEL",
        "LOG_FORMAT", 
        "ENVIRONMENT",
        "GOOGLE_SHEET_ID_DEV",
        "GOOGLE_SHEET_ID_TEST",
        "GOOGLE_SHEET_ID_PROD"
    ]
    
    for var in safe_vars:
        value = get_variable(var)
        if value:
            settings[var.lower()] = value
    
    # Redact sensitive variables
    sensitive_vars = [
        "GOOGLE_CREDENTIALS_PATH",
        "GOOGLE_CREDENTIALS_JSON", 
        "GITHUB_PAT"
    ]
    
    for var in sensitive_vars:
        value = get_variable(var)
        if value:
            settings[var.lower()] = "***REDACTED***"
    
    return settings


# Convenience functions for common settings
def get_log_level() -> str:
    """Get logging level (INFO, DEBUG, etc.)"""
    return get_variable("LOG_LEVEL", "INFO")


def get_log_format() -> str:
    """Get logging format preference"""
    return get_variable("LOG_FORMAT", "detailed")


def get_google_credentials_path() -> Optional[str]:
    """Get path to Google service account credentials"""
    return get_variable("GOOGLE_CREDENTIALS_PATH")


def get_google_credentials_json() -> Optional[str]:
    """Get Google credentials as JSON string"""
    return get_variable("GOOGLE_CREDENTIALS_JSON")
