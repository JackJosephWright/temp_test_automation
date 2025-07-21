"""
Helper utilities for Seton packages

This module provides common utility functions used across Seton packages
including data formatting, validation, transformation, and processing helpers.

Key Functions:
- format_data_for_sheets: Convert data to Google Sheets format
- validate_data_integrity: Validate data consistency and quality
- sanitize_data: Clean and normalize data
- generate_summary_stats: Create data summaries

Usage:
    from seton_package_template.utils.helpers import format_data_for_sheets
    
    formatted_data = format_data_for_sheets(raw_data)
"""

import re
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Union, Tuple
import pandas as pd

from ..config.logging_config import get_logger

# Initialize logger
logger = get_logger(__name__)


def format_data_for_sheets(data: List[Dict[str, Any]], 
                          include_headers: bool = True) -> List[List[Any]]:
    """
    Format data for Google Sheets upload
    
    Converts list of dictionaries to list of lists format required by
    Google Sheets API, with proper handling of None values and data types.
    
    Args:
        data: List of dictionaries to format
        include_headers: Whether to include header row
        
    Returns:
        List[List[Any]]: Formatted data ready for Google Sheets
        
    Example:
        students = [
            {'name': 'John', 'grade': 10, 'score': 95.5},
            {'name': 'Jane', 'grade': 11, 'score': None}
        ]
        formatted = format_data_for_sheets(students)
        # [['name', 'grade', 'score'], ['John', 10, 95.5], ['Jane', 11, '']]
    """
    if not data:
        logger.warning("⚠️ No data provided for formatting")
        return []
    
    logger.info(f"📝 Formatting {len(data)} records for Google Sheets")
    
    # Get headers from first record
    headers = list(data[0].keys())
    
    # Start with headers if requested
    formatted_data = []
    if include_headers:
        formatted_data.append(headers)
    
    # Process each record
    for record in data:
        row = []
        for header in headers:
            value = record.get(header)
            formatted_value = _format_value_for_sheets(value)
            row.append(formatted_value)
        formatted_data.append(row)
    
    logger.info(f"✅ Formatted {len(formatted_data)} rows for Google Sheets")
    return formatted_data


def _format_value_for_sheets(value: Any) -> Any:
    """
    Format individual value for Google Sheets
    
    Args:
        value: Value to format
        
    Returns:
        Any: Formatted value suitable for Google Sheets
    """
    if value is None:
        return ""
    
    # Handle datetime objects
    if isinstance(value, (datetime, date)):
        return value.strftime("%Y-%m-%d %H:%M:%S") if isinstance(value, datetime) else value.strftime("%Y-%m-%d")
    
    # Handle boolean values
    if isinstance(value, bool):
        return "Yes" if value else "No"
    
    # Handle numeric values
    if isinstance(value, (int, float)):
        return value
    
    # Convert everything else to string and strip whitespace
    return str(value).strip()


def validate_data_integrity(student_data: List[Dict[str, Any]], 
                          staff_data: List[Dict[str, Any]]) -> bool:
    """
    Validate data integrity and consistency
    
    Performs comprehensive validation on student and staff data to ensure
    data quality before uploading to Google Sheets.
    
    Args:
        student_data: List of student records
        staff_data: List of staff records
        
    Returns:
        bool: True if validation passes, False otherwise
        
    Validation Checks:
    - Required fields present
    - Data type consistency
    - Value range validation
    - Duplicate detection
    - Cross-reference validation
    """
    logger.info("🔍 Validating data integrity")
    
    validation_passed = True
    issues = []
    
    # Validate student data
    student_issues = _validate_student_data(student_data)
    if student_issues:
        issues.extend(student_issues)
        validation_passed = False
    
    # Validate staff data
    staff_issues = _validate_staff_data(staff_data)
    if staff_issues:
        issues.extend(staff_issues)
        validation_passed = False
    
    # Cross-reference validation
    cross_ref_issues = _validate_cross_references(student_data, staff_data)
    if cross_ref_issues:
        issues.extend(cross_ref_issues)
        validation_passed = False
    
    # Log results
    if validation_passed:
        logger.info("✅ Data integrity validation passed")
    else:
        logger.error("❌ Data integrity validation failed:")
        for issue in issues:
            logger.error(f"   - {issue}")
    
    return validation_passed


def _validate_student_data(data: List[Dict[str, Any]]) -> List[str]:
    """Validate student data specific requirements"""
    issues = []
    
    if not data:
        issues.append("No student data provided")
        return issues
    
    # Required fields for students
    required_fields = ['student_number', 'dcid', 'last_name', 'first_name', 'grade_level']
    
    for i, student in enumerate(data):
        # Check required fields
        for field in required_fields:
            if field not in student or student[field] is None or student[field] == '':
                issues.append(f"Student {i+1}: Missing required field '{field}'")
        
        # Validate student number
        if 'student_number' in student:
            if not isinstance(student['student_number'], (int, str)) or str(student['student_number']).strip() == '':
                issues.append(f"Student {i+1}: Invalid student number")
        
        # Validate grade level
        if 'grade_level' in student:
            try:
                grade = int(student['grade_level'])
                if grade < -2 or grade > 12:  # Allow Pre-K (-2) through 12
                    issues.append(f"Student {i+1}: Invalid grade level: {grade}")
            except (ValueError, TypeError):
                issues.append(f"Student {i+1}: Grade level must be a number")
        
        # Validate email format if present
        if 'email' in student and student['email']:
            if not _is_valid_email(student['email']):
                issues.append(f"Student {i+1}: Invalid email format")
    
    # Check for duplicate student numbers
    student_numbers = [s.get('student_number') for s in data if s.get('student_number')]
    duplicates = _find_duplicates(student_numbers)
    if duplicates:
        issues.append(f"Duplicate student numbers found: {duplicates}")
    
    return issues


def _validate_staff_data(data: List[Dict[str, Any]]) -> List[str]:
    """Validate staff data specific requirements"""
    issues = []
    
    if not data:
        issues.append("No staff data provided")
        return issues
    
    # Required fields for staff
    required_fields = ['dcid', 'last_name', 'first_name']
    
    for i, staff in enumerate(data):
        # Check required fields
        for field in required_fields:
            if field not in staff or staff[field] is None or staff[field] == '':
                issues.append(f"Staff {i+1}: Missing required field '{field}'")
        
        # Validate email format if present
        if 'email' in staff and staff['email']:
            if not _is_valid_email(staff['email']):
                issues.append(f"Staff {i+1}: Invalid email format")
        
        # Validate boolean fields
        boolean_fields = ['admin_access', 'teacher_access', 'can_change_school']
        for field in boolean_fields:
            if field in staff and staff[field] is not None:
                if not isinstance(staff[field], bool):
                    try:
                        # Try to convert to boolean
                        staff[field] = bool(staff[field])
                    except:
                        issues.append(f"Staff {i+1}: Invalid boolean value for '{field}'")
    
    # Check for duplicate DCIDs
    dcids = [s.get('dcid') for s in data if s.get('dcid')]
    duplicates = _find_duplicates(dcids)
    if duplicates:
        issues.append(f"Duplicate staff DCIDs found: {duplicates}")
    
    return issues


def _validate_cross_references(student_data: List[Dict[str, Any]], 
                              staff_data: List[Dict[str, Any]]) -> List[str]:
    """Validate cross-references between student and staff data"""
    issues = []
    
    # Get unique school IDs from both datasets
    student_schools = {s.get('school_id') for s in student_data if s.get('school_id')}
    staff_schools = {s.get('school_id') for s in staff_data if s.get('school_id')}
    
    # Check for schools with students but no staff
    students_only_schools = student_schools - staff_schools
    if students_only_schools:
        issues.append(f"Schools with students but no staff: {students_only_schools}")
    
    return issues


def _is_valid_email(email: str) -> bool:
    """Validate email format"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, str(email)) is not None


def _find_duplicates(items: List[Any]) -> List[Any]:
    """Find duplicate items in a list"""
    seen = set()
    duplicates = set()
    
    for item in items:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    
    return list(duplicates)


def sanitize_data(data: List[Dict[str, Any]], 
                 remove_empty_strings: bool = True,
                 trim_whitespace: bool = True) -> List[Dict[str, Any]]:
    """
    Sanitize data by cleaning and normalizing values
    
    Args:
        data: Data to sanitize
        remove_empty_strings: Replace empty strings with None
        trim_whitespace: Strip whitespace from string values
        
    Returns:
        List[Dict[str, Any]]: Sanitized data
    """
    logger.info(f"🧹 Sanitizing {len(data)} records")
    
    sanitized_data = []
    
    for record in data:
        sanitized_record = {}
        
        for key, value in record.items():
            # Handle string values
            if isinstance(value, str):
                if trim_whitespace:
                    value = value.strip()
                if remove_empty_strings and value == '':
                    value = None
            
            sanitized_record[key] = value
        
        sanitized_data.append(sanitized_record)
    
    logger.info(f"✅ Sanitized {len(sanitized_data)} records")
    return sanitized_data


def generate_summary_stats(student_data: List[Dict[str, Any]], 
                          staff_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate summary statistics about the data
    
    Args:
        student_data: Student records
        staff_data: Staff records
        
    Returns:
        Dict[str, Any]: Summary statistics
    """
    logger.info("📊 Generating summary statistics")
    
    summary = {
        'timestamp': datetime.now().isoformat(),
        'total_students': len(student_data),
        'total_staff': len(staff_data)
    }
    
    if student_data:
        # Student statistics
        grades = [s.get('grade_level') for s in student_data if s.get('grade_level') is not None]
        schools = [s.get('school_id') for s in student_data if s.get('school_id')]
        
        summary.update({
            'student_grade_range': f"{min(grades)} - {max(grades)}" if grades else "N/A",
            'unique_student_schools': len(set(schools)),
            'students_by_grade': _count_by_field(student_data, 'grade_level'),
            'students_by_school': _count_by_field(student_data, 'school_id')
        })
    
    if staff_data:
        # Staff statistics  
        staff_schools = [s.get('school_id') for s in staff_data if s.get('school_id')]
        
        summary.update({
            'unique_staff_schools': len(set(staff_schools)),
            'staff_by_school': _count_by_field(staff_data, 'school_id'),
            'admin_count': len([s for s in staff_data if s.get('admin_access')]),
            'teacher_count': len([s for s in staff_data if s.get('teacher_access')])
        })
    
    logger.info(f"✅ Generated summary with {len(summary)} metrics")
    return summary


def _count_by_field(data: List[Dict[str, Any]], field: str) -> Dict[str, int]:
    """Count occurrences of values in a specific field"""
    counts = {}
    for record in data:
        value = record.get(field)
        if value is not None:
            value_str = str(value)
            counts[value_str] = counts.get(value_str, 0) + 1
    return counts


def convert_to_dataframe(data: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Convert data to pandas DataFrame for analysis
    
    Args:
        data: List of dictionaries to convert
        
    Returns:
        pd.DataFrame: DataFrame representation of the data
    """
    if not data:
        return pd.DataFrame()
    
    logger.info(f"📊 Converting {len(data)} records to DataFrame")
    df = pd.DataFrame(data)
    logger.info(f"✅ Created DataFrame with shape {df.shape}")
    return df


def export_to_csv(data: List[Dict[str, Any]], filename: str, 
                 include_timestamp: bool = True) -> str:
    """
    Export data to CSV file
    
    Args:
        data: Data to export
        filename: Base filename (without extension)
        include_timestamp: Whether to include timestamp in filename
        
    Returns:
        str: Final filename used
    """
    if include_timestamp:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_filename = f"{filename}_{timestamp}.csv"
    else:
        final_filename = f"{filename}.csv"
    
    logger.info(f"💾 Exporting {len(data)} records to {final_filename}")
    
    df = convert_to_dataframe(data)
    df.to_csv(final_filename, index=False)
    
    logger.info(f"✅ Exported data to {final_filename}")
    return final_filename


def mask_sensitive_data(data: List[Dict[str, Any]], 
                       sensitive_fields: List[str] = None) -> List[Dict[str, Any]]:
    """
    Mask sensitive data fields for logging/debugging
    
    Args:
        data: Data to mask
        sensitive_fields: List of field names to mask
        
    Returns:
        List[Dict[str, Any]]: Data with sensitive fields masked
    """
    if sensitive_fields is None:
        sensitive_fields = ['password', 'ssn', 'social_security', 'web_password']
    
    masked_data = []
    
    for record in data:
        masked_record = record.copy()
        for field in sensitive_fields:
            if field in masked_record and masked_record[field]:
                masked_record[field] = "***MASKED***"
        masked_data.append(masked_record)
    
    return masked_data


def chunk_data(data: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split data into chunks for batch processing
    
    Args:
        data: Data to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List[List[Any]]: List of data chunks
        
    Example:
        chunks = chunk_data(large_dataset, 100)
        for chunk in chunks:
            process_chunk(chunk)
    """
    chunks = []
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]
        chunks.append(chunk)
    
    logger.info(f"📦 Split {len(data)} items into {len(chunks)} chunks of size {chunk_size}")
    return chunks
