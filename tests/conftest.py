"""
Pytest configuration and fixtures for Seton package tests

This module provides common fixtures and configuration for testing
Seton packages, including mock database connections, sample data,
and Google Sheets mocking.

Key Fixtures:
- mock_db_connection: Mock Oracle database connection
- sample_student_data: Sample student records with UPPERCASE keys
- sample_staff_data: Sample staff records with UPPERCASE keys
- mock_sheets_manager: Mock Google Sheets manager
- mock_environment: Mock environment configuration

Usage:
    def test_something(sample_student_data):
        assert len(sample_student_data) > 0
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any
from datetime import datetime, date


@pytest.fixture
def sample_student_data() -> List[Dict[str, Any]]:
    """
    Sample student data with UPPERCASE column names (Oracle pattern)
    
    CRITICAL: This fixture demonstrates the Oracle column naming pattern.
    All keys are UPPERCASE as they would be returned from Oracle queries.
    """
    return [
        {
            'STUDENT_NUMBER': 12345,
            'DCID': 98765,
            'LAST_NAME': 'Smith',
            'FIRST_NAME': 'John',
            'MIDDLE_NAME': 'Michael',
            'GRADE_LEVEL': 10,
            'ENROLL_STATUS': 0,
            'ENTRYDATE': date(2023, 8, 15),
            'EXITDATE': None,
            'SCHOOLID': 100,
            'SCHOOL_NAME': 'Main High School',
            'HOME_ROOM': 'A101',
            'GENDER': 'M',
            'DOB': date(2008, 3, 15),
            'STUDENT_WEB_ID': 'jsmith12345',
            'STUDENT_WEB_PASSWORD': 'temp123'
        },
        {
            'STUDENT_NUMBER': 67890,
            'DCID': 54321,
            'LAST_NAME': 'Jones',
            'FIRST_NAME': 'Jane',
            'MIDDLE_NAME': 'Elizabeth',
            'GRADE_LEVEL': 11,
            'ENROLL_STATUS': 0,
            'ENTRYDATE': date(2022, 8, 20),
            'EXITDATE': None,
            'SCHOOLID': 100,
            'SCHOOL_NAME': 'Main High School',
            'HOME_ROOM': 'B205',
            'GENDER': 'F',
            'DOB': date(2007, 7, 22),
            'STUDENT_WEB_ID': 'jjones67890',
            'STUDENT_WEB_PASSWORD': 'temp456'
        },
        {
            'STUDENT_NUMBER': 11111,
            'DCID': 22222,
            'LAST_NAME': 'Brown',
            'FIRST_NAME': 'Michael',
            'MIDDLE_NAME': None,
            'GRADE_LEVEL': 9,
            'ENROLL_STATUS': 0,
            'ENTRYDATE': date(2024, 8, 25),
            'EXITDATE': None,
            'SCHOOLID': 200,
            'SCHOOL_NAME': 'East Elementary',
            'HOME_ROOM': 'C305',
            'GENDER': 'M',
            'DOB': date(2009, 12, 5),
            'STUDENT_WEB_ID': 'mbrown11111',
            'STUDENT_WEB_PASSWORD': None
        }
    ]


@pytest.fixture
def sample_staff_data() -> List[Dict[str, Any]]:
    """
    Sample staff data with UPPERCASE column names (Oracle pattern)
    """
    return [
        {
            'DCID': 1001,
            'LASTFIRST': 'Wilson, Sarah',
            'FIRST_NAME': 'Sarah',
            'LAST_NAME': 'Wilson',
            'EMAIL_ADDR': 'swilson@school.edu',
            'SCHOOLID': 100,
            'SCHOOL_NAME': 'Main High School',
            'TITLE': 'Mathematics Teacher',
            'PHONE': '555-1234',
            'CANCHANGESCHOOL': 0,
            'ADMIN_ACCESS': 0,
            'TEACHER_ACCESS': 1
        },
        {
            'DCID': 1002,
            'LASTFIRST': 'Johnson, David',
            'FIRST_NAME': 'David',
            'LAST_NAME': 'Johnson',
            'EMAIL_ADDR': 'djohnson@school.edu',
            'SCHOOLID': 100,
            'SCHOOL_NAME': 'Main High School',
            'TITLE': 'Principal',
            'PHONE': '555-5678',
            'CANCHANGESCHOOL': 1,
            'ADMIN_ACCESS': 1,
            'TEACHER_ACCESS': 1
        },
        {
            'DCID': 1003,
            'LASTFIRST': 'Davis, Mary',
            'FIRST_NAME': 'Mary',
            'LAST_NAME': 'Davis',
            'EMAIL_ADDR': 'mdavis@school.edu',
            'SCHOOLID': 200,
            'SCHOOL_NAME': 'East Elementary',
            'TITLE': 'Elementary Teacher',
            'PHONE': '555-9012',
            'CANCHANGESCHOOL': 0,
            'ADMIN_ACCESS': 0,
            'TEACHER_ACCESS': 1
        }
    ]


@pytest.fixture
def processed_student_data() -> List[Dict[str, Any]]:
    """
    Sample student data after processing (lowercase keys)
    
    This represents how data looks after being processed by the
    database query functions that normalize Oracle's UPPERCASE keys.
    """
    return [
        {
            'student_number': 12345,
            'dcid': 98765,
            'last_name': 'Smith',
            'first_name': 'John',
            'middle_name': 'Michael',
            'grade_level': 10,
            'enroll_status': 0,
            'entry_date': date(2023, 8, 15),
            'exit_date': None,
            'school_id': 100,
            'school_name': 'Main High School',
            'home_room': 'A101',
            'gender': 'M',
            'date_of_birth': date(2008, 3, 15),
            'web_id': 'jsmith12345',
            'web_password': 'temp123'
        },
        {
            'student_number': 67890,
            'dcid': 54321,
            'last_name': 'Jones',
            'first_name': 'Jane',
            'middle_name': 'Elizabeth',
            'grade_level': 11,
            'enroll_status': 0,
            'entry_date': date(2022, 8, 20),
            'exit_date': None,
            'school_id': 100,
            'school_name': 'Main High School',
            'home_room': 'B205',
            'gender': 'F',
            'date_of_birth': date(2007, 7, 22),
            'web_id': 'jjones67890',
            'web_password': 'temp456'
        }
    ]


@pytest.fixture
def processed_staff_data() -> List[Dict[str, Any]]:
    """
    Sample staff data after processing (lowercase keys)
    """
    return [
        {
            'dcid': 1001,
            'lastfirst': 'Wilson, Sarah',
            'first_name': 'Sarah',
            'last_name': 'Wilson',
            'email': 'swilson@school.edu',
            'school_id': 100,
            'school_name': 'Main High School',
            'title': 'Mathematics Teacher',
            'phone': '555-1234',
            'can_change_school': False,
            'admin_access': False,
            'teacher_access': True
        },
        {
            'dcid': 1002,
            'lastfirst': 'Johnson, David',
            'first_name': 'David',
            'last_name': 'Johnson',
            'email': 'djohnson@school.edu',
            'school_id': 100,
            'school_name': 'Main High School',
            'title': 'Principal',
            'phone': '555-5678',
            'can_change_school': True,
            'admin_access': True,
            'teacher_access': True
        }
    ]


@pytest.fixture
def mock_db_connection():
    """
    Mock database connection that returns sample data with UPPERCASE keys
    
    This fixture mocks the Oracle database connection and cursor,
    ensuring that test data follows the critical UPPERCASE column pattern.
    """
    mock_connection = Mock()
    mock_cursor = Mock()
    
    # Mock cursor methods
    mock_cursor.fetchall.return_value = []
    mock_cursor.fetchone.return_value = {'TEST': 1}  # UPPERCASE key!
    mock_cursor.execute.return_value = None
    mock_cursor.close.return_value = None
    
    # Mock connection methods
    mock_connection.cursor.return_value = mock_cursor
    mock_connection.close.return_value = None
    
    return mock_connection


@pytest.fixture
def mock_seton_utils():
    """Mock seton_utils modules"""
    with patch('seton_utils.connect_to_ps.connect_to_ps') as mock_connect, \
         patch('seton_utils.gdrive.gdrive_helpers.get_gdrive_credentials') as mock_creds:
        
        # Mock database connection
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        # Mock Google credentials
        mock_creds.return_value = Mock()
        
        yield {
            'connect_to_ps': mock_connect,
            'get_gdrive_credentials': mock_creds,
            'connection': mock_conn,
            'cursor': mock_cursor
        }


@pytest.fixture
def mock_sheets_manager():
    """Mock Google Sheets manager"""
    mock_manager = Mock()
    
    # Mock worksheet operations
    mock_worksheet = Mock()
    mock_manager.get_worksheet.return_value = mock_worksheet
    mock_manager.update_worksheet.return_value = None
    mock_manager.validate_upload.return_value = True
    mock_manager.list_worksheets.return_value = ['Sheet1', 'Students', 'Staff']
    
    return mock_manager


@pytest.fixture
def mock_environment_settings():
    """Mock environment settings for testing"""
    with patch('seton_package_template.config.settings.get_environment') as mock_env, \
         patch('seton_package_template.config.settings.get_sheet_id') as mock_sheet, \
         patch('seton_package_template.config.settings.validate_environment_sheet_access') as mock_validate:
        
        mock_env.return_value = 'testing'
        mock_sheet.return_value = 'test_sheet_id_12345'
        mock_validate.return_value = None
        
        yield {
            'environment': 'testing',
            'sheet_id': 'test_sheet_id_12345'
        }


@pytest.fixture
def sample_sheets_data() -> List[List[Any]]:
    """Sample data formatted for Google Sheets (list of lists)"""
    return [
        ['student_number', 'last_name', 'first_name', 'grade_level'],
        [12345, 'Smith', 'John', 10],
        [67890, 'Jones', 'Jane', 11],
        [11111, 'Brown', 'Michael', 9]
    ]


@pytest.fixture
def invalid_student_data() -> List[Dict[str, Any]]:
    """Sample invalid student data for testing validation"""
    return [
        {
            # Missing required fields
            'STUDENT_NUMBER': None,
            'LAST_NAME': '',
            'GRADE_LEVEL': 'invalid'
        },
        {
            # Invalid data types
            'STUDENT_NUMBER': 'not_a_number',
            'GRADE_LEVEL': 25,  # Invalid grade
            'EMAIL': 'invalid_email'
        }
    ]


@pytest.fixture
def mock_airflow_environment():
    """Mock Airflow environment variables and imports"""
    with patch.dict('os.environ', {
        'AIRFLOW_HOME': '/opt/airflow',
        'AIRFLOW__CORE__DAGS_FOLDER': '/opt/airflow/dags'
    }):
        # Mock Airflow Variable import
        with patch('seton_package_template.config.settings.AIRFLOW_AVAILABLE', True), \
             patch('seton_package_template.config.settings.Variable') as mock_variable:
            
            mock_variable.get.return_value = 'mocked_value'
            yield mock_variable


@pytest.fixture
def mock_local_environment():
    """Mock local development environment"""
    with patch.dict('os.environ', {
        'ENVIRONMENT': 'development',
        'GOOGLE_SHEET_ID_DEV': 'dev_sheet_123',
        'GOOGLE_CREDENTIALS_PATH': '/path/to/creds.json'
    }, clear=True):
        # Ensure Airflow is not available
        with patch('seton_package_template.config.settings.AIRFLOW_AVAILABLE', False):
            yield


@pytest.fixture(autouse=True)
def reset_logging():
    """Reset logging configuration before each test"""
    import logging
    # Clear any existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    # Reset log level
    logging.root.setLevel(logging.WARNING)


@pytest.fixture
def capture_logs(caplog):
    """Capture logs for testing"""
    import logging
    caplog.set_level(logging.INFO)
    return caplog


# Pytest configuration
def pytest_configure(config):
    """Pytest configuration"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "database: marks tests that require database connection"
    )
    config.addinivalue_line(
        "markers", "sheets: marks tests that require Google Sheets access"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location"""
    for item in items:
        # Add markers based on test file location
        if "test_database" in str(item.fspath):
            item.add_marker(pytest.mark.database)
        elif "test_google_sheets" in str(item.fspath):
            item.add_marker(pytest.mark.sheets)
        
        # Add unit marker to most tests by default
        if not any(mark.name in ['integration', 'slow'] for mark in item.iter_markers()):
            item.add_marker(pytest.mark.unit)
