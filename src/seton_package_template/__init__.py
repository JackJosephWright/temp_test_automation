"""
Seton Package Template

A comprehensive template for creating Python packages that integrate with the Seton ecosystem.
This package provides standard patterns for database connections, Google Sheets integration,
configuration management, and Airflow compatibility.

Key Features:
- Oracle database integration with proper column naming handling
- Google Sheets integration using seton_utils
- Environment-aware configuration system
- Airflow-compatible main entry points
- Comprehensive logging setup
- Security and safety patterns

Critical Note: Oracle returns ALL column names in UPPERCASE!
Always use uppercase keys when accessing Oracle query results.

Example:
    >>> from seton_package_template import main
    >>> main.run()
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Import main components for easy access
from .main import main, run_package
from .config.settings import get_environment, get_sheet_id

# Expose key functions at package level
__all__ = [
    "main",
    "run_package", 
    "get_environment",
    "get_sheet_id",
]
