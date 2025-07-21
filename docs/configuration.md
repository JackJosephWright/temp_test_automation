# Configuration Guide

This guide explains the sophisticated configuration system used in Seton packages that automatically adapts between Airflow and local development environments.

## Configuration System Overview

The Seton package template provides a smart configuration system that:

1. **Auto-detects execution environment** (Airflow vs local)
2. **Chooses appropriate variable sources** (Airflow Variables vs environment variables)
3. **Provides environment-based configuration** (dev/test/prod)
4. **Includes safety validations** to prevent production data corruption
5. **Handles credential management** seamlessly

## Environment Detection

```python
from seton_package_template.config.settings import is_airflow_environment

if is_airflow_environment():
    print("Running in Airflow")
else:
    print("Running locally")
```

The system detects Airflow by checking:
- Airflow-specific environment variables (`AIRFLOW_HOME`, etc.)
- Availability of Airflow `Variable` module
- Ability to access Airflow Variable store

## Variable Resolution Pattern

The core pattern automatically chooses the right variable source:

```python
from seton_package_template.config.settings import get_variable

# Automatically uses Airflow Variable.get() or os.getenv()
sheet_id = get_variable("GOOGLE_SHEET_ID_PROD")
log_level = get_variable("LOG_LEVEL", "INFO")  # With default
```

### In Airflow Environment
```python
# Uses Airflow Variable.get()
Variable.get("GOOGLE_SHEET_ID_PROD")
```

### In Local Development
```python
# Uses os.getenv()
os.getenv("GOOGLE_SHEET_ID_PROD")
```

## Environment Configuration

### Setting Your Environment

Create a `.env` file (copied from `.env.example`):

```bash
# Set your environment
ENVIRONMENT=development  # or testing, production

# Configure sheet IDs for each environment
GOOGLE_SHEET_ID_DEV=your_dev_sheet_id_here
GOOGLE_SHEET_ID_TEST=your_test_sheet_id_here
GOOGLE_SHEET_ID_PROD=your_production_sheet_id_here

# Google credentials
GOOGLE_CREDENTIALS_PATH=path/to/service-account.json

# Optional: GitHub PAT for seton_utils installation
GITHUB_PAT=your_github_token_here
```

### Environment-Based Sheet Selection

The system automatically selects the correct Google Sheet based on environment:

```python
from seton_package_template.config.settings import get_sheet_id, get_environment

environment = get_environment()  # "development", "testing", or "production"
sheet_id = get_sheet_id()        # Automatically selects correct sheet ID

# development -> GOOGLE_SHEET_ID_DEV
# testing     -> GOOGLE_SHEET_ID_TEST
# production  -> GOOGLE_SHEET_ID_PROD
```

## Safety Features

### Production Sheet Protection

The system prevents non-production environments from accidentally accessing production sheets:

```python
from seton_package_template.config.settings import validate_environment_sheet_access

# This will raise an error if dev/test environment tries to access prod sheet
validate_environment_sheet_access()
```

Example error:
```
🚨 CRITICAL SAFETY ERROR 🚨
Environment 'development' is attempting to access PRODUCTION Google Sheet!
Current sheet ID: production_sheet_id_here
Production sheet ID: production_sheet_id_here
This could result in production data corruption.
Please check your environment configuration.
```

### Comprehensive Environment Validation

```python
from seton_package_template.config.settings import validate_environment

# Validates:
# - Required environment variables are set
# - Environment/sheet access safety
# - Google credentials configuration
# - Configuration consistency
validate_environment()
```

## Airflow Configuration

### Setting Up Airflow Variables

In Airflow, set these variables through the UI or CLI:

```bash
# Sheet IDs
airflow variables set GOOGLE_SHEET_ID_DEV "dev_sheet_id_12345"
airflow variables set GOOGLE_SHEET_ID_TEST "test_sheet_id_67890"
airflow variables set GOOGLE_SHEET_ID_PROD "prod_sheet_id_abcdef"

# Environment setting
airflow variables set ENVIRONMENT "production"

# Google credentials (as JSON string or file path)
airflow variables set GOOGLE_CREDENTIALS_PATH "/opt/airflow/credentials/service-account.json"
```

### Airflow DAG Example

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

from seton_package_template.main import main

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'seton_package_workflow',
    default_args=default_args,
    description='Seton package data workflow',
    schedule_interval='0 6 * * *',  # Daily at 6 AM
    catchup=False
)

# The main function automatically adapts to Airflow context
run_task = PythonOperator(
    task_id='run_seton_package',
    python_callable=main,  # No changes needed!
    dag=dag
)
```

## Local Development Configuration

### .env File Setup

```bash
# Development environment
ENVIRONMENT=development

# Sheet IDs (use dev/test sheets)
GOOGLE_SHEET_ID_DEV=1abc...dev_sheet_id
GOOGLE_SHEET_ID_TEST=1def...test_sheet_id
GOOGLE_SHEET_ID_PROD=1ghi...prod_sheet_id

# Google credentials - choose one method:

# Method 1: File path
GOOGLE_CREDENTIALS_PATH=/path/to/service-account.json

# Method 2: JSON string (for CI/CD)
GOOGLE_CREDENTIALS_JSON={"type":"service_account","project_id":"..."}

# Logging
LOG_LEVEL=DEBUG
LOG_FORMAT=detailed

# Optional: Override database settings (usually not needed)
# DATABASE_HOST=custom_host
# DATABASE_PORT=1521
```

### IDE/VS Code Setup

Add to your VS Code settings.json:
```json
{
    "python.envFile": "${workspaceFolder}/.env",
    "python.terminal.activateEnvironment": true
}
```

## Credential Management

### Google Credentials

The system supports multiple credential methods:

1. **Service Account File** (recommended for local dev):
   ```bash
   GOOGLE_CREDENTIALS_PATH=/path/to/service-account.json
   ```

2. **JSON String** (recommended for CI/CD):
   ```bash
   GOOGLE_CREDENTIALS_JSON='{"type":"service_account",...}'
   ```

3. **Airflow Variables** (for Airflow environment):
   ```python
   # Set in Airflow UI or CLI
   Variable.set("GOOGLE_CREDENTIALS_PATH", "/opt/airflow/creds/service-account.json")
   ```

### seton_utils Integration

Credentials are handled automatically by seton_utils:

```python
from seton_utils.gdrive.gdrive_helpers import get_gdrive_credentials

# Works in both Airflow and local development
credentials = get_gdrive_credentials()
```

## Configuration Best Practices

### 1. Environment Separation

Always use separate Google Sheets for each environment:
- **Development**: For local testing and development
- **Testing**: For automated testing and staging
- **Production**: For live data operations

### 2. Credential Security

- ✅ Use service account credentials
- ✅ Never commit credentials to git
- ✅ Use environment variables or Airflow Variables
- ✅ Rotate credentials regularly
- ❌ Never hardcode credentials in source code

### 3. Environment Validation

Always call validation at the start of your main function:
```python
def main():
    validate_environment()  # Critical safety check
    # ... rest of your code
```

### 4. Logging Configuration

```python
# Get current settings for debugging
from seton_package_template.config.settings import get_all_settings

settings = get_all_settings()
logger.info(f"Current configuration: {settings}")
```

## Troubleshooting

### Common Issues

1. **KeyError on Variable Access**:
   ```python
   # Check if variable exists
   value = get_variable("MY_VAR")
   if value is None:
       print("Variable MY_VAR is not set")
   ```

2. **Environment Detection Issues**:
   ```python
   # Debug environment detection
   from seton_package_template.config.settings import is_airflow_environment
   print(f"Airflow detected: {is_airflow_environment()}")
   ```

3. **Credential Issues**:
   ```python
   # Test credential access
   from seton_utils.gdrive.gdrive_helpers import get_gdrive_credentials
   try:
       credentials = get_gdrive_credentials()
       print("Credentials loaded successfully")
   except Exception as e:
       print(f"Credential error: {e}")
   ```

### Debug Commands

```python
# Check all configuration
from seton_package_template.config.settings import get_all_settings
print(get_all_settings())

# Test environment validation
from seton_package_template.config.settings import validate_environment
validate_environment()

# Check specific variables
from seton_package_template.config.settings import get_variable
print(f"Environment: {get_variable('ENVIRONMENT')}")
print(f"Sheet ID: {get_variable('GOOGLE_SHEET_ID_DEV')}")
```

## Migration Guide

### From Manual Configuration

If you have existing Seton packages with manual configuration:

1. **Replace manual environment checks** with `is_airflow_environment()`
2. **Replace direct Variable.get() calls** with `get_variable()`
3. **Add environment validation** with `validate_environment()`
4. **Set up .env file** for local development
5. **Add safety validations** with `validate_environment_sheet_access()`

### Before:
```python
# Old manual pattern
try:
    from airflow.models import Variable
    sheet_id = Variable.get("GOOGLE_SHEET_ID")
except:
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
```

### After:
```python
# New template pattern
from seton_package_template.config.settings import get_variable
sheet_id = get_variable("GOOGLE_SHEET_ID")
```

This configuration system ensures robust, safe, and maintainable Seton packages that work seamlessly across all deployment environments.
