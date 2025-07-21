"""
Logging configuration for Seton packages

This module provides a standardized logging configuration that works in both
Airflow tasks and standalone execution. It provides:

1. Environment-aware logging setup
2. Structured logging with consistent formats
3. Performance logging utilities
4. Simple get_logger(__name__) interface
5. No complex file path management

Key Features:
- Works seamlessly in Airflow and local development
- Structured logging with contextual information
- Performance timing utilities
- Configurable log levels and formats
- No file management complexity

Usage:
    from seton_package_template.config.logging_config import get_logger
    
    logger = get_logger(__name__)
    logger.info("Processing started")
"""

import logging
import logging.config
import sys
import time
from typing import Optional, Dict, Any
from contextlib import contextmanager

from .settings import get_log_level, get_log_format, is_airflow_environment


class SetonFormatter(logging.Formatter):
    """
    Custom formatter for Seton packages with enhanced information
    """
    
    def format(self, record):
        # Add execution context
        record.context = "airflow" if is_airflow_environment() else "local"
        
        # Add module context
        if hasattr(record, 'name'):
            # Extract meaningful module name from full path
            name_parts = record.name.split('.')
            if len(name_parts) > 2:
                record.module_context = f"{name_parts[-2]}.{name_parts[-1]}"
            else:
                record.module_context = record.name
        else:
            record.module_context = "unknown"
        
        return super().format(record)


def get_logging_config(log_level: str = "INFO", log_format: str = "detailed") -> Dict[str, Any]:
    """
    Get logging configuration dictionary
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Format style ('simple', 'detailed', 'structured')
        
    Returns:
        Dict[str, Any]: Logging configuration dictionary
    """
    
    # Define format strings
    formats = {
        "simple": "%(levelname)s - %(message)s",
        "detailed": "%(asctime)s | %(context)s | %(module_context)s | %(levelname)s | %(message)s",
        "structured": "%(asctime)s | %(context)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s"
    }
    
    format_string = formats.get(log_format, formats["detailed"])
    
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "seton_formatter": {
                "()": SetonFormatter,
                "format": format_string,
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "seton_formatter",
                "stream": "ext://sys.stdout"
            }
        },
        "loggers": {
            "seton_package_template": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False
            },
            # Allow other loggers to work normally
            "": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": True
            }
        }
    }
    
    # In Airflow, we might want to adjust the configuration
    if is_airflow_environment():
        # Airflow has its own logging setup, so we integrate with it
        config["handlers"]["console"]["class"] = "logging.StreamHandler"
        config["handlers"]["console"]["stream"] = "ext://sys.stdout"
    
    return config


def setup_logging(log_level: Optional[str] = None, log_format: Optional[str] = None) -> None:
    """
    Set up logging configuration for the application
    
    Args:
        log_level: Override log level (uses settings default if None)
        log_format: Override log format (uses settings default if None)
    """
    # Get configuration from settings if not provided
    if log_level is None:
        log_level = get_log_level()
    if log_format is None:
        log_format = get_log_format()
    
    # Get and apply logging configuration
    config = get_logging_config(log_level, log_format)
    logging.config.dictConfig(config)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with proper configuration
    
    This is the main function used throughout Seton packages to get loggers.
    It ensures consistent logging setup across all modules.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        logging.Logger: Configured logger instance
        
    Example:
        logger = get_logger(__name__)
        logger.info("This is a log message")
    """
    # Ensure logging is set up
    if not logging.getLogger().handlers:
        setup_logging()
    
    return logging.getLogger(name)


@contextmanager
def log_performance(logger: logging.Logger, operation_name: str, 
                   log_level: int = logging.INFO):
    """
    Context manager for logging operation performance
    
    Args:
        logger: Logger instance to use
        operation_name: Name of the operation being timed
        log_level: Log level for performance messages
        
    Example:
        with log_performance(logger, "database_query"):
            results = execute_query()
    """
    start_time = time.time()
    logger.log(log_level, f"🚀 Starting {operation_name}")
    
    try:
        yield
        end_time = time.time()
        duration = end_time - start_time
        logger.log(log_level, f"✅ Completed {operation_name} in {duration:.2f} seconds")
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        logger.log(logging.ERROR, f"❌ Failed {operation_name} after {duration:.2f} seconds: {e}")
        raise


class LoggerMixin:
    """
    Mixin class to add logging capabilities to any class
    
    Example:
        class MyClass(LoggerMixin):
            def process_data(self):
                self.logger.info("Processing data")
                
        obj = MyClass()
        obj.process_data()
    """
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class"""
        return get_logger(f"{self.__class__.__module__}.{self.__class__.__name__}")


def log_function_call(func):
    """
    Decorator to log function calls with parameters and execution time
    
    Example:
        @log_function_call
        def my_function(param1, param2):
            return param1 + param2
    """
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        func_name = f"{func.__module__}.{func.__name__}"
        
        # Log function call
        logger.debug(f"📞 Calling {func_name} with args={args}, kwargs={kwargs}")
        
        with log_performance(logger, func_name, logging.DEBUG):
            result = func(*args, **kwargs)
        
        logger.debug(f"📤 {func_name} returned: {type(result).__name__}")
        return result
    
    return wrapper


def configure_third_party_loggers():
    """
    Configure third-party loggers to reduce noise
    
    This function sets appropriate log levels for common third-party
    libraries to reduce log noise while maintaining important information.
    """
    # Reduce Google API client logging
    logging.getLogger('googleapiclient.discovery').setLevel(logging.WARNING)
    logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
    logging.getLogger('google.auth').setLevel(logging.WARNING)
    
    # Reduce urllib3 logging
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
    
    # Reduce requests logging
    logging.getLogger('requests.packages.urllib3').setLevel(logging.WARNING)
    
    # Oracle client logging
    logging.getLogger('cx_Oracle').setLevel(logging.WARNING)


# Set up third-party logger configuration when module is imported
configure_third_party_loggers()
