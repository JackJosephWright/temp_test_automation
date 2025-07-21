# Seton Package Template

A comprehensive template repository for creating Python packages that integrate seamlessly with the Seton ecosystem. This template captures all the patterns and best practices learned from developing successful Seton packages.

## 🎯 **Template Philosophy: 80% Infrastructure, 20% Business Logic**

This template provides **production-ready infrastructure** so you can focus on **your specific data processing needs**. Instead of spending days configuring Oracle connections, Google Sheets integration, and environment management, you get a working foundation in 10 minutes.

### **Standard Package Interface**
Every package created from this template follows a **standardized `main()` function pattern** that works seamlessly with Airflow:

```python
def main(context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Standard entry point - works in both Airflow and standalone environments
    
    Args:
        context: Airflow context (optional, provided automatically by Airflow)
        
    Returns:
        Dict[str, Any]: Consistent results format across all packages
    """
    # Your business logic here
    return {
        "status": "success", 
        "records_processed": 1250,
        "environment": "production"
    }
```

### **One-Line Airflow Integration**
```python
# In your Airflow DAG - just import and use
from your_package.main import main

sync_task = PythonOperator(
    task_id='run_your_package',
    python_callable=main,  # Template's standardized main() function
    dag=dag
)
```

## 🚀 Quick Start

### 1. Use This Template
Click "Use this template" on GitHub or clone this repository:
```bash
git clone https://github.com/your-org/seton-package-template.git your-package-name
cd your-package-name
```

### 2. Automated Setup
Run the setup script to configure your development environment:
```bash
python setup_dev_env.py
```

The script will:
- ✅ Create a virtual environment
- ✅ Install all dependencies including modern `oracledb` driver
- ✅ Install `seton_utils` from private GitHub repository
- ✅ Rename entire template with your package name
- ✅ Update all imports and references automatically
- ✅ Create environment configuration files
- ✅ Validate the installation with diagnostic tests

### 3. Configure Your Environment
Edit the generated `.env` file with your specific settings:
```bash
# Environment Detection (automatically used)
ENVIRONMENT=development
LOG_LEVEL=DEBUG

# Google Sheets Integration (optional)
ATTENDANCE_SHEET_ID=your_dev_sheet_id_here
STUDENT_SYNC_SHEET_ID=another_sheet_id_here

# Database Connections (handled automatically by seton_utils)
# No connection strings needed - seton_utils manages all credentials

# GitHub PAT for seton_utils installation
GITHUB_PAT=your_personal_access_token_here
```

**Environment Auto-Detection:**
The template automatically adapts configuration sources:
- 🏠 **Local Development**: Uses `.env` file with `os.getenv()`
- 🚁 **Airflow Production**: Uses `Variable.get()` from Airflow UI
- 🔄 **Zero Code Changes**: Same package works in both environments

---

## 📋 **Template vs Package: Key Concepts**

### **🎯 Template Repository (This Repo)**
- **Purpose**: Reusable foundation for creating packages
- **Location**: `https://github.com/JackJosephWright/seton_pipeline_template`
- **Usage**: Create new repositories using "Use this template"
- **Maintenance**: Updated by template maintainers

### **📦 Package Repository (Your Repo)**  
- **Purpose**: Specific data processing package (e.g., attendance, grades)
- **Location**: `https://github.com/your-username/process_attendance`
- **Usage**: Deployed to Airflow, contains your business logic
- **Maintenance**: Owned and maintained by you

### **🚁 Airflow Integration**
- **Installs**: Your package (`process_attendance`), not the template
- **Imports**: `from process_attendance.main import main`
- **Deployment**: `pip install git+https://github.com/your-username/process_attendance.git`

---

## **How to Use This Template (Important!)**

### **This is a Template Repository, Not a Package to Install**

This repository is designed to be **cloned and customized**, not installed as a dependency.

**⚡ QUICK START: Use GitHub's "Use This Template" Feature**

**🎯 Don't clone this repository directly!** Instead:

**⚠️ FIRST: Enable Template Feature**
1. **Go to**: https://github.com/JackJosephWright/seton_pipeline_template/settings
2. **Scroll to "Template repository" section**
3. **Check the box**: ✅ "Template repository" 
4. **Return to main repository page**

**✅ THEN: Use the Template**
1. **Go to**: https://github.com/JackJosephWright/seton_pipeline_template
2. **Click the green "Use this template" button** (now visible near "Code" button)
3. **Fill out the form**:
   - **Repository name**: `process_attendance` (or your package name)
   - **Description**: "Package for processing daily attendance data"
   - **Public/Private**: Choose based on your needs
4. **Click "Create repository from template"**

**✅ Result**: GitHub creates **YOUR own repository** at `https://github.com/your-username/process_attendance`

**Step 2: Clone YOUR New Repository**
```bash
# Clone YOUR repository (not the template!)
git clone https://github.com/your-username/process_attendance.git
cd process_attendance
```

**Step 3: Run Automated Setup**
```bash
# Transform YOUR repository into a working package
python setup_dev_env.py
# Enter your package name when prompted (e.g., "process_attendance")
```

**The setup script will:**
- ✅ Rename `seton_package_template` → `process_attendance`
- ✅ Update all imports throughout the codebase
- ✅ Create `.env` file from `.env.template`  
- ✅ Create virtual environment: `venv_process_attendance`
- ✅ Install dependencies including `seton_utils`

**🎉 That's It! You Now Have a Working Package**

Your repository structure after setup:
```
process_attendance/                   # ✅ YOUR repository
├── src/process_attendance/           # ✅ YOUR package code
├── .env                             # ✅ YOUR environment config
├── venv_process_attendance/         # ✅ YOUR virtual environment
└── README.md                        # ✅ Customize as needed
```

**Repository URL**: `https://github.com/your-username/process_attendance`
**Package Import**: `from process_attendance.main import main`

---

**Alternative Method: Manual Clone (Not Recommended)**

This repository is designed to be **cloned and customized**, not installed as a dependency.

### **Complete Workflow:**

#### **Step 1: Create Your Package Repository**
```bash
# Clone this template to create your new package
git clone https://github.com/JackJosephWright/seton_pipeline_template.git process_attendance
cd process_attendance

# Remove the template's Git history and start fresh
rm -rf .git
git init
git add .
git commit -m "Initial package from seton_pipeline_template"
```

#### **Step 2: Run Automated Setup**
```bash
# Transform the template into your specific package
python setup_dev_env.py
# Enter your package name when prompted (e.g., "process_attendance")
```

**The setup script will:**
- ✅ Rename `seton_package_template` → `process_attendance`
- ✅ Update all imports throughout the codebase
- ✅ Create `.env` file from `.env.template`  
- ✅ Create virtual environment: `venv_process_attendance`
- ✅ Install dependencies including `seton_utils`

#### **Step 3: Configure Your Environment**
```bash
# The setup script creates .env file - add your GitHub PAT:
nano .env

# Add this line:
GITHUB_PAT=ghp_your_personal_access_token_here
```

#### **Step 4: Develop Your Business Logic**
```python
# Edit src/process_attendance/main.py
def main(context=None):
    """Your specific attendance processing logic"""
    
    # Template provides infrastructure:
    settings = get_settings()          # Environment detection
    logger = get_logger(__name__)       # Structured logging
    sheets = SheetsManager(sheet_id)    # Google Sheets integration
    
    # You add business logic:
    attendance_data = get_attendance_from_powerschool()  # Your function
    processed_data = calculate_metrics(attendance_data)   # Your function
    sheets.update_worksheet_dict("Report", processed_data) # Template handles upload
    
    return {"status": "success", "records": len(processed_data)}
```

#### **Step 5: Create New Repository & Deploy**
```bash
# Create new repository on GitHub for YOUR package
# Then push your customized package:
git remote add origin https://github.com/seton/process_attendance.git
git push -u origin main

# Deploy to Airflow by installing your package:
pip install git+https://github.com/seton/process_attendance.git
```

#### **Step 6: Use in Airflow DAG**
```python
# In airflow_clean/dags/attendance_pipeline.py
from process_attendance.main import main as run_attendance

attendance_task = PythonOperator(
    task_id='process_attendance',
    python_callable=run_attendance,  # Your package's main() function!
    dag=dag
)
```

### **⚠️ Important: You Own Your Package Repository**

After using this template:
- 📦 **You have your own repository** (e.g., `process_attendance`)
- 🔧 **You maintain your own code** and dependencies  
- 🚀 **You deploy YOUR package** to Airflow, not this template
- 🔄 **Updates to this template** don't automatically affect your package

## 🔑 **GitHub PAT Requirements & Security**

### **When is GitHub PAT Required?**

#### **✅ ALWAYS Required: Template Setup**
```bash
# When using this template - PAT needed for seton_utils installation
python setup_dev_env.py
# → Installs seton_utils from private GitHub repository
```

### **PAT Security Options (Choose One):**

#### **🥇 Most Secure: Environment Variable (Recommended)**
```bash
# Set PAT as environment variable
export GITHUB_PAT=ghp_your_pat_here
python setup_dev_env.py  # Auto-detects PAT
```

#### **🥈 Secure: .env File (Delete After Setup)**
```bash
# Add to .env file created by setup script
echo "GITHUB_PAT=ghp_your_pat_here" >> .env
python setup_dev_env.py
# Then delete the PAT line from .env for security
```

#### **🥉 Interactive: Prompt Only**
```bash
# Run setup without PAT - script will prompt securely
python setup_dev_env.py
# Enter PAT when prompted (not saved anywhere)
```

### **PAT Permissions Required:**
- ✅ `repo` (Full control of private repositories)
- ✅ `read:packages` (Download packages)

Create PAT at: https://github.com/settings/tokens

## 🤖 **For AI Assistants: Template Usage Summary**

**WORKFLOW CLARIFICATION FOR AI:**

1. **This is a TEMPLATE** that creates NEW repositories
2. **Users don't modify this template** directly  
3. **Each package is independent** with its own repository
4. **The process is:** Template → New Repo → Customize → Deploy

**Example AI Conversation:**
- **User**: "Help me create an attendance package"
- **AI**: "I'll help you customize the template for attendance processing. Did you use the 'Use this template' button to create your own repository first?"

**Key AI Understanding Points:**
- ✅ Template creates independent repositories
- ✅ Users own and maintain their package repositories  
- ✅ Airflow installs the user's package, not the template
- ✅ Template provides 80% infrastructure, user adds 20% business logic

## 🏗️ Template Architecture

### Package Structure
The template creates a standardized package structure optimized for Seton's Airflow environment:

```
src/your_package_name/
├── __init__.py              # Package initialization
├── main.py                  # 🎯 Airflow entry point with main() function
├── config/
│   ├── __init__.py
│   ├── settings.py          # 🔧 Environment-aware configuration
│   └── logging_config.py    # 📊 Structured logging setup
├── database/
│   ├── __init__.py
│   └── queries.py           # 🗃️ SQL queries with Oracle patterns
├── google_sheets/
│   ├── __init__.py
│   └── sheets_manager.py    # 📋 Complete Google Sheets CRUD operations
└── utils/
    ├── __init__.py
    ├── helpers.py           # 🛠️ Data processing utilities
    └── exceptions.py        # ⚠️ Custom error handling
```

### 🎯 The main() Function Pattern

**Why This Matters:** Airflow requires a standardized entry point for each package. The template provides a `main()` function that:
- ✅ Works seamlessly with Airflow DAG imports
- ✅ Provides consistent error handling across all packages
- ✅ Enables easy local testing and debugging
- ✅ Maintains environment detection automatically

**Standard Pattern:**
```python
def main():
    """
    Main entry point for the package.
    This function is called by Airflow DAGs and can be tested locally.
    """
    try:
        logger.info("Starting package execution")
        
        # Your package logic here
        process_data()
        update_sheets()
        sync_databases()
        
        logger.info("Package execution completed successfully")
        return {"status": "success", "message": "All operations completed"}
        
    except Exception as e:
        logger.error(f"Package execution failed: {str(e)}")
        raise
```

### 🔄 seton_utils Integration Patterns

The template seamlessly integrates with `seton_utils` for database operations:

**PowerSchool Oracle Connection:**
```python
from seton_utils import connect_to_ps

def get_student_data():
    """Get student data from PowerSchool Oracle database."""
    conn = connect_to_ps()
    try:
        with conn.cursor() as cursor:
            cursor.execute(queries.GET_STUDENTS)
            rows = cursor.fetchall()
            # Oracle returns UPPERCASE column names
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    finally:
        conn.close()
```

**Azure SQL Connection:**
```python
from seton_utils import connect_to_azure_db

def update_azure_data(student_data):
    """Update student data in Azure SQL database."""
    conn = connect_to_azure_db()
    try:
        with conn.cursor() as cursor:
            for student in student_data:
                cursor.execute(queries.UPDATE_STUDENT, 
                             (student['STUDENT_NUMBER'], student['LASTFIRST']))
        conn.commit()
    finally:
        conn.close()
```

## 🌟 Real-World Usage Examples

### Example 1: Student Sync Package
```python
# main.py - Complete package that syncs PowerSchool to Azure
def main():
    """Sync student data from PowerSchool to Azure SQL."""
    try:
        logger.info("Starting student sync process")
        
        # 1. Query PowerSchool Oracle
        ps_conn = connect_to_ps()
        students = []
        try:
            with ps_conn.cursor() as cursor:
                cursor.execute("""
                    SELECT STUDENT_NUMBER, LASTFIRST, GRADE_LEVEL, SCHOOLID 
                    FROM STUDENTS 
                    WHERE ENROLLSTATUS = 0
                """)
                columns = [col[0] for col in cursor.description]
                students = [dict(zip(columns, row)) for row in cursor.fetchall()]
        finally:
            ps_conn.close()
        
        logger.info(f"Retrieved {len(students)} students from PowerSchool")
        
        # 2. Transform data
        for student in students:
            student['sync_timestamp'] = datetime.now()
            student['grade_level'] = int(student['GRADE_LEVEL']) if student['GRADE_LEVEL'] else 0
        
        # 3. Update Azure SQL
        azure_conn = connect_to_azure_db()
        try:
            with azure_conn.cursor() as cursor:
                for student in students:
                    cursor.execute("""
                        MERGE student_sync AS target
                        USING (VALUES (?, ?, ?, ?, ?)) AS source 
                               (student_number, name, grade_level, school_id, sync_timestamp)
                        ON target.student_number = source.student_number
                        WHEN MATCHED THEN UPDATE SET 
                            name = source.name,
                            grade_level = source.grade_level,
                            school_id = source.school_id,
                            sync_timestamp = source.sync_timestamp
                        WHEN NOT MATCHED THEN INSERT 
                            (student_number, name, grade_level, school_id, sync_timestamp)
                            VALUES (source.student_number, source.name, source.grade_level, 
                                   source.school_id, source.sync_timestamp);
                    """, (student['STUDENT_NUMBER'], student['LASTFIRST'], 
                          student['grade_level'], student['SCHOOLID'], student['sync_timestamp']))
            azure_conn.commit()
        finally:
            azure_conn.close()
        
        # 4. Update tracking sheet
        sheets_manager = SheetsManager()
        sheets_manager.update_sync_log('student_sync', len(students), 'success')
        
        logger.info("Student sync completed successfully")
        return {"status": "success", "students_synced": len(students)}
        
    except Exception as e:
        logger.error(f"Student sync failed: {str(e)}")
        # Update error tracking
        try:
            sheets_manager = SheetsManager()
            sheets_manager.update_sync_log('student_sync', 0, f'error: {str(e)}')
        except:
            pass  # Don't fail on logging errors
        raise
```

### Example 2: Attendance Processing Package
```python
# main.py - Process attendance data and update multiple systems
def main():
    """Process daily attendance and update tracking systems."""
    try:
        logger.info("Starting attendance processing")
        
        # 1. Get today's attendance from PowerSchool
        ps_conn = connect_to_ps()
        attendance_data = []
        try:
            with ps_conn.cursor() as cursor:
                cursor.execute("""
                    SELECT s.STUDENT_NUMBER, s.LASTFIRST, att.ATTENDANCEDATE, 
                           att.ATT_CODE, att.SCHOOLID
                    FROM STUDENTS s
                    JOIN ATTENDANCE att ON s.ID = att.STUDENTID
                    WHERE att.ATTENDANCEDATE = TRUNC(SYSDATE)
                    AND att.ATT_CODE IN ('A', 'T', 'E')
                """)
                columns = [col[0] for col in cursor.description]
                attendance_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        finally:
            ps_conn.close()
        
        # 2. Process and categorize attendance
        absent_students = [att for att in attendance_data if att['ATT_CODE'] == 'A']
        tardy_students = [att for att in attendance_data if att['ATT_CODE'] == 'T']
        early_dismissal = [att for att in attendance_data if att['ATT_CODE'] == 'E']
        
        # 3. Update Google Sheets dashboard
        sheets_manager = SheetsManager()
        
        # Update daily summary
        summary_data = [
            ['Date', 'Total Absent', 'Total Tardy', 'Early Dismissals'],
            [datetime.now().strftime('%Y-%m-%d'), 
             len(absent_students), len(tardy_students), len(early_dismissal)]
        ]
        sheets_manager.update_range('attendance_summary', 'A1:D2', summary_data)
        
        # Update detailed absence list
        absence_data = [['Student Number', 'Student Name', 'School', 'Code']]
        for student in absent_students:
            absence_data.append([
                student['STUDENT_NUMBER'], student['LASTFIRST'], 
                student['SCHOOLID'], student['ATT_CODE']
            ])
        sheets_manager.update_range('daily_absences', 'A1:D' + str(len(absence_data)), absence_data)
        
        # 4. Store in Azure for reporting
        azure_conn = connect_to_azure_db()
        try:
            with azure_conn.cursor() as cursor:
                for att in attendance_data:
                    cursor.execute("""
                        INSERT INTO daily_attendance 
                        (student_number, student_name, attendance_date, 
                         attendance_code, school_id, processed_timestamp)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (att['STUDENT_NUMBER'], att['LASTFIRST'], 
                          att['ATTENDANCEDATE'], att['ATT_CODE'], 
                          att['SCHOOLID'], datetime.now()))
            azure_conn.commit()
        finally:
            azure_conn.close()
        
        logger.info(f"Processed {len(attendance_data)} attendance records")
        return {
            "status": "success", 
            "total_records": len(attendance_data),
            "absent": len(absent_students),
            "tardy": len(tardy_students),
            "early_dismissal": len(early_dismissal)
        }
        
    except Exception as e:
        logger.error(f"Attendance processing failed: {str(e)}")
        raise
```

## 🎨 Customization Guide

### Adding New Database Connections
The template is designed to work with `seton_utils`, but you can add custom connections:

```python
# In your main.py or helpers.py
import pyodbc
from config.settings import get_setting

def connect_to_custom_db():
    """Connect to a custom database not in seton_utils."""
    connection_string = get_setting('CUSTOM_DB_CONNECTION')
    return pyodbc.connect(connection_string)
```

### Adding New Google Sheets Operations
Extend the `SheetsManager` class:

```python
# In google_sheets/sheets_manager.py
class SheetsManager:
    # ... existing methods ...
    
    def create_pivot_table(self, sheet_id, source_range, pivot_range):
        """Create a pivot table from source data."""
        # Implementation here
        pass
    
    def format_cells(self, sheet_id, range_name, format_spec):
        """Apply formatting to a range of cells."""
        # Implementation here
        pass
```

### Custom Error Handling
Add domain-specific exceptions:

```python
# In utils/exceptions.py
class StudentDataError(SetonPackageError):
    """Raised when student data validation fails."""
    pass

class AttendanceProcessingError(SetonPackageError):
    """Raised when attendance processing encounters issues."""
    pass
```

### Environment-Specific Logic
Use the environment detection for different behaviors:

```python
# In main.py
from config.settings import get_environment

def main():
    env = get_environment()
    
    if env == 'development':
        # Use smaller data sets, verbose logging
        limit_clause = "ROWNUM <= 100"
        logger.setLevel(logging.DEBUG)
    else:
        # Production settings
        limit_clause = ""
        logger.setLevel(logging.INFO)
    
    # Use limit_clause in your queries
```

## 🚀 Benefits Summary

### For Developers
- ⚡ **Rapid Setup**: New packages ready in minutes, not hours
- 🔄 **Consistent Patterns**: Same structure across all Seton packages
- 🛡️ **Built-in Best Practices**: Error handling, logging, testing
- 🔧 **Environment Flexibility**: Works locally and in Airflow seamlessly

### For Operations
- 📊 **Standardized Logging**: Consistent log formats across all packages
- 🔍 **Easy Debugging**: Predictable structure makes troubleshooting faster
- 🚁 **Airflow Ready**: Zero configuration needed for DAG integration
- 📈 **Scalable Architecture**: Add new data sources without architectural changes

### For Data Pipeline Reliability
- 🛡️ **Robust Error Handling**: Graceful failure with detailed logging
- 🔄 **Database Connection Management**: Automatic cleanup and connection pooling
- 📋 **Data Validation**: Built-in patterns for data quality checks
- 🎯 **Single Responsibility**: Each package handles one clear business function

## 📁 Template Structure

```
seton_package_template/
├── src/seton_package_template/          # Main package source
│   ├── __init__.py                      # Package initialization
│   ├── main.py                          # Entry point (Airflow compatible)
│   ├── config/                          # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py                  # Environment-aware settings
│   ├── database/                        # Oracle database integration
│   │   ├── __init__.py
│   │   └── queries.py                   # Database query functions
│   ├── google_sheets/                   # Google Sheets integration
│   │   ├── __init__.py
│   │   └── sheets_manager.py            # SheetsManager class
│   └── utils/                           # Utility functions
│       ├── __init__.py
│       ├── exceptions.py                # Custom exceptions
│       ├── logging.py                   # Structured logging
│       └── validators.py                # Data validation
├── tests/                               # Comprehensive test suite
│   ├── __init__.py
│   ├── conftest.py                      # Pytest configuration & fixtures
│   ├── test_main.py                     # Main workflow tests
│   ├── test_config/                     # Configuration tests
│   ├── test_database/                   # Database tests (with Oracle patterns)
│   ├── test_google_sheets/              # Google Sheets tests
│   └── test_utils/                      # Utility tests
├── docs/                                # Documentation
│   ├── oracle_column_naming.md          # CRITICAL Oracle patterns
│   ├── configuration.md                 # Environment setup guide
│   └── development.md                   # Development workflow
├── .github/workflows/                   # CI/CD pipelines
│   ├── test.yml                         # Test automation
│   └── publish.yml                      # Package publishing
├── requirements.txt                     # Core dependencies
├── requirements-dev.txt                 # Development dependencies
├── pyproject.toml                       # Modern Python packaging
├── setup_dev_env.py                     # Automated setup script
├── .env.template                        # Environment template
├── .gitignore                           # Git ignore patterns
└── README.md                            # This file
```

## 🔑 Key Features

### Oracle Database Integration
- **Seamless seton_utils integration** with `connect_to_ps()`
- **UPPERCASE column handling** - Oracle returns column names in UPPERCASE
- **Connection pooling** and automatic retry logic
- **Comprehensive test patterns** with mock Oracle data

### Google Sheets Integration  
- **Credential management** via seton_utils gdrive helpers
- **Batch operations** for efficient data processing
- **Environment-aware sheet selection** (dev vs production)
- **Robust error handling** and validation

### Environment Management
- **Airflow compatibility** - automatic detection of Airflow environment
- **Variable resolution** - `Variable.get()` in Airflow, `os.getenv()` locally
- **Environment validation** - prevents accidental production writes
- **Secure credential handling** - never log sensitive information

### Development Experience
- **Modern Python packaging** with pyproject.toml
- **Comprehensive test suite** with pytest fixtures
- **Code quality tools** - black, flake8, mypy, isort
- **Documentation** with critical Oracle patterns
- **CI/CD ready** with GitHub Actions

## ⚠️ Critical Oracle Pattern

**Oracle databases return column names in UPPERCASE!** This is the most important pattern to remember:

```python
# ❌ WRONG - will cause KeyError
def get_student_data():
    rows = cursor.fetchall()
    for row in rows:
        student_id = row['student_id']  # KeyError!

# ✅ CORRECT - use UPPERCASE keys
def get_student_data():
    rows = cursor.fetchall()
    for row in rows:
        student_id = row['STUDENT_ID']  # Works!
```

See `docs/oracle_column_naming.md` for complete details and examples.

## 🧪 Testing

The template includes comprehensive tests with realistic Oracle patterns:

```bash
# Activate virtual environment
source venv_your_package/bin/activate  # Linux/Mac
# or
venv_your_package\Scripts\activate     # Windows

# Run all tests
pytest

# Run with coverage
pytest --cov=your_package --cov-report=html

# Run specific test categories
pytest tests/test_database/           # Database tests only
pytest tests/test_google_sheets/      # Google Sheets tests only
```

## 📚 Documentation

### Essential Reading
1. **`docs/oracle_column_naming.md`** - CRITICAL Oracle database patterns
2. **`docs/configuration.md`** - Environment and configuration management
3. **`docs/development.md`** - Development workflow and best practices

### Code Examples
The template includes working examples of:
- Oracle database queries with proper UPPERCASE column handling
- Google Sheets operations with batch processing
- Environment-aware configuration management
- Comprehensive error handling and logging
- Test fixtures with realistic mock data

## 🔧 Development Workflow

### 1. Package Development
```bash
# Activate environment
source venv_your_package/bin/activate

# Install in development mode
pip install -e .

# Run your package
python -m your_package

# Or run directly
python src/your_package/main.py
```

### 2. Code Quality
```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/your_package
```

### 3. Testing
```bash
# Run tests with coverage
pytest --cov=your_package --cov-report=html

# Test specific modules
pytest tests/test_database/ -v

# Run tests in parallel
pytest -n auto
```

## 🚀 Deployment

### Airflow Integration
Your package is designed to work seamlessly with Apache Airflow:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from your_package.main import run_package

# Define your DAG
dag = DAG('your_package_dag', ...)

# Add your package as a task
package_task = PythonOperator(
    task_id='run_your_package',
    python_callable=run_package,
    dag=dag
)
```

### Manual Execution
```bash
# Run locally
python src/your_package/main.py

# Or as a module
python -m your_package
```

## 📦 Dependencies

### Core Dependencies
- `pandas` - Data manipulation and analysis
- `cx_Oracle` - Oracle database connectivity
- `gspread` - Google Sheets integration
- `seton_utils` - Seton ecosystem utilities
- `pydantic` - Data validation and settings
- `structlog` - Structured logging

### Development Dependencies
- `pytest` - Testing framework
- `black` - Code formatting
- `mypy` - Type checking
- `flake8` - Code linting
- See `requirements-dev.txt` for complete list

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch
3. **Follow** the established patterns
4. **Test** your changes thoroughly
5. **Document** any new patterns
6. **Submit** a pull request

## 📝 License

This template is provided under the MIT License. See `LICENSE` file for details.

## 🆘 Support & Troubleshooting

### 🔧 seton_utils Installation Issues

The most common issue is `seton_utils` installation failure. Here's how we successfully solved it:

#### ✅ Step 1: GitHub PAT Setup
Create a GitHub Personal Access Token with these **required permissions**:
- ✅ `repo` (Full control of private repositories)  
- ✅ `read:packages` (Download packages from GitHub Package Registry)

Create your PAT at: https://github.com/settings/tokens

#### ✅ Step 2: Manual Installation (if automated setup fails)
```bash
# 1. Activate your virtual environment
venv_your_package\Scripts\activate     # Windows
# or
source venv_your_package/bin/activate  # Linux/Mac

# 2. Install seton_utils with your PAT
pip install git+https://YOUR_PAT_HERE@github.com/JackJosephWright/seton_utils.git

# 3. Verify installation
python -c "import seton_utils; print('Success!')"
```

#### ✅ Step 3: Common Issues & Solutions

**Issue: "ModuleNotFoundError: No module named 'seton_utils'"**
```bash
# Check if seton_utils is installed
pip list | grep seton

# If not found, reinstall:
pip install git+https://YOUR_PAT@github.com/JackJosephWright/seton_utils.git
```

**Issue: "PAT Authentication Failed"**
- ✅ Check PAT hasn't expired
- ✅ Verify PAT has `repo` and `read:packages` permissions
- ✅ Ensure correct URL format: `git+https://PAT@github.com/...`

**Issue: "cx_Oracle build failed"**
```bash
# Install Visual C++ Build Tools OR use these alternatives:
pip install --only-binary=all cx_Oracle
# or for development without Oracle:
pip install --no-deps seton_utils  # Skip Oracle dependencies
```

**Issue: "Network/VPN connectivity"**
- ✅ Ensure VPN connection if required
- ✅ Check corporate firewall settings
- ✅ Try installation during different network conditions

#### ✅ Step 4: Validation Script
Create `test_seton_utils.py` to debug installation:
```python
#!/usr/bin/env python3
"""Enhanced seton_utils validation script"""

def test_seton_utils_installation():
    """Test seton_utils installation with detailed debugging"""
    try:
        import seton_utils
        print("✅ seton_utils imported successfully")
        
        # Test specific modules
        from seton_utils.connect_to_ps import connect_to_ps
        print("✅ Database connection module imported")
        
        from seton_utils.gdrive.gdrive_helpers import get_gdrive_credentials
        print("✅ Google Drive helpers imported")
        
        print(f"✅ seton_utils version: {getattr(seton_utils, '__version__', 'No version info')}")
        return True
        
    except ImportError as e:
        print(f"❌ seton_utils import failed: {e}")
        print("\n🔧 Troubleshooting steps:")
        print("1. Check if seton_utils is installed:")
        print("   pip list | grep seton")
        print("2. Reinstall with PAT:")
        print("   pip install git+https://YOUR_PAT@github.com/JackJosephWright/seton_utils.git")
        print("3. Check GitHub PAT permissions")
        return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_seton_utils_installation()
```

### 📦 Other Common Issues

**Oracle Connection Issues**
- Ensure Oracle Instant Client is installed
- Verify VPN connection to Seton network
- Check seton_utils configuration

**Google Sheets Permissions**
- Verify service account credentials
- Ensure sheet sharing permissions
- Check seton_utils gdrive configuration

**Import Errors**
- Activate virtual environment
- Install in development mode: `pip install -e .`
- Verify seton_utils installation

**Windows Build Tools Issues**
- Install Microsoft Visual C++ Build Tools
- Use precompiled wheels when available
- Consider using WSL for development

### Getting Help
1. Check the documentation in `docs/`
2. Review the test examples for patterns
3. Consult the seton_utils documentation
4. Open an issue on the repository

---

**Remember**: Oracle returns UPPERCASE column names! This is the most common source of errors when working with Seton packages. Always use `row['COLUMN_NAME']` not `row['column_name']`.

Happy coding in the Seton ecosystem! 🚀
# In Airflow tasks
sheet_id = Variable.get("GOOGLE_SHEET_ID_PROD")

# In local development
sheet_id = os.getenv("GOOGLE_SHEET_ID_DEV")
```

### Key Environment Variables

- `ENVIRONMENT`: `development`, `testing`, or `production`
- `GOOGLE_SHEET_ID_DEV`: Development Google Sheet ID
- `GOOGLE_SHEET_ID_TEST`: Testing Google Sheet ID  
- `GOOGLE_SHEET_ID_PROD`: Production Google Sheet ID
- `GOOGLE_CREDENTIALS_PATH`: Path to service account JSON
- `GITHUB_PAT`: Personal Access Token for seton_utils installation

## 🗄️ Database Integration

### Oracle Column Naming - CRITICAL PATTERN ⚠️

**Oracle returns ALL column names in UPPERCASE**. This is a critical pattern that must be handled correctly:

```python
# ✅ CORRECT - Oracle returns uppercase
student_data = {
    'student_number': row['STUDENT_NUMBER'],  # Note: UPPERCASE key
    'dcid': row['DCID'],
    'last_name': row['LAST_NAME'],
    'relationship': row['RELATIONSHIP']
}

# ❌ WRONG - Will cause KeyError
student_data = {
    'student_number': row['student_number'],  # lowercase won't work
}
```

### Database Connection Pattern

```python
from seton_utils.connect_to_ps import connect_to_ps

def get_student_data():
    conn = connect_to_ps()
    cursor = conn.cursor()
    
    query = """
    SELECT STUDENT_NUMBER, DCID, LAST_NAME, FIRST_NAME
    FROM STUDENTS 
    WHERE ENROLL_STATUS = 0
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    # Process results with UPPERCASE column names
    students = []
    for row in results:
        students.append({
            'student_number': row['STUDENT_NUMBER'],  # UPPERCASE!
            'dcid': row['DCID'],
            'last_name': row['LAST_NAME'],
            'first_name': row['FIRST_NAME']
        })
    
    cursor.close()
    conn.close()
    return students
```

## 📊 Google Sheets Integration

### Credentials Pattern

```python
from seton_utils.gdrive.gdrive_helpers import get_gdrive_credentials

# Works in both Airflow and local development
credentials = get_gdrive_credentials()
```

### Sheet ID Selection

```python
from .config.settings import get_sheet_id

# Automatically selects correct sheet based on environment
sheet_id = get_sheet_id()
```

## 🧪 Testing Framework

The template includes comprehensive testing patterns:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test category
pytest tests/test_database/
```

### Mock Database Fixtures

```python
@pytest.fixture
def mock_db_connection():
    """Mock database connection for testing"""
    # Returns mock data with UPPERCASE column names
    return [
        {'STUDENT_NUMBER': 12345, 'LAST_NAME': 'Smith'},
        {'STUDENT_NUMBER': 67890, 'LAST_NAME': 'Jones'}
    ]
```

## 🚦 CI/CD Integration

### GitHub Actions Workflows

- **CI Pipeline**: Runs tests, linting, and security checks
- **Release Pipeline**: Automated versioning and releases
- **Security Scanning**: Dependency vulnerability checks

## 🔒 Security & Safety

### Production Sheet Protection

The template includes automatic warnings when non-production environments attempt to access production Google Sheets:

```python
def validate_environment_sheet_access():
    env = get_environment()
    sheet_id = get_sheet_id()
    
    if env != 'production' and sheet_id == get_production_sheet_id():
        raise EnvironmentError(
            f"❌ DANGER: {env} environment attempting to access PRODUCTION sheet!"
        )
```

### .gitignore Patterns

The template includes comprehensive .gitignore patterns for:
- Credentials and secrets
- Environment files
- IDE configurations
- Python artifacts
- Local development files

## 📚 Documentation

### Essential Guides

1. **[Oracle Column Naming](docs/oracle_column_naming.md)** - Critical patterns for Oracle database integration
2. **[Configuration Guide](docs/configuration.md)** - Environment and settings management
3. **[Development Guidelines](docs/development.md)** - Best practices and patterns

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For questions or issues:
1. Check the documentation in the `docs/` folder
2. Review existing issues on GitHub
3. Create a new issue with detailed information

---

**Happy coding in the Seton ecosystem! 🎉**
