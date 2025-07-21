"""
Database queries for Seton package template

This module demonstrates the critical patterns for Oracle database integration
in Seton packages, with special attention to Oracle's UPPERCASE column naming.

CRITICAL PATTERN: Oracle Column Naming
Oracle returns ALL column names in UPPERCASE. This is the most common source
of bugs in Seton packages. Always use uppercase keys when accessing results.

Examples:
    ✅ CORRECT: row['STUDENT_NUMBER']
    ❌ WRONG:   row['student_number']  # Will cause KeyError!

Standard Patterns Demonstrated:
1. Oracle database connection using seton_utils
2. Proper column naming handling (UPPERCASE!)
3. Error handling and logging
4. Data type conversion and validation
5. Connection management

Usage:
    from seton_package_template.database.queries import get_student_data
    
    students = get_student_data()
    for student in students:
        print(student['student_number'])  # Normalized to lowercase
"""

from typing import List, Dict, Any, Optional

# Handle Oracle import gracefully (modern oracledb driver)
try:
    import oracledb
    ORACLE_AVAILABLE = True
except ImportError:
    logger = None  # Will be set below
    ORACLE_AVAILABLE = False

from seton_utils.connect_to_ps import connect_to_ps
from ..config.logging_config import get_logger, log_performance

# Initialize logger
logger = get_logger(__name__)

if not ORACLE_AVAILABLE:
    logger.warning("⚠️ oracledb not available - Oracle database features disabled")
    logger.info("💡 To enable Oracle features, install oracledb: pip install oracledb")


def get_student_data() -> List[Dict[str, Any]]:
    """
    Retrieve student data from Oracle database
    
    This function demonstrates the standard pattern for Oracle queries
    in Seton packages, including proper column naming handling.
    
    Returns:
        List[Dict[str, Any]]: List of student records with normalized keys
        
    Raises:
        DatabaseError: If database operation fails
        ImportError: If cx_Oracle is not available
        
    Example:
        students = get_student_data()
        for student in students:
            print(f"Student: {student['student_number']} - {student['last_name']}")
            
    CRITICAL: Oracle returns UPPERCASE column names!
    """
    if not ORACLE_AVAILABLE:
        raise ImportError(
            "oracledb is not installed. Install it with: pip install oracledb\n"
            "Note: oracledb is the modern Oracle driver (replaces cx_Oracle)"
        )
    
    logger.info("🎓 Fetching student data from Oracle database")
    
    conn = None
    cursor = None
    
    try:
        # Connect to PowerSchool Oracle database
        with log_performance(logger, "database_connection"):
            conn = connect_to_ps()
            cursor = conn.cursor()
        
        # SQL Query - note that Oracle will return UPPERCASE column names
        query = """
        SELECT 
            s.STUDENT_NUMBER,
            s.DCID,
            s.LAST_NAME,
            s.FIRST_NAME,
            s.MIDDLE_NAME,
            s.GRADE_LEVEL,
            s.ENROLL_STATUS,
            s.ENTRYDATE,
            s.EXITDATE,
            s.SCHOOLID,
            sch.NAME AS SCHOOL_NAME,
            s.HOME_ROOM,
            s.GENDER,
            s.DOB,
            s.STUDENT_WEB_ID,
            s.STUDENT_WEB_PASSWORD
        FROM STUDENTS s
        LEFT JOIN SCHOOLS sch ON s.SCHOOLID = sch.SCHOOL_NUMBER
        WHERE s.ENROLL_STATUS = 0  -- Active students only
        ORDER BY s.LAST_NAME, s.FIRST_NAME
        """
        
        logger.debug(f"Executing query: {query}")
        
        with log_performance(logger, "student_query"):
            cursor.execute(query)
            rows = cursor.fetchall()
        
        logger.info(f"Retrieved {len(rows)} student records from database")
        
        # Process results with UPPERCASE column handling
        students = []
        for row in rows:
            # CRITICAL: Oracle returns UPPERCASE column names!
            # We access with UPPERCASE keys and normalize to lowercase
            student = {
                'student_number': row['STUDENT_NUMBER'],        # Note: UPPERCASE key!
                'dcid': row['DCID'],                           # Note: UPPERCASE key!
                'last_name': row['LAST_NAME'],                 # Note: UPPERCASE key!
                'first_name': row['FIRST_NAME'],               # Note: UPPERCASE key!
                'middle_name': row['MIDDLE_NAME'],             # Note: UPPERCASE key!
                'grade_level': row['GRADE_LEVEL'],             # Note: UPPERCASE key!
                'enroll_status': row['ENROLL_STATUS'],         # Note: UPPERCASE key!
                'entry_date': row['ENTRYDATE'],                # Note: UPPERCASE key!
                'exit_date': row['EXITDATE'],                  # Note: UPPERCASE key!
                'school_id': row['SCHOOLID'],                  # Note: UPPERCASE key!
                'school_name': row['SCHOOL_NAME'],             # Note: UPPERCASE key!
                'home_room': row['HOME_ROOM'],                 # Note: UPPERCASE key!
                'gender': row['GENDER'],                       # Note: UPPERCASE key!
                'date_of_birth': row['DOB'],                   # Note: UPPERCASE key!
                'web_id': row['STUDENT_WEB_ID'],               # Note: UPPERCASE key!
                'web_password': row['STUDENT_WEB_PASSWORD']    # Note: UPPERCASE key!
            }
            
            # Data validation and transformation
            student = validate_and_transform_student(student)
            students.append(student)
        
        logger.info(f"✅ Successfully processed {len(students)} student records")
        return students
        
    except oracledb.Error as e:
        logger.error(f"❌ Oracle database error: {e}")
        raise DatabaseError(f"Failed to retrieve student data: {e}")
    except Exception as e:
        logger.error(f"❌ Unexpected error retrieving student data: {e}")
        raise DatabaseError(f"Unexpected error: {e}")
    finally:
        # Always close database connections
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        logger.debug("🔒 Database connection closed")


def get_staff_data() -> List[Dict[str, Any]]:
    """
    Retrieve staff data from Oracle database
    
    Returns:
        List[Dict[str, Any]]: List of staff records with normalized keys
        
    Example:
        staff = get_staff_data()
        for person in staff:
            print(f"Staff: {person['last_name']}, {person['first_name']}")
    """
    logger.info("👥 Fetching staff data from Oracle database")
    
    conn = None
    cursor = None
    
    try:
        with log_performance(logger, "database_connection"):
            conn = connect_to_ps()
            cursor = conn.cursor()
        
        # SQL Query for staff data
        query = """
        SELECT 
            u.DCID,
            u.LASTFIRST,
            u.FIRST_NAME,
            u.LAST_NAME,
            u.EMAIL_ADDR,
            u.SCHOOLID,
            sch.NAME AS SCHOOL_NAME,
            u.TITLE,
            u.PHONE,
            u.CANCHANGESCHOOL,
            u.ADMIN_ACCESS,
            u.TEACHER_ACCESS
        FROM USERS u
        LEFT JOIN SCHOOLS sch ON u.SCHOOLID = sch.SCHOOL_NUMBER
        WHERE u.ACTIVE = 1  -- Active staff only
        ORDER BY u.LAST_NAME, u.FIRST_NAME
        """
        
        with log_performance(logger, "staff_query"):
            cursor.execute(query)
            rows = cursor.fetchall()
        
        logger.info(f"Retrieved {len(rows)} staff records from database")
        
        # Process results with UPPERCASE column handling
        staff = []
        for row in rows:
            # CRITICAL: Oracle returns UPPERCASE column names!
            person = {
                'dcid': row['DCID'],                           # Note: UPPERCASE key!
                'lastfirst': row['LASTFIRST'],                 # Note: UPPERCASE key!
                'first_name': row['FIRST_NAME'],               # Note: UPPERCASE key!
                'last_name': row['LAST_NAME'],                 # Note: UPPERCASE key!
                'email': row['EMAIL_ADDR'],                    # Note: UPPERCASE key!
                'school_id': row['SCHOOLID'],                  # Note: UPPERCASE key!
                'school_name': row['SCHOOL_NAME'],             # Note: UPPERCASE key!
                'title': row['TITLE'],                         # Note: UPPERCASE key!
                'phone': row['PHONE'],                         # Note: UPPERCASE key!
                'can_change_school': row['CANCHANGESCHOOL'],   # Note: UPPERCASE key!
                'admin_access': row['ADMIN_ACCESS'],           # Note: UPPERCASE key!
                'teacher_access': row['TEACHER_ACCESS']        # Note: UPPERCASE key!
            }
            
            # Data validation and transformation
            person = validate_and_transform_staff(person)
            staff.append(person)
        
        logger.info(f"✅ Successfully processed {len(staff)} staff records")
        return staff
        
    except oracledb.Error as e:
        logger.error(f"❌ Oracle database error: {e}")
        raise DatabaseError(f"Failed to retrieve staff data: {e}")
    except Exception as e:
        logger.error(f"❌ Unexpected error retrieving staff data: {e}")
        raise DatabaseError(f"Unexpected error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        logger.debug("🔒 Database connection closed")


def get_enrollment_data(school_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Retrieve enrollment data with optional school filtering
    
    Args:
        school_id: Optional school ID to filter by
        
    Returns:
        List[Dict[str, Any]]: List of enrollment records
        
    Example:
        # All schools
        enrollments = get_enrollment_data()
        
        # Specific school
        enrollments = get_enrollment_data(school_id=100)
    """
    logger.info(f"📊 Fetching enrollment data (school_id: {school_id})")
    
    conn = None
    cursor = None
    
    try:
        with log_performance(logger, "database_connection"):
            conn = connect_to_ps()
            cursor = conn.cursor()
        
        # Build query with optional school filter
        base_query = """
        SELECT 
            s.STUDENT_NUMBER,
            s.DCID,
            s.LAST_NAME,
            s.FIRST_NAME,
            s.GRADE_LEVEL,
            s.SCHOOLID,
            sch.NAME AS SCHOOL_NAME,
            s.ENROLL_STATUS,
            s.ENTRYDATE,
            s.EXITDATE
        FROM STUDENTS s
        LEFT JOIN SCHOOLS sch ON s.SCHOOLID = sch.SCHOOL_NUMBER
        WHERE s.ENROLL_STATUS = 0
        LIMIT 100
        """
        
        if school_id:
            query = base_query + " AND s.SCHOOLID = :school_id"
            params = {'school_id': school_id}
        else:
            query = base_query
            params = {}
        
        query += " ORDER BY s.SCHOOLID, s.GRADE_LEVEL, s.LAST_NAME"
        
        with log_performance(logger, "enrollment_query"):
            cursor.execute(query, params)
            rows = cursor.fetchall()
        
        logger.info(f"Retrieved {len(rows)} enrollment records")
        
        # Process results with UPPERCASE column handling
        enrollments = []
        for row in rows:
            # CRITICAL: Oracle returns UPPERCASE column names!
            enrollment = {
                'student_number': row['STUDENT_NUMBER'],       # Note: UPPERCASE key!
                'dcid': row['DCID'],                          # Note: UPPERCASE key!
                'last_name': row['LAST_NAME'],                # Note: UPPERCASE key!
                'first_name': row['FIRST_NAME'],              # Note: UPPERCASE key!
                'grade_level': row['GRADE_LEVEL'],            # Note: UPPERCASE key!
                'school_id': row['SCHOOLID'],                 # Note: UPPERCASE key!
                'school_name': row['SCHOOL_NAME'],            # Note: UPPERCASE key!
                'enroll_status': row['ENROLL_STATUS'],        # Note: UPPERCASE key!
                'entry_date': row['ENTRYDATE'],               # Note: UPPERCASE key!
                'exit_date': row['EXITDATE']                  # Note: UPPERCASE key!
            }
            
            enrollment = validate_and_transform_enrollment(enrollment)
            enrollments.append(enrollment)
        
        logger.info(f"✅ Successfully processed {len(enrollments)} enrollment records")
        return enrollments
        
    except oracledb.Error as e:
        logger.error(f"❌ Oracle database error: {e}")
        raise DatabaseError(f"Failed to retrieve enrollment data: {e}")
    except Exception as e:
        logger.error(f"❌ Unexpected error retrieving enrollment data: {e}")
        raise DatabaseError(f"Unexpected error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        logger.debug("🔒 Database connection closed")


def validate_and_transform_student(student: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and transform student data
    
    Args:
        student: Raw student data from database
        
    Returns:
        Dict[str, Any]: Validated and transformed student data
    """
    # Convert grade level to integer if possible
    if student.get('grade_level') is not None:
        try:
            student['grade_level'] = int(student['grade_level'])
        except (ValueError, TypeError):
            logger.warning(f"Invalid grade level for student {student.get('student_number')}: {student.get('grade_level')}")
    
    # Normalize string fields
    string_fields = ['last_name', 'first_name', 'middle_name', 'school_name', 'home_room', 'gender']
    for field in string_fields:
        if student.get(field):
            student[field] = str(student[field]).strip()
    
    # Handle null web passwords (security)
    if not student.get('web_password'):
        student['web_password'] = None
    
    return student


def validate_and_transform_staff(staff: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and transform staff data
    
    Args:
        staff: Raw staff data from database
        
    Returns:
        Dict[str, Any]: Validated and transformed staff data
    """
    # Normalize string fields
    string_fields = ['first_name', 'last_name', 'lastfirst', 'email', 'school_name', 'title', 'phone']
    for field in string_fields:
        if staff.get(field):
            staff[field] = str(staff[field]).strip()
    
    # Convert boolean-like fields
    boolean_fields = ['can_change_school', 'admin_access', 'teacher_access']
    for field in boolean_fields:
        value = staff.get(field)
        if value is not None:
            staff[field] = bool(int(value)) if str(value).isdigit() else bool(value)
    
    return staff


def validate_and_transform_enrollment(enrollment: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and transform enrollment data
    
    Args:
        enrollment: Raw enrollment data from database
        
    Returns:
        Dict[str, Any]: Validated and transformed enrollment data
    """
    # Convert grade level to integer
    if enrollment.get('grade_level') is not None:
        try:
            enrollment['grade_level'] = int(enrollment['grade_level'])
        except (ValueError, TypeError):
            logger.warning(f"Invalid grade level for student {enrollment.get('student_number')}: {enrollment.get('grade_level')}")
    
    # Normalize string fields
    string_fields = ['last_name', 'first_name', 'school_name']
    for field in string_fields:
        if enrollment.get(field):
            enrollment[field] = str(enrollment[field]).strip()
    
    return enrollment


class DatabaseError(Exception):
    """Custom exception for database-related errors"""
    pass


def test_connection() -> bool:
    """
    Test database connection
    
    Returns:
        bool: True if connection successful, False otherwise
        
    Example:
        if test_connection():
            print("Database connection OK")
        else:
            print("Database connection failed")
    """
    logger.info("🔍 Testing database connection")
    
    try:
        conn = connect_to_ps()
        cursor = conn.cursor()
        
        # Simple test query
        cursor.execute("SELECT 1 AS TEST FROM DUAL")
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if result and result['TEST'] == 1:  # Note: Oracle returns UPPERCASE 'TEST'
            logger.info("✅ Database connection test successful")
            return True
        else:
            logger.error("❌ Database connection test failed - unexpected result")
            return False
            
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        return False
