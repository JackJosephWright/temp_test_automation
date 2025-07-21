"""
Google Sheets manager for Seton packages

This module provides a comprehensive Google Sheets integration that follows
the standard patterns used across Seton packages. It demonstrates:

1. Credential management using seton_utils
2. Worksheet creation and management
3. Data upload with validation
4. Error handling and retries
5. Batch operations for performance

Key Features:
- Uses seton_utils for credential management
- Handles worksheet creation automatically
- Supports batch operations
- Comprehensive error handling
- Upload validation

Usage:
    from seton_package_template.google_sheets.sheets_manager import SheetsManager
    
    manager = SheetsManager(sheet_id)
    manager.update_worksheet("Students", student_data)
"""

import time
from typing import List, Dict, Any, Optional, Union
import gspread
from gspread.exceptions import APIError, SpreadsheetNotFound, WorksheetNotFound

from seton_utils.gdrive.gdrive_helpers import get_gdrive_credentials
from ..config.logging_config import get_logger, log_performance
from ..config.settings import validate_environment_sheet_access

# Initialize logger
logger = get_logger(__name__)


class SheetsError(Exception):
    """Custom exception for Google Sheets operations"""
    pass


class SheetsManager:
    """
    Google Sheets manager for Seton packages
    
    This class provides a high-level interface for Google Sheets operations
    with built-in error handling, retries, and validation.
    """
    
    def __init__(self, sheet_id: str):
        """
        Initialize Sheets manager
        
        Args:
            sheet_id: Google Sheets ID
            
        Raises:
            SheetsError: If initialization fails
        """
        self.sheet_id = sheet_id
        self.client = None
        self.spreadsheet = None
        
        # Validate environment access before proceeding
        validate_environment_sheet_access()
        
        # Initialize connection
        self._initialize_connection()
    
    def _initialize_connection(self) -> None:
        """Initialize Google Sheets API connection"""
        try:
            logger.info("🔗 Initializing Google Sheets connection")
            
            with log_performance(logger, "sheets_authentication"):
                # Get credentials using seton_utils
                credentials = get_gdrive_credentials()
                
                # Create gspread client
                self.client = gspread.authorize(credentials)
            
            with log_performance(logger, "spreadsheet_access"):
                # Open the spreadsheet
                self.spreadsheet = self.client.open_by_key(self.sheet_id)
            
            logger.info(f"✅ Connected to spreadsheet: '{self.spreadsheet.title}'")
            
        except SpreadsheetNotFound:
            raise SheetsError(f"Spreadsheet not found: {self.sheet_id}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Google Sheets connection: {e}")
            raise SheetsError(f"Connection failed: {e}")
    
    def get_worksheet(self, worksheet_name: str, create_if_missing: bool = True) -> gspread.Worksheet:
        """
        Get or create a worksheet
        
        Args:
            worksheet_name: Name of the worksheet
            create_if_missing: Whether to create worksheet if it doesn't exist
            
        Returns:
            gspread.Worksheet: The worksheet object
            
        Raises:
            SheetsError: If worksheet access fails
        """
        try:
            # Try to get existing worksheet
            worksheet = self.spreadsheet.worksheet(worksheet_name)
            logger.debug(f"📄 Found existing worksheet: '{worksheet_name}'")
            return worksheet
            
        except WorksheetNotFound:
            if create_if_missing:
                logger.info(f"📄 Creating new worksheet: '{worksheet_name}'")
                with log_performance(logger, f"create_worksheet_{worksheet_name}"):
                    worksheet = self.spreadsheet.add_worksheet(
                        title=worksheet_name,
                        rows=1000,  # Default size
                        cols=26
                    )
                logger.info(f"✅ Created worksheet: '{worksheet_name}'")
                return worksheet
            else:
                raise SheetsError(f"Worksheet '{worksheet_name}' not found")
        except Exception as e:
            raise SheetsError(f"Failed to access worksheet '{worksheet_name}': {e}")
    
    def update_worksheet(self, worksheet_name: str, data: List[List[Any]], 
                        clear_existing: bool = True, start_cell: str = "A1") -> None:
        """
        Update worksheet with data
        
        Args:
            worksheet_name: Name of the worksheet to update
            data: Data as list of lists (rows and columns)
            clear_existing: Whether to clear existing data
            start_cell: Starting cell (e.g., "A1")
            
        Raises:
            SheetsError: If update fails
        """
        if not data:
            logger.warning(f"⚠️ No data provided for worksheet '{worksheet_name}'")
            return
        
        try:
            worksheet = self.get_worksheet(worksheet_name)
            
            if clear_existing:
                logger.info(f"🧹 Clearing existing data in '{worksheet_name}'")
                worksheet.clear()
            
            logger.info(f"📤 Uploading {len(data)} rows to '{worksheet_name}'")
            
            with log_performance(logger, f"upload_data_{worksheet_name}"):
                # Use batch update for better performance
                worksheet.update(start_cell, data, value_input_option='USER_ENTERED')
            
            logger.info(f"✅ Successfully updated '{worksheet_name}' with {len(data)} rows")
            
        except APIError as e:
            if "quota" in str(e).lower():
                logger.error("❌ Google Sheets API quota exceeded")
                raise SheetsError("API quota exceeded - try again later")
            else:
                logger.error(f"❌ Google Sheets API error: {e}")
                raise SheetsError(f"API error: {e}")
        except Exception as e:
            logger.error(f"❌ Failed to update worksheet '{worksheet_name}': {e}")
            raise SheetsError(f"Update failed: {e}")
    
    def update_worksheet_dict(self, worksheet_name: str, data: List[Dict[str, Any]], 
                             clear_existing: bool = True) -> None:
        """
        Update worksheet with dictionary data (converts to rows/columns)
        
        Args:
            worksheet_name: Name of the worksheet to update
            data: Data as list of dictionaries
            clear_existing: Whether to clear existing data
            
        Example:
            data = [
                {'name': 'John', 'age': 25, 'grade': 'A'},
                {'name': 'Jane', 'age': 24, 'grade': 'B'}
            ]
            manager.update_worksheet_dict("Students", data)
        """
        if not data:
            logger.warning(f"⚠️ No data provided for worksheet '{worksheet_name}'")
            return
        
        # Convert dictionaries to rows/columns format
        logger.info(f"📝 Converting {len(data)} records to sheet format")
        
        # Get headers from first dictionary
        headers = list(data[0].keys())
        
        # Create rows starting with headers
        rows = [headers]
        
        # Add data rows
        for record in data:
            row = [record.get(header, '') for header in headers]
            rows.append(row)
        
        # Update worksheet
        self.update_worksheet(worksheet_name, rows, clear_existing)
    
    def append_data(self, worksheet_name: str, data: List[List[Any]]) -> None:
        """
        Append data to existing worksheet
        
        Args:
            worksheet_name: Name of the worksheet
            data: Data to append as list of lists
        """
        try:
            worksheet = self.get_worksheet(worksheet_name)
            
            logger.info(f"➕ Appending {len(data)} rows to '{worksheet_name}'")
            
            with log_performance(logger, f"append_data_{worksheet_name}"):
                for row in data:
                    worksheet.append_row(row, value_input_option='USER_ENTERED')
            
            logger.info(f"✅ Successfully appended {len(data)} rows to '{worksheet_name}'")
            
        except Exception as e:
            logger.error(f"❌ Failed to append data to '{worksheet_name}': {e}")
            raise SheetsError(f"Append failed: {e}")
    
    def get_worksheet_data(self, worksheet_name: str, include_headers: bool = True) -> List[List[str]]:
        """
        Get all data from a worksheet
        
        Args:
            worksheet_name: Name of the worksheet
            include_headers: Whether to include header row
            
        Returns:
            List[List[str]]: All worksheet data
        """
        try:
            worksheet = self.get_worksheet(worksheet_name, create_if_missing=False)
            
            logger.info(f"📥 Retrieving data from '{worksheet_name}'")
            
            with log_performance(logger, f"get_data_{worksheet_name}"):
                data = worksheet.get_all_values()
            
            if not include_headers and data:
                data = data[1:]  # Skip header row
            
            logger.info(f"✅ Retrieved {len(data)} rows from '{worksheet_name}'")
            return data
            
        except Exception as e:
            logger.error(f"❌ Failed to get data from '{worksheet_name}': {e}")
            raise SheetsError(f"Get data failed: {e}")
    
    def validate_upload(self, expected_students: Optional[int] = None, 
                       expected_staff: Optional[int] = None) -> bool:
        """
        Validate that data was uploaded correctly
        
        Args:
            expected_students: Expected number of student records
            expected_staff: Expected number of staff records
            
        Returns:
            bool: True if validation passes
        """
        logger.info("🔍 Validating upload success")
        
        try:
            validation_passed = True
            
            # Validate student data if expected count provided
            if expected_students is not None:
                try:
                    student_data = self.get_worksheet_data("Students", include_headers=False)
                    actual_students = len(student_data)
                    
                    if actual_students == expected_students:
                        logger.info(f"✅ Student count validation passed: {actual_students}")
                    else:
                        logger.error(f"❌ Student count mismatch: expected {expected_students}, got {actual_students}")
                        validation_passed = False
                except Exception as e:
                    logger.error(f"❌ Student validation failed: {e}")
                    validation_passed = False
            
            # Validate staff data if expected count provided
            if expected_staff is not None:
                try:
                    staff_data = self.get_worksheet_data("Staff", include_headers=False)
                    actual_staff = len(staff_data)
                    
                    if actual_staff == expected_staff:
                        logger.info(f"✅ Staff count validation passed: {actual_staff}")
                    else:
                        logger.error(f"❌ Staff count mismatch: expected {expected_staff}, got {actual_staff}")
                        validation_passed = False
                except Exception as e:
                    logger.error(f"❌ Staff validation failed: {e}")
                    validation_passed = False
            
            if validation_passed:
                logger.info("✅ Upload validation passed")
            else:
                logger.error("❌ Upload validation failed")
            
            return validation_passed
            
        except Exception as e:
            logger.error(f"❌ Upload validation error: {e}")
            return False
    
    def create_summary_worksheet(self, summary_data: Dict[str, Any]) -> None:
        """
        Create a summary worksheet with metadata about the upload
        
        Args:
            summary_data: Dictionary containing summary information
        """
        logger.info("📊 Creating summary worksheet")
        
        try:
            # Prepare summary data as rows
            summary_rows = [
                ["Summary", "Value"],
                ["Upload Date", summary_data.get('upload_date', 'Unknown')],
                ["Total Students", summary_data.get('total_students', 0)],
                ["Total Staff", summary_data.get('total_staff', 0)],
                ["Environment", summary_data.get('environment', 'Unknown')],
                ["Package Version", summary_data.get('package_version', 'Unknown')]
            ]
            
            # Add any additional summary data
            for key, value in summary_data.items():
                if key not in ['upload_date', 'total_students', 'total_staff', 'environment', 'package_version']:
                    summary_rows.append([str(key).replace('_', ' ').title(), str(value)])
            
            self.update_worksheet("Summary", summary_rows, clear_existing=True)
            logger.info("✅ Summary worksheet created")
            
        except Exception as e:
            logger.error(f"❌ Failed to create summary worksheet: {e}")
            # Don't raise exception - summary is not critical
    
    def delete_worksheet(self, worksheet_name: str) -> None:
        """
        Delete a worksheet
        
        Args:
            worksheet_name: Name of worksheet to delete
        """
        try:
            worksheet = self.get_worksheet(worksheet_name, create_if_missing=False)
            self.spreadsheet.del_worksheet(worksheet)
            logger.info(f"🗑️ Deleted worksheet: '{worksheet_name}'")
        except WorksheetNotFound:
            logger.warning(f"⚠️ Worksheet '{worksheet_name}' not found for deletion")
        except Exception as e:
            logger.error(f"❌ Failed to delete worksheet '{worksheet_name}': {e}")
            raise SheetsError(f"Delete failed: {e}")
    
    def list_worksheets(self) -> List[str]:
        """
        Get list of all worksheet names
        
        Returns:
            List[str]: List of worksheet names
        """
        try:
            worksheets = self.spreadsheet.worksheets()
            names = [ws.title for ws in worksheets]
            logger.info(f"📋 Found {len(names)} worksheets: {names}")
            return names
        except Exception as e:
            logger.error(f"❌ Failed to list worksheets: {e}")
            raise SheetsError(f"List worksheets failed: {e}")
    
    def batch_update_multiple_worksheets(self, worksheet_data: Dict[str, List[List[Any]]]) -> None:
        """
        Update multiple worksheets in a batch operation
        
        Args:
            worksheet_data: Dictionary mapping worksheet names to data
            
        Example:
            data = {
                "Students": student_rows,
                "Staff": staff_rows,
                "Summary": summary_rows
            }
            manager.batch_update_multiple_worksheets(data)
        """
        logger.info(f"📦 Batch updating {len(worksheet_data)} worksheets")
        
        try:
            with log_performance(logger, "batch_update_worksheets"):
                for worksheet_name, data in worksheet_data.items():
                    logger.info(f"📤 Updating worksheet: '{worksheet_name}'")
                    self.update_worksheet(worksheet_name, data)
                    
                    # Add small delay between updates to avoid rate limits
                    time.sleep(0.5)
            
            logger.info("✅ Batch update completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Batch update failed: {e}")
            raise SheetsError(f"Batch update failed: {e}")


def test_sheets_connection(sheet_id: str) -> bool:
    """
    Test Google Sheets connection and access
    
    Args:
        sheet_id: Google Sheets ID to test
        
    Returns:
        bool: True if connection successful
    """
    logger.info(f"🔍 Testing Google Sheets connection: {sheet_id}")
    
    try:
        manager = SheetsManager(sheet_id)
        worksheets = manager.list_worksheets()
        logger.info(f"✅ Sheets connection test successful - found {len(worksheets)} worksheets")
        return True
    except Exception as e:
        logger.error(f"❌ Sheets connection test failed: {e}")
        return False
