"""
Tests for database queries module

This module tests the critical Oracle database integration patterns,
with special focus on the UPPERCASE column naming requirements.

CRITICAL TESTING PATTERN:
All test data must use UPPERCASE keys to simulate Oracle database behavior.
This is the most common source of bugs in Seton packages.

Key Test Areas:
- Oracle column naming handling (UPPERCASE -> lowercase)
- Database connection management
- Query execution and result processing
- Data validation and transformation
- Error handling for database operations
"""

import pytest
from unittest.mock import Mock, patch
from datetime import date, datetime
import cx_Oracle

from src.seton_package_template.database.queries import (
    get_student_data,
    get_staff_data,
    get_enrollment_data,
    validate_and_transform_student,
    validate_and_transform_staff,
    test_connection,
    DatabaseError
)


class TestGetStudentData:
    """Test student data retrieval with Oracle column naming"""
    
    def test_get_student_data_success(self, mock_seton_utils, sample_student_data, caplog):
        """Test successful student data retrieval with UPPERCASE columns"""
        # Setup mock cursor to return sample data with UPPERCASE keys
        mock_seton_utils['cursor'].fetchall.return_value = sample_student_data
        
        result = get_student_data()
        
        # Verify database operations
        mock_seton_utils['connect_to_ps'].assert_called_once()
        mock_seton_utils['cursor'].execute.assert_called_once()
        mock_seton_utils['cursor'].fetchall.assert_called_once()
        mock_seton_utils['cursor'].close.assert_called_once()
        mock_seton_utils['connection'].close.assert_called_once()
        
        # Verify data processing - should convert UPPERCASE to lowercase keys
        assert len(result) == len(sample_student_data)
        for i, student in enumerate(result):
            # Verify UPPERCASE keys were converted to lowercase
            assert 'student_number' in student  # lowercase
            assert 'STUDENT_NUMBER' not in student  # UPPERCASE removed
            assert student['student_number'] == sample_student_data[i]['STUDENT_NUMBER']
            
            assert 'last_name' in student
            assert student['last_name'] == sample_student_data[i]['LAST_NAME']
            
            assert 'grade_level' in student
            assert student['grade_level'] == sample_student_data[i]['GRADE_LEVEL']
        
        assert "student records from database" in caplog.text
    
    def test_get_student_data_oracle_error(self, mock_seton_utils, caplog):
        """Test Oracle database error handling"""
        # Setup mock to raise Oracle error
        mock_seton_utils['cursor'].execute.side_effect = cx_Oracle.Error("Oracle connection failed")
        
        with pytest.raises(DatabaseError) as exc_info:
            get_student_data()
        
        assert "Failed to retrieve student data" in str(exc_info.value)
        assert "Oracle database error" in caplog.text
    
    def test_get_student_data_unexpected_error(self, mock_seton_utils, caplog):
        """Test unexpected error handling"""
        # Setup mock to raise unexpected error
        mock_seton_utils['cursor'].fetchall.side_effect = Exception("Unexpected error")
        
        with pytest.raises(DatabaseError) as exc_info:
            get_student_data()
        
        assert "Unexpected error" in str(exc_info.value)
        assert "Unexpected error retrieving student data" in caplog.text
    
    def test_get_student_data_connection_cleanup(self, mock_seton_utils, sample_student_data):
        """Test that database connections are properly cleaned up"""
        mock_seton_utils['cursor'].fetchall.return_value = sample_student_data
        
        get_student_data()
        
        # Verify cleanup is called even on success
        mock_seton_utils['cursor'].close.assert_called_once()
        mock_seton_utils['connection'].close.assert_called_once()
    
    def test_get_student_data_cleanup_on_error(self, mock_seton_utils):
        """Test connection cleanup on error"""
        mock_seton_utils['cursor'].execute.side_effect = Exception("Test error")
        
        with pytest.raises(DatabaseError):
            get_student_data()
        
        # Verify cleanup is called even on error
        mock_seton_utils['cursor'].close.assert_called_once()
        mock_seton_utils['connection'].close.assert_called_once()


class TestGetStaffData:
    """Test staff data retrieval with Oracle column naming"""
    
    def test_get_staff_data_success(self, mock_seton_utils, sample_staff_data, caplog):
        """Test successful staff data retrieval with UPPERCASE columns"""
        mock_seton_utils['cursor'].fetchall.return_value = sample_staff_data
        
        result = get_staff_data()
        
        # Verify data processing - should convert UPPERCASE to lowercase keys
        assert len(result) == len(sample_staff_data)
        for i, staff in enumerate(result):
            # Verify UPPERCASE keys were converted to lowercase
            assert 'dcid' in staff
            assert 'DCID' not in staff
            assert staff['dcid'] == sample_staff_data[i]['DCID']
            
            assert 'last_name' in staff
            assert staff['last_name'] == sample_staff_data[i]['LAST_NAME']
            
            assert 'email' in staff
            assert staff['email'] == sample_staff_data[i]['EMAIL_ADDR']
            
            # Verify boolean conversion
            assert isinstance(staff['admin_access'], bool)
            assert isinstance(staff['teacher_access'], bool)
        
        assert "staff records from database" in caplog.text
    
    def test_get_staff_data_empty_result(self, mock_seton_utils, caplog):
        """Test handling of empty staff data result"""
        mock_seton_utils['cursor'].fetchall.return_value = []
        
        result = get_staff_data()
        
        assert result == []
        assert "0 staff records" in caplog.text


class TestGetEnrollmentData:
    """Test enrollment data retrieval with optional filtering"""
    
    def test_get_enrollment_data_all_schools(self, mock_seton_utils, sample_student_data, caplog):
        """Test enrollment data retrieval for all schools"""
        mock_seton_utils['cursor'].fetchall.return_value = sample_student_data
        
        result = get_enrollment_data()
        
        # Verify query executed without school filter
        query_call = mock_seton_utils['cursor'].execute.call_args
        assert query_call[0][1] == {}  # No parameters passed
        
        assert len(result) == len(sample_student_data)
    
    def test_get_enrollment_data_specific_school(self, mock_seton_utils, sample_student_data, caplog):
        """Test enrollment data retrieval for specific school"""
        school_id = 100
        mock_seton_utils['cursor'].fetchall.return_value = sample_student_data
        
        result = get_enrollment_data(school_id=school_id)
        
        # Verify query executed with school filter
        query_call = mock_seton_utils['cursor'].execute.call_args
        assert query_call[0][1] == {'school_id': school_id}
        
        assert len(result) == len(sample_student_data)
        assert f"school_id: {school_id}" in caplog.text


class TestDataValidationAndTransformation:
    """Test data validation and transformation functions"""
    
    def test_validate_and_transform_student_success(self):
        """Test successful student data validation and transformation"""
        raw_student = {
            'student_number': 12345,
            'dcid': 98765,
            'last_name': '  Smith  ',  # Whitespace to trim
            'first_name': '  John  ',
            'middle_name': None,
            'grade_level': '10',  # String that should convert to int
            'school_name': '  Test School  ',
            'web_password': ''  # Empty string should become None
        }
        
        result = validate_and_transform_student(raw_student)
        
        # Verify transformations
        assert result['grade_level'] == 10  # Converted to int
        assert result['last_name'] == 'Smith'  # Whitespace trimmed
        assert result['first_name'] == 'John'  # Whitespace trimmed
        assert result['school_name'] == 'Test School'  # Whitespace trimmed
        assert result['web_password'] is None  # Empty string converted to None
    
    def test_validate_and_transform_student_invalid_grade(self, caplog):
        """Test student validation with invalid grade level"""
        raw_student = {
            'student_number': 12345,
            'grade_level': 'invalid_grade'
        }
        
        result = validate_and_transform_student(raw_student)
        
        # Grade should remain as original value
        assert result['grade_level'] == 'invalid_grade'
        assert "Invalid grade level" in caplog.text
    
    def test_validate_and_transform_staff_success(self):
        """Test successful staff data validation and transformation"""
        raw_staff = {
            'dcid': 1001,
            'first_name': '  Sarah  ',
            'last_name': '  Wilson  ',
            'email': '  swilson@school.edu  ',
            'can_change_school': '0',  # String that should convert to bool
            'admin_access': 1,  # Int that should convert to bool
            'teacher_access': '1'  # String that should convert to bool
        }
        
        result = validate_and_transform_staff(raw_staff)
        
        # Verify transformations
        assert result['first_name'] == 'Sarah'  # Whitespace trimmed
        assert result['last_name'] == 'Wilson'  # Whitespace trimmed
        assert result['email'] == 'swilson@school.edu'  # Whitespace trimmed
        assert result['can_change_school'] is False  # Converted to bool
        assert result['admin_access'] is True  # Converted to bool
        assert result['teacher_access'] is True  # Converted to bool


class TestDatabaseConnectionTesting:
    """Test database connection testing utilities"""
    
    def test_connection_success(self, mock_seton_utils, caplog):
        """Test successful database connection test"""
        # Mock successful connection and test query
        mock_seton_utils['cursor'].fetchone.return_value = {'TEST': 1}  # UPPERCASE key!
        
        result = test_connection()
        
        assert result is True
        mock_seton_utils['connect_to_ps'].assert_called_once()
        mock_seton_utils['cursor'].execute.assert_called_with("SELECT 1 AS TEST FROM DUAL")
        assert "Database connection test successful" in caplog.text
    
    def test_connection_failure(self, mock_seton_utils, caplog):
        """Test database connection test failure"""
        # Mock connection failure
        mock_seton_utils['connect_to_ps'].side_effect = Exception("Connection failed")
        
        result = test_connection()
        
        assert result is False
        assert "Database connection test failed" in caplog.text
    
    def test_connection_unexpected_result(self, mock_seton_utils, caplog):
        """Test database connection test with unexpected result"""
        # Mock unexpected test result
        mock_seton_utils['cursor'].fetchone.return_value = {'TEST': 0}  # Wrong value
        
        result = test_connection()
        
        assert result is False
        assert "unexpected result" in caplog.text


@pytest.mark.database
class TestOracleColumnNamingPatterns:
    """Critical tests for Oracle column naming patterns"""
    
    def test_uppercase_column_access_pattern(self, mock_seton_utils):
        """Test the critical UPPERCASE column access pattern"""
        # This test validates the most important pattern in Seton packages
        sample_data = [
            {
                'STUDENT_NUMBER': 12345,  # UPPERCASE key from Oracle
                'LAST_NAME': 'Smith',     # UPPERCASE key from Oracle
                'FIRST_NAME': 'John',     # UPPERCASE key from Oracle
                'GRADE_LEVEL': 10         # UPPERCASE key from Oracle
            }
        ]
        
        mock_seton_utils['cursor'].fetchall.return_value = sample_data
        
        result = get_student_data()
        
        # Verify the critical pattern: Oracle UPPERCASE -> lowercase normalization
        student = result[0]
        assert 'student_number' in student  # Normalized to lowercase
        assert 'STUDENT_NUMBER' not in student  # Original UPPERCASE removed
        assert student['student_number'] == 12345
        
        assert 'last_name' in student
        assert 'LAST_NAME' not in student
        assert student['last_name'] == 'Smith'
    
    def test_missing_uppercase_key_handling(self, mock_seton_utils):
        """Test error when trying to access non-existent lowercase keys"""
        # This test demonstrates what happens with incorrect column naming
        sample_data = [
            {
                'STUDENT_NUMBER': 12345,  # Only UPPERCASE key exists
                # 'student_number': 12345  # lowercase key does NOT exist in Oracle
            }
        ]
        
        mock_seton_utils['cursor'].fetchall.return_value = sample_data
        
        # The get_student_data function should access with UPPERCASE keys
        # and normalize to lowercase in the result
        result = get_student_data()
        
        # Verify correct handling
        assert result[0]['student_number'] == 12345  # Accessible via normalized key
    
    def test_documentation_examples_accuracy(self, mock_seton_utils):
        """Test that documentation examples are accurate"""
        # Test data that matches the examples in docstrings
        oracle_result = [
            {
                'STUDENT_NUMBER': 12345,
                'DCID': 98765,
                'LAST_NAME': 'Smith',
                'RELATIONSHIP': 'Self'
            }
        ]
        
        mock_seton_utils['cursor'].fetchall.return_value = oracle_result
        
        result = get_student_data()
        
        # These should work (correct pattern from documentation)
        student_data = {
            'student_number': result[0]['student_number'],  # ✅ Correct
            'dcid': result[0]['dcid'],                      # ✅ Correct  
            'last_name': result[0]['last_name']             # ✅ Correct
        }
        
        assert student_data['student_number'] == 12345
        assert student_data['dcid'] == 98765
        assert student_data['last_name'] == 'Smith'


@pytest.mark.integration
class TestDatabaseIntegration:
    """Integration tests for database module"""
    
    def test_multiple_query_workflow(self, mock_seton_utils, sample_student_data, sample_staff_data):
        """Test workflow that uses multiple database queries"""
        # Setup mocks for multiple calls
        mock_seton_utils['cursor'].fetchall.side_effect = [
            sample_student_data,  # First call: students
            sample_staff_data     # Second call: staff
        ]
        
        # Execute multiple queries
        students = get_student_data()
        staff = get_staff_data()
        
        # Verify both queries executed
        assert len(students) == len(sample_student_data)
        assert len(staff) == len(sample_staff_data)
        
        # Verify connection was used multiple times
        assert mock_seton_utils['connect_to_ps'].call_count == 2
    
    def test_error_recovery_workflow(self, mock_seton_utils, sample_student_data):
        """Test error recovery in multi-step workflow"""
        # First call succeeds, second call fails
        mock_seton_utils['cursor'].fetchall.side_effect = [
            sample_student_data,  # Students succeed
            Exception("Staff query failed")  # Staff query fails
        ]
        
        # First query should succeed
        students = get_student_data()
        assert len(students) == len(sample_student_data)
        
        # Second query should fail gracefully
        with pytest.raises(DatabaseError):
            get_staff_data()
