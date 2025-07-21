# Development Guidelines

This guide provides best practices and guidelines for developing Seton packages using the template.

## Development Workflow

### 1. Initial Setup

```bash
# Clone the template
git clone https://github.com/JackJosephWright/seton_pipeline_template.git your_package_name
cd your_package_name

# Run automated setup
python setup_dev_env.py

# Activate virtual environment
# Windows:
venv_your_package_name\Scripts\activate
# Unix/Linux/macOS:
source venv_your_package_name/bin/activate
```

### 2. Development Cycle

```bash
# Make your changes
# ...

# Run tests
pytest

# Run with coverage
pytest --cov=src

# Check code quality
black src tests
flake8 src tests
mypy src

# Run your package
python -m src.your_package_name.main
```

### 3. Pre-commit Checks

Install pre-commit hooks:
```bash
pre-commit install
```

Run all checks:
```bash
pre-commit run --all-files
```

## Code Organization

### Package Structure

```
your_package_name/
├── src/your_package_name/
│   ├── __init__.py           # Package exports
│   ├── main.py              # Main entry point
│   ├── config/              # Configuration management
│   │   ├── settings.py      # Environment & variable management
│   │   └── logging_config.py # Logging setup
│   ├── database/            # Database operations
│   │   └── queries.py       # SQL queries and data retrieval
│   ├── google_sheets/       # Google Sheets integration
│   │   └── sheets_manager.py # Sheets operations
│   └── utils/               # Utility functions
│       └── helpers.py       # Data processing helpers
├── tests/                   # Comprehensive test suite
├── docs/                    # Documentation
└── requirements*.txt        # Dependencies
```

### Module Responsibilities

- **main.py**: Entry point, orchestrates the workflow
- **config/**: Environment detection, settings management
- **database/**: Oracle database interactions, query management
- **google_sheets/**: Google Sheets API operations
- **utils/**: Data processing, validation, transformation

## Coding Standards

### 1. Oracle Database Patterns

**Always use UPPERCASE column names** when accessing Oracle results:

```python
# ✅ CORRECT
def process_students(rows):
    students = []
    for row in rows:
        student = {
            'student_number': row['STUDENT_NUMBER'],  # UPPERCASE key!
            'last_name': row['LAST_NAME'],            # UPPERCASE key!
            'first_name': row['FIRST_NAME']           # UPPERCASE key!
        }
        students.append(student)
    return students

# ❌ WRONG - Will cause KeyError
def process_students_WRONG(rows):
    students = []
    for row in rows:
        student = {
            'student_number': row['student_number'],  # KeyError!
            'last_name': row['last_name']             # KeyError!
        }
        students.append(student)
    return students
```

### 2. Configuration Access

Use the template's configuration system:

```python
# ✅ CORRECT - Auto-detects Airflow vs local
from your_package_name.config.settings import get_variable, get_environment

environment = get_environment()
sheet_id = get_variable("GOOGLE_SHEET_ID_PROD")

# ❌ WRONG - Manual environment detection
import os
try:
    from airflow.models import Variable
    sheet_id = Variable.get("GOOGLE_SHEET_ID_PROD")
except:
    sheet_id = os.getenv("GOOGLE_SHEET_ID_PROD")
```

### 3. Error Handling

Follow the template's error handling patterns:

```python
# ✅ CORRECT - Comprehensive error handling
def get_data():
    conn = None
    cursor = None
    try:
        conn = connect_to_ps()
        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()
    except cx_Oracle.Error as e:
        logger.error(f"Oracle error: {e}")
        raise DatabaseError(f"Database operation failed: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise DatabaseError(f"Unexpected error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
```

### 4. Logging Standards

Use the template's logging system:

```python
from your_package_name.config.logging_config import get_logger

logger = get_logger(__name__)

def process_data():
    logger.info("🚀 Starting data processing")
    try:
        # Processing logic
        logger.info("✅ Data processing completed")
    except Exception as e:
        logger.error(f"❌ Processing failed: {e}")
        raise
```

## Testing Guidelines

### 1. Test Organization

```
tests/
├── conftest.py              # Shared fixtures
├── test_main.py            # Main function tests
├── test_database/
│   └── test_queries.py     # Database tests
├── test_google_sheets/
│   └── test_sheets_manager.py # Sheets tests
└── test_utils/
    └── test_helpers.py     # Utility tests
```

### 2. Mock Patterns

**Always use UPPERCASE keys in Oracle mock data**:

```python
@pytest.fixture
def sample_student_data():
    """Mock Oracle data with UPPERCASE keys"""
    return [
        {
            'STUDENT_NUMBER': 12345,    # UPPERCASE!
            'LAST_NAME': 'Smith',       # UPPERCASE!
            'FIRST_NAME': 'John',       # UPPERCASE!
            'GRADE_LEVEL': 10           # UPPERCASE!
        }
    ]
```

### 3. Test Categories

Use pytest markers to categorize tests:

```python
@pytest.mark.unit
def test_data_validation():
    """Unit test for data validation"""
    pass

@pytest.mark.integration
def test_database_integration():
    """Integration test requiring database"""
    pass

@pytest.mark.slow
def test_large_dataset():
    """Slow test with large dataset"""
    pass
```

Run specific test categories:
```bash
pytest -m unit          # Only unit tests
pytest -m "not slow"    # Exclude slow tests
pytest -m integration   # Only integration tests
```

### 4. Coverage Standards

Maintain high test coverage:
```bash
pytest --cov=src --cov-report=html --cov-fail-under=80
```

## Documentation Standards

### 1. Docstring Format

```python
def process_data(data: List[Dict[str, Any]], validate: bool = True) -> List[Dict[str, Any]]:
    """
    Process and validate data for upload
    
    Args:
        data: List of records to process
        validate: Whether to perform validation
        
    Returns:
        List[Dict[str, Any]]: Processed and validated data
        
    Raises:
        ValidationError: If data validation fails
        
    Example:
        data = [{'STUDENT_NUMBER': 123, 'LAST_NAME': 'Smith'}]
        processed = process_data(data)
    """
```

### 2. README Updates

Update your package README with:
- Purpose and functionality
- Installation instructions
- Configuration requirements
- Usage examples
- Oracle column naming notes

### 3. Type Hints

Use comprehensive type hints:

```python
from typing import List, Dict, Any, Optional, Union

def get_student_data(school_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get student data with optional school filter"""
    pass
```

## Performance Guidelines

### 1. Database Optimization

```python
# ✅ Use connection pooling patterns
def batch_process_students():
    conn = connect_to_ps()
    try:
        for batch in student_batches:
            process_batch(conn, batch)  # Reuse connection
    finally:
        conn.close()

# ✅ Use appropriate query limits
query = """
SELECT STUDENT_NUMBER, LAST_NAME, FIRST_NAME
FROM STUDENTS 
WHERE ENROLL_STATUS = 0
AND ROWNUM <= 1000  -- Limit results
"""
```

### 2. Google Sheets Optimization

```python
# ✅ Use batch operations
manager.batch_update_multiple_worksheets({
    "Students": student_data,
    "Staff": staff_data
})

# ✅ Handle rate limits
import time
for worksheet_name, data in worksheets.items():
    manager.update_worksheet(worksheet_name, data)
    time.sleep(0.5)  # Rate limiting
```

### 3. Memory Management

```python
# ✅ Process large datasets in chunks
from your_package_name.utils.helpers import chunk_data

large_dataset = get_all_students()
for chunk in chunk_data(large_dataset, 1000):
    process_chunk(chunk)
```

## Security Guidelines

### 1. Credential Management

```python
# ✅ Use environment variables
credentials_path = get_variable("GOOGLE_CREDENTIALS_PATH")

# ✅ Mask sensitive data in logs
from your_package_name.utils.helpers import mask_sensitive_data
masked_data = mask_sensitive_data(data, ['password', 'ssn'])
logger.info(f"Processing {len(masked_data)} records")

# ❌ Never hardcode credentials
google_creds = "/path/to/secret/file.json"  # DON'T DO THIS
```

### 2. Production Safety

```python
# ✅ Always validate environment
from your_package_name.config.settings import validate_environment

def main():
    validate_environment()  # Critical safety check
    # ... rest of code
```

### 3. Data Sanitization

```python
# ✅ Sanitize data before processing
from your_package_name.utils.helpers import sanitize_data

cleaned_data = sanitize_data(raw_data, 
                            remove_empty_strings=True,
                            trim_whitespace=True)
```

## Git Workflow

### 1. Branch Naming

```bash
git checkout -b feature/add-enrollment-data
git checkout -b bugfix/oracle-column-naming
git checkout -b hotfix/production-sheet-access
```

### 2. Commit Messages

```bash
git commit -m "feat: add enrollment data retrieval with Oracle UPPERCASE handling"
git commit -m "fix: correct Oracle column naming in staff queries"
git commit -m "test: add comprehensive Oracle column naming tests"
git commit -m "docs: update Oracle column naming documentation"
```

### 3. Pre-merge Checklist

- [ ] All tests pass
- [ ] Code coverage maintained
- [ ] Oracle column naming patterns followed
- [ ] Environment validation included
- [ ] Documentation updated
- [ ] Security review completed

## Deployment Guidelines

### 1. Environment Preparation

**Development**:
```bash
ENVIRONMENT=development
GOOGLE_SHEET_ID_DEV=your_dev_sheet_id
```

**Testing**:
```bash
ENVIRONMENT=testing
GOOGLE_SHEET_ID_TEST=your_test_sheet_id
```

**Production**:
```bash
ENVIRONMENT=production
GOOGLE_SHEET_ID_PROD=your_prod_sheet_id
```

### 2. Airflow Deployment

1. **Set Airflow Variables**:
   ```bash
   airflow variables set ENVIRONMENT "production"
   airflow variables set GOOGLE_SHEET_ID_PROD "your_prod_sheet"
   airflow variables set GOOGLE_CREDENTIALS_PATH "/opt/airflow/creds/service-account.json"
   ```

2. **Deploy DAG**:
   ```python
   from your_package_name.main import main
   
   run_task = PythonOperator(
       task_id='run_package',
       python_callable=main,
       dag=dag
   )
   ```

### 3. Monitoring

```python
# Add monitoring and alerting
def main(**kwargs):
    try:
        result = run_package()
        if not result:
            # Send alert
            send_failure_alert("Package execution failed")
        return result
    except Exception as e:
        send_error_alert(f"Critical error: {e}")
        raise
```

## Common Pitfalls

### 1. Oracle Column Naming

❌ **Most common mistake**: Using lowercase column names
```python
# This will fail!
student_number = row['student_number']
```

✅ **Always use UPPERCASE**:
```python
# This works!
student_number = row['STUDENT_NUMBER']
```

### 2. Environment Configuration

❌ **Hardcoded sheet IDs**:
```python
sheet_id = "hardcoded_sheet_id"  # Don't do this
```

✅ **Environment-aware configuration**:
```python
sheet_id = get_sheet_id()  # Automatically selects correct sheet
```

### 3. Error Handling

❌ **Silent failures**:
```python
try:
    process_data()
except:
    pass  # Silent failure is dangerous
```

✅ **Proper error handling**:
```python
try:
    process_data()
except Exception as e:
    logger.error(f"Processing failed: {e}")
    raise
```

## Getting Help

1. **Check the documentation**: `docs/` directory
2. **Run the tests**: `pytest -v`
3. **Check Oracle column naming**: `docs/oracle_column_naming.md`
4. **Review configuration**: `docs/configuration.md`
5. **Test connection**: Use built-in test functions

```python
# Test database connection
from your_package_name.database.queries import test_connection
print(f"Database OK: {test_connection()}")

# Test Google Sheets connection
from your_package_name.google_sheets.sheets_manager import test_sheets_connection
print(f"Sheets OK: {test_sheets_connection('your_sheet_id')}")
```

Remember: The Oracle column naming pattern is the most critical aspect of Seton package development. When in doubt, use UPPERCASE keys!
