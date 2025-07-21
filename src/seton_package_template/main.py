"""
Main entry point for Seton package template

This module provides the main function that serves as the entry point for both
Airflow tasks and standalone execution. It demonstrates the standard patterns
used across Seton ecosystem packages.

Key Patterns Demonstrated:
1. Environment-aware configuration
2. Oracle database connection with proper column naming
3. Google Sheets integration
4. Comprehensive error handling and logging
5. Airflow compatibility

Usage:
    As Airflow task:
        from seton_package_template.main import main
        
    As standalone script:
        python -m seton_package_template.main
        
    Command line:
        seton-package-template
"""

import sys
from typing import Dict, List, Optional

from .config.logging_config import get_logger
from .config.settings import get_environment, get_sheet_id, validate_environment
from .database.queries import get_student_data, get_staff_data
from .google_sheets.sheets_manager import SheetsManager
from .utils.helpers import format_data_for_sheets, validate_data_integrity

# Initialize logger
logger = get_logger(__name__)


def run_package() -> bool:
    """
    Main package execution function
    
    This function demonstrates the standard Seton package workflow:
    1. Validate environment and configuration
    2. Connect to Oracle database
    3. Retrieve and process data
    4. Upload to Google Sheets
    5. Validate results
    
    Returns:
        bool: True if successful, False otherwise
        
    Raises:
        EnvironmentError: If environment validation fails
        DatabaseError: If database operations fail
        SheetsError: If Google Sheets operations fail
    """
    try:
        logger.info("🚀 Starting Seton package execution")
        
        # Step 1: Validate environment and configuration
        logger.info("📋 Validating environment configuration")
        validate_environment()
        environment = get_environment()
        sheet_id = get_sheet_id()
        
        logger.info(f"Environment: {environment}")
        logger.info(f"Target sheet ID: {sheet_id}")
        
        # Step 2: Initialize Google Sheets manager
        logger.info("📊 Initializing Google Sheets connection")
        sheets_manager = SheetsManager(sheet_id)
        
        # Step 3: Retrieve data from Oracle database
        logger.info("🗄️  Fetching student data from Oracle database")
        student_data = get_student_data()
        logger.info(f"Retrieved {len(student_data)} student records")
        
        logger.info("👥 Fetching staff data from Oracle database")
        staff_data = get_staff_data()
        logger.info(f"Retrieved {len(staff_data)} staff records")
        
        # Step 4: Validate data integrity
        logger.info("✅ Validating data integrity")
        if not validate_data_integrity(student_data, staff_data):
            logger.error("❌ Data integrity validation failed")
            return False
        
        # Step 5: Format data for Google Sheets
        logger.info("📝 Formatting data for Google Sheets")
        formatted_student_data = format_data_for_sheets(student_data)
        formatted_staff_data = format_data_for_sheets(staff_data)
        
        # Step 6: Upload to Google Sheets
        logger.info("📤 Uploading data to Google Sheets")
        
        # Update student data worksheet
        sheets_manager.update_worksheet(
            worksheet_name="Students",
            data=formatted_student_data,
            clear_existing=True
        )
        
        # Update staff data worksheet
        sheets_manager.update_worksheet(
            worksheet_name="Staff", 
            data=formatted_staff_data,
            clear_existing=True
        )
        
        # Step 7: Validate upload success
        logger.info("🔍 Validating upload success")
        upload_validation = sheets_manager.validate_upload(
            expected_students=len(student_data),
            expected_staff=len(staff_data)
        )
        
        if not upload_validation:
            logger.error("❌ Upload validation failed")
            return False
        
        logger.info("✅ Package execution completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Package execution failed: {str(e)}", exc_info=True)
        return False


def main(**kwargs) -> Optional[str]:
    """
    Main entry point compatible with both Airflow and standalone execution
    
    This function follows the standard pattern for Seton package main functions:
    - Accepts **kwargs for Airflow compatibility
    - Returns status string for Airflow task logging
    - Handles all exceptions gracefully
    - Provides detailed logging
    
    Args:
        **kwargs: Keyword arguments (used by Airflow for context)
        
    Returns:
        Optional[str]: Success message for Airflow, None for failure
        
    Example:
        # In Airflow DAG
        PythonOperator(
            task_id='run_seton_package',
            python_callable=main,
            dag=dag
        )
        
        # Standalone execution
        if __name__ == "__main__":
            result = main()
            sys.exit(0 if result else 1)
    """
    try:
        logger.info("🎯 Main function started")
        
        # Log execution context
        environment = get_environment()
        logger.info(f"Execution environment: {environment}")
        
        if kwargs:
            logger.info("📄 Airflow context detected")
            # Log relevant Airflow context if available
            task_instance = kwargs.get('task_instance')
            if task_instance:
                logger.info(f"Task ID: {task_instance.task_id}")
                logger.info(f"DAG ID: {task_instance.dag_id}")
                logger.info(f"Execution date: {task_instance.execution_date}")
        else:
            logger.info("🖥️  Standalone execution detected")
        
        # Execute main package logic
        success = run_package()
        
        if success:
            success_msg = "✅ Seton package execution completed successfully"
            logger.info(success_msg)
            return success_msg
        else:
            error_msg = "❌ Seton package execution failed"
            logger.error(error_msg)
            return None
            
    except Exception as e:
        error_msg = f"❌ Critical error in main function: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return None


if __name__ == "__main__":
    """
    Command-line execution entry point
    
    This allows the package to be run directly:
    python -m seton_package_template.main
    """
    print("🚀 Seton Package Template - Standalone Execution")
    
    result = main()
    if result:
        print(f"✅ Success: {result}")
        sys.exit(0)
    else:
        print("❌ Execution failed - check logs for details")
        sys.exit(1)
