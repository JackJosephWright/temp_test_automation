# Oracle Database Integration - CRITICAL DOCUMENTATION

⚠️ **CRITICAL PATTERNS FOR ALL SETON PACKAGES** ⚠️

## Modern Oracle Driver (oracledb)

**✅ IMPORTANT: Use Modern Driver**

Seton packages now use the **modern `oracledb` driver** instead of legacy `cx_Oracle`:

```python
# ✅ CORRECT - Modern approach (already in seton_utils)
from seton_utils.connect_to_ps import connect_to_ps

# This uses oracledb internally through SQLAlchemy
conn = connect_to_ps()
```

```bash
# ✅ Install modern driver
pip install oracledb  # No build tools needed!

# ❌ Don't use legacy driver  
pip install cx_Oracle  # Requires Visual C++ Build Tools
```

**Benefits of Modern Driver:**
- ✅ No Microsoft Visual C++ Build Tools required
- ✅ Easier installation on Windows
- ✅ Better performance and features
- ✅ Official Oracle support
- ✅ Works with Instant Client or full Oracle Client

## Oracle Column Naming - CRITICAL PATTERN

Oracle database returns **ALL** column names in **UPPERCASE**. This is the most common source of bugs in Seton packages and must be handled correctly.

## The Problem

When you execute a query against Oracle/PowerSchool database:

```sql
SELECT student_number, last_name, first_name FROM students
```

Oracle returns results where the column names are **UPPERCASE**:
- `'STUDENT_NUMBER'` (not `'student_number'`)
- `'LAST_NAME'` (not `'last_name'`)
- `'FIRST_NAME'` (not `'first_name'`)

## The Solution Pattern

### ✅ CORRECT Pattern

```python
from seton_utils.connect_to_ps import connect_to_ps

def get_student_data():
    conn = connect_to_ps()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT STUDENT_NUMBER, LAST_NAME, FIRST_NAME, GRADE_LEVEL
        FROM STUDENTS 
        WHERE ENROLL_STATUS = 0
    """)
    
    results = cursor.fetchall()
    students = []
    
    for row in results:
        # ✅ CORRECT: Access with UPPERCASE keys, normalize to lowercase
        student = {
            'student_number': row['STUDENT_NUMBER'],  # UPPERCASE key!
            'last_name': row['LAST_NAME'],            # UPPERCASE key!
            'first_name': row['FIRST_NAME'],          # UPPERCASE key!
            'grade_level': row['GRADE_LEVEL']         # UPPERCASE key!
        }
        students.append(student)
    
    cursor.close()
    conn.close()
    return students
```

### ❌ WRONG Pattern (Common Bug)

```python
def get_student_data_WRONG():
    # ... database connection code ...
    
    for row in results:
        # ❌ WRONG: This will cause KeyError!
        student = {
            'student_number': row['student_number'],  # KeyError! No lowercase key
            'last_name': row['last_name'],            # KeyError! No lowercase key
            'first_name': row['first_name']           # KeyError! No lowercase key
        }
        students.append(student)
```

## Common Oracle Column Names in PowerSchool

### Students Table
- `'STUDENT_NUMBER'` (not `'student_number'`)
- `'DCID'` (not `'dcid'`)
- `'LAST_NAME'` (not `'last_name'`)
- `'FIRST_NAME'` (not `'first_name'`)
- `'MIDDLE_NAME'` (not `'middle_name'`)
- `'GRADE_LEVEL'` (not `'grade_level'`)
- `'ENROLL_STATUS'` (not `'enroll_status'`)
- `'ENTRYDATE'` (not `'entrydate'`)
- `'EXITDATE'` (not `'exitdate'`)
- `'SCHOOLID'` (not `'schoolid'`)
- `'HOME_ROOM'` (not `'home_room'`)
- `'GENDER'` (not `'gender'`)
- `'DOB'` (not `'dob'`)
- `'STUDENT_WEB_ID'` (not `'student_web_id'`)
- `'STUDENT_WEB_PASSWORD'` (not `'student_web_password'`)

### Staff/Users Table
- `'DCID'` (not `'dcid'`)
- `'LASTFIRST'` (not `'lastfirst'`)
- `'FIRST_NAME'` (not `'first_name'`)
- `'LAST_NAME'` (not `'last_name'`)
- `'EMAIL_ADDR'` (not `'email_addr'`)
- `'SCHOOLID'` (not `'schoolid'`)
- `'TITLE'` (not `'title'`)
- `'PHONE'` (not `'phone'`)
- `'CANCHANGESCHOOL'` (not `'canchangeschool'`)
- `'ADMIN_ACCESS'` (not `'admin_access'`)
- `'TEACHER_ACCESS'` (not `'teacher_access'`)

### Schools Table
- `'SCHOOL_NUMBER'` (not `'school_number'`)
- `'NAME'` (not `'name'`)
- `'ABBREVIATION'` (not `'abbreviation'`)

## Testing Pattern

When writing tests, **always use UPPERCASE keys** in mock data to simulate Oracle behavior:

```python
@pytest.fixture
def sample_student_data():
    """Sample data with UPPERCASE keys (Oracle pattern)"""
    return [
        {
            'STUDENT_NUMBER': 12345,        # UPPERCASE key
            'LAST_NAME': 'Smith',           # UPPERCASE key
            'FIRST_NAME': 'John',           # UPPERCASE key
            'GRADE_LEVEL': 10               # UPPERCASE key
        }
    ]

def test_student_processing(sample_student_data):
    # Mock Oracle cursor
    mock_cursor.fetchall.return_value = sample_student_data
    
    result = get_student_data()
    
    # Verify normalization to lowercase keys
    assert 'student_number' in result[0]    # lowercase in output
    assert 'STUDENT_NUMBER' not in result[0]  # UPPERCASE removed
```

## Error Patterns to Watch For

### 1. KeyError on Row Access
```python
# ❌ This will fail with KeyError
student_number = row['student_number']  # Oracle doesn't have lowercase keys

# ✅ This works
student_number = row['STUDENT_NUMBER']  # Oracle has UPPERCASE keys
```

### 2. Inconsistent Column References
```python
# ❌ Mixing case will cause confusion
query = "SELECT student_number, LAST_NAME FROM students"  # Inconsistent

# ✅ Use consistent UPPERCASE in SQL and access
query = "SELECT STUDENT_NUMBER, LAST_NAME FROM students"
student_number = row['STUDENT_NUMBER']
last_name = row['LAST_NAME']
```

### 3. Copy-Paste from Other Databases
```python
# ❌ Code copied from MySQL/PostgreSQL won't work
student_data = {
    'id': row['id'],              # Other DBs might use lowercase
    'name': row['name']           # Won't work with Oracle
}

# ✅ Always use Oracle UPPERCASE pattern
student_data = {
    'id': row['ID'],              # Oracle UPPERCASE
    'name': row['NAME']           # Oracle UPPERCASE
}
```

## Quick Reference Checklist

Before deploying any Seton package:

- [ ] All database column access uses UPPERCASE keys
- [ ] Test data fixtures use UPPERCASE keys
- [ ] Documentation examples show UPPERCASE pattern
- [ ] Code review checks for lowercase column access
- [ ] Integration tests validate Oracle column naming

## Debugging Oracle Column Issues

If you're getting KeyError exceptions:

1. **Print available keys**:
   ```python
   print("Available columns:", list(row.keys()))
   # Should show: ['STUDENT_NUMBER', 'LAST_NAME', 'FIRST_NAME']
   # NOT: ['student_number', 'last_name', 'first_name']
   ```

2. **Check SQL column aliases**:
   ```python
   # If you need lowercase, use AS alias
   query = "SELECT STUDENT_NUMBER AS student_number FROM students"
   # Then you can access: row['student_number']
   ```

3. **Verify connection type**:
   ```python
   # Make sure you're using Oracle connection
   from seton_utils.connect_to_ps import connect_to_ps
   conn = connect_to_ps()  # This connects to Oracle
   ```

## Summary

> **Remember**: Oracle = UPPERCASE column names
> 
> When in doubt, use UPPERCASE keys when accessing Oracle query results. Your future self (and your colleagues) will thank you for following this critical pattern.

This pattern is embedded throughout the Seton package template and should be followed religiously in all Seton ecosystem packages.
