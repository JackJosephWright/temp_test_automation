"""
Tests for Google Sheets manager module

This module tests the Google Sheets integration patterns used in
Seton packages, including credential management, worksheet operations,
data uploading, and error handling.

Key Test Areas:
- seton_utils credential integration
- Worksheet creation and management
- Data formatting and upload
- Batch operations
- Error handling and retries
- Environment safety validation
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date

from src.seton_package_template.google_sheets.sheets_manager import (
    SheetsManager,
    SheetsError,
    test_sheets_connection
)


class TestSheetsManagerInitialization:
    """Test SheetsManager initialization and connection"""
    
    def test_initialization_success(self, mock_seton_utils, mock_environment_settings):
        """Test successful SheetsManager initialization"""
        with patch('src.seton_package_template.google_sheets.sheets_manager.gspread') as mock_gspread:
            # Setup mocks
            mock_client = Mock()
            mock_spreadsheet = Mock()
            mock_spreadsheet.title = "Test Spreadsheet"
            
            mock_gspread.authorize.return_value = mock_client
            mock_client.open_by_key.return_value = mock_spreadsheet
            
            manager = SheetsManager("test_sheet_id")
            
            # Verify initialization
            assert manager.sheet_id == "test_sheet_id"
            assert manager.client == mock_client
            assert manager.spreadsheet == mock_spreadsheet
            
            # Verify credential and client setup
            mock_seton_utils['get_gdrive_credentials'].assert_called_once()
            mock_gspread.authorize.assert_called_once()
            mock_client.open_by_key.assert_called_once_with("test_sheet_id")
    
    def test_initialization_spreadsheet_not_found(self, mock_seton_utils, mock_environment_settings):
        """Test initialization with non-existent spreadsheet"""
        with patch('src.seton_package_template.google_sheets.sheets_manager.gspread') as mock_gspread:
            from gspread.exceptions import SpreadsheetNotFound
            
            mock_client = Mock()
            mock_gspread.authorize.return_value = mock_client
            mock_client.open_by_key.side_effect = SpreadsheetNotFound()
            
            with pytest.raises(SheetsError) as exc_info:
                SheetsManager("invalid_sheet_id")
            
            assert "Spreadsheet not found" in str(exc_info.value)
    
    def test_initialization_credential_failure(self, mock_seton_utils, mock_environment_settings):
        """Test initialization with credential failure"""
        mock_seton_utils['get_gdrive_credentials'].side_effect = Exception("Credential error")
        
        with pytest.raises(SheetsError) as exc_info:
            SheetsManager("test_sheet_id")
        
        assert "Connection failed" in str(exc_info.value)
    
    def test_environment_validation_called(self, mock_seton_utils, mock_environment_settings):
        """Test that environment validation is called during initialization"""
        with patch('src.seton_package_template.google_sheets.sheets_manager.gspread'), \
             patch('src.seton_package_template.google_sheets.sheets_manager.validate_environment_sheet_access') as mock_validate:
            
            SheetsManager("test_sheet_id")
            
            mock_validate.assert_called_once()


class TestWorksheetOperations:
    """Test worksheet creation and management"""
    
    @pytest.fixture
    def initialized_manager(self, mock_seton_utils, mock_environment_settings):
        """Fixture providing an initialized SheetsManager"""
        with patch('src.seton_package_template.google_sheets.sheets_manager.gspread') as mock_gspread:
            mock_client = Mock()
            mock_spreadsheet = Mock()
            mock_spreadsheet.title = "Test Spreadsheet"
            
            mock_gspread.authorize.return_value = mock_client
            mock_client.open_by_key.return_value = mock_spreadsheet
            
            manager = SheetsManager("test_sheet_id")
            return manager, mock_spreadsheet
    
    def test_get_existing_worksheet(self, initialized_manager, caplog):
        """Test getting an existing worksheet"""
        manager, mock_spreadsheet = initialized_manager
        
        mock_worksheet = Mock()
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        
        result = manager.get_worksheet("Students")
        
        assert result == mock_worksheet
        mock_spreadsheet.worksheet.assert_called_once_with("Students")
        assert "Found existing worksheet: 'Students'" in caplog.text
    
    def test_create_missing_worksheet(self, initialized_manager, caplog):
        """Test creating a worksheet when it doesn't exist"""
        manager, mock_spreadsheet = initialized_manager
        
        from gspread.exceptions import WorksheetNotFound
        
        mock_new_worksheet = Mock()
        mock_spreadsheet.worksheet.side_effect = WorksheetNotFound()
        mock_spreadsheet.add_worksheet.return_value = mock_new_worksheet
        
        result = manager.get_worksheet("NewSheet", create_if_missing=True)
        
        assert result == mock_new_worksheet
        mock_spreadsheet.add_worksheet.assert_called_once_with(
            title="NewSheet",
            rows=1000,
            cols=26
        )
        assert "Creating new worksheet: 'NewSheet'" in caplog.text
    
    def test_get_worksheet_no_create(self, initialized_manager):
        """Test getting worksheet with create_if_missing=False"""
        manager, mock_spreadsheet = initialized_manager
        
        from gspread.exceptions import WorksheetNotFound
        
        mock_spreadsheet.worksheet.side_effect = WorksheetNotFound()
        
        with pytest.raises(SheetsError) as exc_info:
            manager.get_worksheet("NonExistent", create_if_missing=False)
        
        assert "Worksheet 'NonExistent' not found" in str(exc_info.value)


class TestDataUploadOperations:
    """Test data upload and formatting operations"""
    
    @pytest.fixture
    def manager_with_worksheet(self, mock_seton_utils, mock_environment_settings):
        """Fixture providing manager with mocked worksheet"""
        with patch('src.seton_package_template.google_sheets.sheets_manager.gspread') as mock_gspread:
            mock_client = Mock()
            mock_spreadsheet = Mock()
            mock_worksheet = Mock()
            
            mock_gspread.authorize.return_value = mock_client
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            mock_spreadsheet.title = "Test Spreadsheet"
            
            manager = SheetsManager("test_sheet_id")
            return manager, mock_worksheet
    
    def test_update_worksheet_success(self, manager_with_worksheet, sample_sheets_data, caplog):
        """Test successful worksheet update"""
        manager, mock_worksheet = manager_with_worksheet
        
        manager.update_worksheet("Students", sample_sheets_data)
        
        # Verify operations
        mock_worksheet.clear.assert_called_once()
        mock_worksheet.update.assert_called_once_with(
            "A1", sample_sheets_data, value_input_option='USER_ENTERED'
        )
        assert "Successfully updated 'Students' with 4 rows" in caplog.text
    
    def test_update_worksheet_no_clear(self, manager_with_worksheet, sample_sheets_data):
        """Test worksheet update without clearing existing data"""
        manager, mock_worksheet = manager_with_worksheet
        
        manager.update_worksheet("Students", sample_sheets_data, clear_existing=False)
        
        # Verify clear was not called
        mock_worksheet.clear.assert_not_called()
        mock_worksheet.update.assert_called_once()
    
    def test_update_worksheet_empty_data(self, manager_with_worksheet, caplog):
        """Test worksheet update with empty data"""
        manager, mock_worksheet = manager_with_worksheet
        
        manager.update_worksheet("Students", [])
        
        # Should not perform any operations
        mock_worksheet.clear.assert_not_called()
        mock_worksheet.update.assert_not_called()
        assert "No data provided" in caplog.text
    
    def test_update_worksheet_dict_format(self, manager_with_worksheet, processed_student_data, caplog):
        """Test worksheet update with dictionary data"""
        manager, mock_worksheet = manager_with_worksheet
        
        manager.update_worksheet_dict("Students", processed_student_data)
        
        # Verify conversion and update
        mock_worksheet.clear.assert_called_once()
        mock_worksheet.update.assert_called_once()
        
        # Verify data conversion was logged
        assert "Converting 2 records to sheet format" in caplog.text
    
    def test_update_worksheet_api_quota_error(self, manager_with_worksheet, sample_sheets_data):
        """Test handling of Google Sheets API quota errors"""
        manager, mock_worksheet = manager_with_worksheet
        
        from gspread.exceptions import APIError
        
        api_error = APIError({'error': {'message': 'quota exceeded'}})
        mock_worksheet.update.side_effect = api_error
        
        with pytest.raises(SheetsError) as exc_info:
            manager.update_worksheet("Students", sample_sheets_data)
        
        assert "API quota exceeded" in str(exc_info.value)
    
    def test_append_data_success(self, manager_with_worksheet, sample_sheets_data, caplog):
        """Test successful data appending"""
        manager, mock_worksheet = manager_with_worksheet
        
        manager.append_data("Students", sample_sheets_data)
        
        # Verify append operations
        assert mock_worksheet.append_row.call_count == len(sample_sheets_data)
        assert "Successfully appended 4 rows" in caplog.text


class TestDataRetrieval:
    """Test data retrieval operations"""
    
    def test_get_worksheet_data_with_headers(self, mock_seton_utils, mock_environment_settings, sample_sheets_data):
        """Test getting worksheet data including headers"""
        with patch('src.seton_package_template.google_sheets.sheets_manager.gspread') as mock_gspread:
            mock_client = Mock()
            mock_spreadsheet = Mock()
            mock_worksheet = Mock()
            
            mock_gspread.authorize.return_value = mock_client
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            mock_spreadsheet.title = "Test Spreadsheet"
            
            mock_worksheet.get_all_values.return_value = sample_sheets_data
            
            manager = SheetsManager("test_sheet_id")
            result = manager.get_worksheet_data("Students", include_headers=True)
            
            assert result == sample_sheets_data
            assert len(result) == 4  # Including header row
    
    def test_get_worksheet_data_without_headers(self, mock_seton_utils, mock_environment_settings, sample_sheets_data):
        """Test getting worksheet data excluding headers"""
        with patch('src.seton_package_template.google_sheets.sheets_manager.gspread') as mock_gspread:
            mock_client = Mock()
            mock_spreadsheet = Mock()
            mock_worksheet = Mock()
            
            mock_gspread.authorize.return_value = mock_client
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            mock_spreadsheet.title = "Test Spreadsheet"
            
            mock_worksheet.get_all_values.return_value = sample_sheets_data
            
            manager = SheetsManager("test_sheet_id")
            result = manager.get_worksheet_data("Students", include_headers=False)
            
            assert len(result) == 3  # Excluding header row
            assert result == sample_sheets_data[1:]  # Skip first row


class TestValidationOperations:
    """Test upload validation and verification"""
    
    def test_validate_upload_success(self, mock_seton_utils, mock_environment_settings, caplog):
        """Test successful upload validation"""
        with patch('src.seton_package_template.google_sheets.sheets_manager.gspread') as mock_gspread:
            mock_client = Mock()
            mock_spreadsheet = Mock()
            mock_worksheet = Mock()
            
            mock_gspread.authorize.return_value = mock_client
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            mock_spreadsheet.title = "Test Spreadsheet"
            
            # Mock worksheet data (excluding headers)
            mock_worksheet.get_all_values.side_effect = [
                [['header'], ['data1'], ['data2']],  # Students: 2 data rows
                [['header'], ['staff1'], ['staff2'], ['staff3']]  # Staff: 3 data rows
            ]
            
            manager = SheetsManager("test_sheet_id")
            result = manager.validate_upload(expected_students=2, expected_staff=3)
            
            assert result is True
            assert "Student count validation passed: 2" in caplog.text
            assert "Staff count validation passed: 3" in caplog.text
    
    def test_validate_upload_count_mismatch(self, mock_seton_utils, mock_environment_settings, caplog):
        """Test upload validation with count mismatch"""
        with patch('src.seton_package_template.google_sheets.sheets_manager.gspread') as mock_gspread:
            mock_client = Mock()
            mock_spreadsheet = Mock()
            mock_worksheet = Mock()
            
            mock_gspread.authorize.return_value = mock_client
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            mock_spreadsheet.title = "Test Spreadsheet"
            
            # Mock worksheet data with wrong counts
            mock_worksheet.get_all_values.return_value = [['header'], ['data1']]  # Only 1 data row
            
            manager = SheetsManager("test_sheet_id")
            result = manager.validate_upload(expected_students=5)  # Expecting 5, got 1
            
            assert result is False
            assert "Student count mismatch: expected 5, got 1" in caplog.text


class TestBatchOperations:
    """Test batch operations and performance features"""
    
    def test_batch_update_multiple_worksheets(self, mock_seton_utils, mock_environment_settings, caplog):
        """Test batch updating multiple worksheets"""
        with patch('src.seton_package_template.google_sheets.sheets_manager.gspread') as mock_gspread, \
             patch('time.sleep') as mock_sleep:  # Mock sleep to speed up test
            
            mock_client = Mock()
            mock_spreadsheet = Mock()
            mock_worksheet = Mock()
            
            mock_gspread.authorize.return_value = mock_client
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            mock_spreadsheet.title = "Test Spreadsheet"
            
            manager = SheetsManager("test_sheet_id")
            
            batch_data = {
                "Students": [['header'], ['data1']],
                "Staff": [['header'], ['data2']],
                "Summary": [['metric'], ['value']]
            }
            
            manager.batch_update_multiple_worksheets(batch_data)
            
            # Verify all worksheets were updated
            assert mock_worksheet.clear.call_count == 3
            assert mock_worksheet.update.call_count == 3
            assert mock_sleep.call_count == 3  # Rate limiting delays
            assert "Batch update completed successfully" in caplog.text
    
    def test_create_summary_worksheet(self, mock_seton_utils, mock_environment_settings, caplog):
        """Test summary worksheet creation"""
        with patch('src.seton_package_template.google_sheets.sheets_manager.gspread') as mock_gspread:
            mock_client = Mock()
            mock_spreadsheet = Mock()
            mock_worksheet = Mock()
            
            mock_gspread.authorize.return_value = mock_client
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            mock_spreadsheet.title = "Test Spreadsheet"
            
            manager = SheetsManager("test_sheet_id")
            
            summary_data = {
                'upload_date': '2024-01-01',
                'total_students': 100,
                'total_staff': 25,
                'environment': 'testing',
                'custom_metric': 'test_value'
            }
            
            manager.create_summary_worksheet(summary_data)
            
            # Verify summary worksheet was created
            mock_worksheet.clear.assert_called_once()
            mock_worksheet.update.assert_called_once()
            
            # Verify summary data structure
            update_call = mock_worksheet.update.call_args[0]
            summary_rows = update_call[1]  # The data passed to update
            
            assert ['Summary', 'Value'] in summary_rows  # Header row
            assert ['Upload Date', '2024-01-01'] in summary_rows
            assert ['Total Students', 100] in summary_rows
            assert "Summary worksheet created" in caplog.text


class TestErrorHandlingAndRobustness:
    """Test error handling and robustness features"""
    
    def test_worksheet_deletion_success(self, mock_seton_utils, mock_environment_settings, caplog):
        """Test successful worksheet deletion"""
        with patch('src.seton_package_template.google_sheets.sheets_manager.gspread') as mock_gspread:
            mock_client = Mock()
            mock_spreadsheet = Mock()
            mock_worksheet = Mock()
            
            mock_gspread.authorize.return_value = mock_client
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            mock_spreadsheet.title = "Test Spreadsheet"
            
            manager = SheetsManager("test_sheet_id")
            manager.delete_worksheet("TestSheet")
            
            mock_spreadsheet.del_worksheet.assert_called_once_with(mock_worksheet)
            assert "Deleted worksheet: 'TestSheet'" in caplog.text
    
    def test_list_worksheets_success(self, mock_seton_utils, mock_environment_settings, caplog):
        """Test listing all worksheets"""
        with patch('src.seton_package_template.google_sheets.sheets_manager.gspread') as mock_gspread:
            mock_client = Mock()
            mock_spreadsheet = Mock()
            
            # Create mock worksheets
            mock_ws1 = Mock()
            mock_ws1.title = "Students"
            mock_ws2 = Mock()
            mock_ws2.title = "Staff"
            
            mock_gspread.authorize.return_value = mock_client
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_spreadsheet.title = "Test Spreadsheet"
            mock_spreadsheet.worksheets.return_value = [mock_ws1, mock_ws2]
            
            manager = SheetsManager("test_sheet_id")
            result = manager.list_worksheets()
            
            assert result == ["Students", "Staff"]
            assert "Found 2 worksheets: ['Students', 'Staff']" in caplog.text


@pytest.mark.sheets
class TestSheetsIntegration:
    """Integration tests for Google Sheets functionality"""
    
    def test_complete_sheets_workflow(self, mock_seton_utils, mock_environment_settings, 
                                     processed_student_data, processed_staff_data, caplog):
        """Test complete Google Sheets workflow"""
        with patch('src.seton_package_template.google_sheets.sheets_manager.gspread') as mock_gspread:
            mock_client = Mock()
            mock_spreadsheet = Mock()
            mock_worksheet = Mock()
            
            mock_gspread.authorize.return_value = mock_client
            mock_client.open_by_key.return_value = mock_spreadsheet
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            mock_spreadsheet.title = "Test Spreadsheet"
            
            # Mock validation data
            mock_worksheet.get_all_values.side_effect = [
                [['header']] + [['data']] * len(processed_student_data),  # Students
                [['header']] + [['data']] * len(processed_staff_data)     # Staff
            ]
            
            manager = SheetsManager("test_sheet_id")
            
            # Upload student data
            manager.update_worksheet_dict("Students", processed_student_data)
            
            # Upload staff data
            manager.update_worksheet_dict("Staff", processed_staff_data)
            
            # Validate upload
            validation_result = manager.validate_upload(
                expected_students=len(processed_student_data),
                expected_staff=len(processed_staff_data)
            )
            
            assert validation_result is True
            assert "Successfully updated 'Students'" in caplog.text
            assert "Successfully updated 'Staff'" in caplog.text


class TestConnectionTesting:
    """Test connection testing utilities"""
    
    def test_sheets_connection_test_success(self, mock_seton_utils, mock_environment_settings, caplog):
        """Test successful sheets connection test"""
        with patch('src.seton_package_template.google_sheets.sheets_manager.SheetsManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager.list_worksheets.return_value = ["Sheet1", "Sheet2"]
            mock_manager_class.return_value = mock_manager
            
            result = test_sheets_connection("test_sheet_id")
            
            assert result is True
            mock_manager_class.assert_called_once_with("test_sheet_id")
            assert "Sheets connection test successful" in caplog.text
    
    def test_sheets_connection_test_failure(self, mock_seton_utils, mock_environment_settings, caplog):
        """Test sheets connection test failure"""
        with patch('src.seton_package_template.google_sheets.sheets_manager.SheetsManager') as mock_manager_class:
            mock_manager_class.side_effect = Exception("Connection failed")
            
            result = test_sheets_connection("invalid_sheet_id")
            
            assert result is False
            assert "Sheets connection test failed" in caplog.text
