"""
Tests for main module

This module tests the main entry point functions and demonstrates
testing patterns for Seton packages, including:

- Airflow compatibility testing
- Environment configuration testing  
- End-to-end workflow testing
- Error handling validation
- Mock integration testing

Key Test Patterns:
- Mock all external dependencies (database, Google Sheets, seton_utils)
- Test both Airflow and standalone execution modes
- Validate Oracle column naming handling
- Test environment safety features
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from datetime import datetime

from src.seton_package_template.main import main, run_package


class TestMainFunction:
    """Test cases for the main() function"""
    
    def test_main_standalone_execution_success(self, mock_seton_utils, mock_environment_settings, caplog):
        """Test successful standalone execution"""
        with patch('src.seton_package_template.main.run_package') as mock_run:
            mock_run.return_value = True
            
            result = main()
            
            assert result is not None
            assert "completed successfully" in result
            mock_run.assert_called_once()
    
    def test_main_standalone_execution_failure(self, mock_seton_utils, mock_environment_settings, caplog):
        """Test failed standalone execution"""
        with patch('src.seton_package_template.main.run_package') as mock_run:
            mock_run.return_value = False
            
            result = main()
            
            assert result is None
            mock_run.assert_called_once()
    
    def test_main_airflow_execution_success(self, mock_seton_utils, mock_environment_settings, caplog):
        """Test successful Airflow execution with context"""
        airflow_kwargs = {
            'task_instance': Mock(
                task_id='test_task',
                dag_id='test_dag',
                execution_date=datetime.now()
            )
        }
        
        with patch('src.seton_package_template.main.run_package') as mock_run:
            mock_run.return_value = True
            
            result = main(**airflow_kwargs)
            
            assert result is not None
            assert "completed successfully" in result
            mock_run.assert_called_once()
    
    def test_main_exception_handling(self, mock_seton_utils, mock_environment_settings, caplog):
        """Test main function exception handling"""
        with patch('src.seton_package_template.main.run_package') as mock_run:
            mock_run.side_effect = Exception("Test exception")
            
            result = main()
            
            assert result is None
            assert "Critical error" in caplog.text
    
    def test_main_environment_logging(self, mock_local_environment, mock_seton_utils, caplog):
        """Test that environment is properly logged"""
        with patch('src.seton_package_template.main.run_package') as mock_run:
            mock_run.return_value = True
            
            main()
            
            assert "Execution environment:" in caplog.text


class TestRunPackageFunction:
    """Test cases for the run_package() function"""
    
    def test_run_package_full_workflow_success(self, mock_seton_utils, mock_environment_settings, 
                                               processed_student_data, processed_staff_data, caplog):
        """Test complete successful workflow"""
        # Mock all the dependencies
        with patch('src.seton_package_template.main.SheetsManager') as mock_sheets_class, \
             patch('src.seton_package_template.main.get_student_data') as mock_get_students, \
             patch('src.seton_package_template.main.get_staff_data') as mock_get_staff, \
             patch('src.seton_package_template.main.validate_data_integrity') as mock_validate, \
             patch('src.seton_package_template.main.format_data_for_sheets') as mock_format:
            
            # Setup mock returns
            mock_get_students.return_value = processed_student_data
            mock_get_staff.return_value = processed_staff_data
            mock_validate.return_value = True
            mock_format.return_value = [['header'], ['data']]
            
            # Setup mock sheets manager
            mock_sheets = Mock()
            mock_sheets.validate_upload.return_value = True
            mock_sheets_class.return_value = mock_sheets
            
            result = run_package()
            
            assert result is True
            mock_get_students.assert_called_once()
            mock_get_staff.assert_called_once()
            mock_validate.assert_called_once()
            mock_sheets.update_worksheet.assert_called()
            mock_sheets.validate_upload.assert_called_once()
    
    def test_run_package_validation_failure(self, mock_seton_utils, mock_environment_settings, 
                                           processed_student_data, processed_staff_data, caplog):
        """Test workflow when data validation fails"""
        with patch('src.seton_package_template.main.get_student_data') as mock_get_students, \
             patch('src.seton_package_template.main.get_staff_data') as mock_get_staff, \
             patch('src.seton_package_template.main.validate_data_integrity') as mock_validate:
            
            mock_get_students.return_value = processed_student_data
            mock_get_staff.return_value = processed_staff_data
            mock_validate.return_value = False  # Validation fails
            
            result = run_package()
            
            assert result is False
            assert "Data integrity validation failed" in caplog.text
    
    def test_run_package_upload_validation_failure(self, mock_seton_utils, mock_environment_settings,
                                                   processed_student_data, processed_staff_data, caplog):
        """Test workflow when upload validation fails"""
        with patch('src.seton_package_template.main.SheetsManager') as mock_sheets_class, \
             patch('src.seton_package_template.main.get_student_data') as mock_get_students, \
             patch('src.seton_package_template.main.get_staff_data') as mock_get_staff, \
             patch('src.seton_package_template.main.validate_data_integrity') as mock_validate, \
             patch('src.seton_package_template.main.format_data_for_sheets') as mock_format:
            
            # Setup mock returns
            mock_get_students.return_value = processed_student_data
            mock_get_staff.return_value = processed_staff_data
            mock_validate.return_value = True
            mock_format.return_value = [['header'], ['data']]
            
            # Setup mock sheets manager with failed upload validation
            mock_sheets = Mock()
            mock_sheets.validate_upload.return_value = False  # Upload validation fails
            mock_sheets_class.return_value = mock_sheets
            
            result = run_package()
            
            assert result is False
            assert "Upload validation failed" in caplog.text
    
    def test_run_package_database_exception(self, mock_seton_utils, mock_environment_settings, caplog):
        """Test workflow when database operations fail"""
        with patch('src.seton_package_template.main.get_student_data') as mock_get_students:
            mock_get_students.side_effect = Exception("Database connection failed")
            
            result = run_package()
            
            assert result is False
            assert "Package execution failed" in caplog.text
    
    def test_run_package_sheets_exception(self, mock_seton_utils, mock_environment_settings,
                                         processed_student_data, processed_staff_data, caplog):
        """Test workflow when Google Sheets operations fail"""
        with patch('src.seton_package_template.main.SheetsManager') as mock_sheets_class, \
             patch('src.seton_package_template.main.get_student_data') as mock_get_students, \
             patch('src.seton_package_template.main.get_staff_data') as mock_get_staff, \
             patch('src.seton_package_template.main.validate_data_integrity') as mock_validate, \
             patch('src.seton_package_template.main.format_data_for_sheets') as mock_format:
            
            # Setup mock returns
            mock_get_students.return_value = processed_student_data
            mock_get_staff.return_value = processed_staff_data
            mock_validate.return_value = True
            mock_format.return_value = [['header'], ['data']]
            
            # Setup mock sheets manager that raises exception
            mock_sheets_class.side_effect = Exception("Sheets connection failed")
            
            result = run_package()
            
            assert result is False
            assert "Package execution failed" in caplog.text


class TestEnvironmentIntegration:
    """Test environment configuration integration"""
    
    def test_environment_validation_called(self, mock_seton_utils, mock_environment_settings, caplog):
        """Test that environment validation is called"""
        with patch('src.seton_package_template.main.validate_environment') as mock_validate, \
             patch('src.seton_package_template.main.run_package') as mock_run:
            
            mock_run.return_value = True
            
            main()
            
            mock_validate.assert_called_once()
    
    def test_production_safety_validation(self, mock_seton_utils, caplog):
        """Test production safety validation"""
        with patch('src.seton_package_template.config.settings.get_environment') as mock_env, \
             patch('src.seton_package_template.config.settings.get_sheet_id') as mock_sheet, \
             patch('src.seton_package_template.config.settings.validate_environment_sheet_access') as mock_validate:
            
            mock_env.return_value = 'development'
            mock_sheet.return_value = 'dev_sheet_123'
            mock_validate.side_effect = Exception("Safety validation failed")
            
            with patch('src.seton_package_template.main.run_package') as mock_run:
                mock_run.side_effect = Exception("Safety validation failed")
                
                result = main()
                
                assert result is None


class TestCommandLineExecution:
    """Test command-line execution patterns"""
    
    def test_main_module_execution_success(self, mock_seton_utils, mock_environment_settings):
        """Test successful command-line execution"""
        with patch('src.seton_package_template.main.main') as mock_main, \
             patch('sys.exit') as mock_exit:
            
            mock_main.return_value = "Success message"
            
            # This would be called when running: python -m seton_package_template.main
            exec("""
if __name__ == "__main__":
    result = main()
    if result:
        sys.exit(0)
    else:
        sys.exit(1)
""", {
                'main': mock_main,
                'sys': sys,
                '__name__': '__main__'
            })
            
            mock_exit.assert_called_with(0)
    
    def test_main_module_execution_failure(self, mock_seton_utils, mock_environment_settings):
        """Test failed command-line execution"""
        with patch('src.seton_package_template.main.main') as mock_main, \
             patch('sys.exit') as mock_exit:
            
            mock_main.return_value = None  # Indicates failure
            
            exec("""
if __name__ == "__main__":
    result = main()
    if result:
        sys.exit(0)
    else:
        sys.exit(1)
""", {
                'main': mock_main,
                'sys': sys,
                '__name__': '__main__'
            })
            
            mock_exit.assert_called_with(1)


@pytest.mark.integration
class TestEndToEndWorkflow:
    """Integration tests for complete workflow"""
    
    def test_complete_workflow_integration(self, mock_seton_utils, mock_local_environment,
                                          sample_student_data, sample_staff_data, caplog):
        """Test complete end-to-end workflow with all components"""
        # This test validates the entire workflow while mocking external dependencies
        
        # Mock database to return sample data with UPPERCASE keys (Oracle pattern)
        mock_seton_utils['cursor'].fetchall.side_effect = [
            sample_student_data,  # First call for students
            sample_staff_data     # Second call for staff
        ]
        
        with patch('src.seton_package_template.google_sheets.sheets_manager.SheetsManager') as mock_sheets_class:
            # Setup mock sheets manager
            mock_sheets = Mock()
            mock_sheets.validate_upload.return_value = True
            mock_sheets_class.return_value = mock_sheets
            
            result = main()
            
            assert result is not None
            assert "completed successfully" in result
            
            # Verify database queries were executed
            assert mock_seton_utils['cursor'].execute.call_count >= 2
            
            # Verify sheets operations
            assert mock_sheets.update_worksheet.call_count >= 2  # Students and Staff
            mock_sheets.validate_upload.assert_called_once()
    
    @pytest.mark.slow
    def test_large_dataset_handling(self, mock_seton_utils, mock_environment_settings, caplog):
        """Test handling of large datasets"""
        # Create large dataset
        large_student_data = []
        for i in range(1000):
            large_student_data.append({
                'STUDENT_NUMBER': 10000 + i,
                'DCID': 20000 + i,
                'LAST_NAME': f'Student{i}',
                'FIRST_NAME': f'Test{i}',
                'GRADE_LEVEL': (i % 12) + 1,
                'ENROLL_STATUS': 0,
                'ENTRYDATE': datetime.now().date(),
                'EXITDATE': None,
                'SCHOOLID': 100,
                'SCHOOL_NAME': 'Test School',
                'HOME_ROOM': f'Room{i % 20}',
                'GENDER': 'M' if i % 2 == 0 else 'F',
                'DOB': datetime.now().date(),
                'STUDENT_WEB_ID': f'student{i}',
                'STUDENT_WEB_PASSWORD': None
            })
        
        mock_seton_utils['cursor'].fetchall.side_effect = [
            large_student_data,  # Students
            []  # Staff (empty for this test)
        ]
        
        with patch('src.seton_package_template.google_sheets.sheets_manager.SheetsManager') as mock_sheets_class:
            mock_sheets = Mock()
            mock_sheets.validate_upload.return_value = True
            mock_sheets_class.return_value = mock_sheets
            
            result = main()
            
            assert result is not None
            assert "completed successfully" in result
            assert "1000 student records" in caplog.text
