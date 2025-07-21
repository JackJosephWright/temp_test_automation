#!/usr/bin/env python3
"""
Seton Package Template - Development Environment Setup Script

This script automates the creation of a development environment for Seton packages.
It handles virtual environment creation, dependency installation, and configuration.
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path
from typing import Optional


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(message: str):
    """Print a colored header message"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}🚀 {message}{Colors.ENDC}")


def print_success(message: str):
    """Print a success message"""
    print(f"{Colors.GREEN}✅ {message}{Colors.ENDC}")


def print_warning(message: str):
    """Print a warning message"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.ENDC}")


def print_error(message: str):
    """Print an error message"""
    print(f"{Colors.RED}❌ {message}{Colors.ENDC}")


def print_info(message: str):
    """Print an info message"""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.ENDC}")


def run_command(command: str, check: bool = True, capture_output: bool = False) -> Optional[str]:
    """
    Run a shell command with error handling
    
    Returns:
        None: Command succeeded (when capture_output=False)
        str: Command output (when capture_output=True and succeeded)
        "ERROR": Command failed (always when failed)
    """
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, check=check, 
                                  capture_output=True, text=True)
            return result.stdout.strip()
        else:
            subprocess.run(command, shell=True, check=check)
            return None  # Success
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {command}")
        print_error(f"Error: {e}")
        return "ERROR"  # Failure indicator


def check_python_version():
    """Check if Python version is compatible"""
    print_header("Checking Python Version")
    
    version = sys.version_info
    if version < (3, 8):
        print_error(f"Python 3.8+ required. Current version: {version.major}.{version.minor}")
        return False
    
    print_success(f"Python {version.major}.{version.minor}.{version.micro} ✓")
    return True


def get_package_name() -> str:
    """Get package name from user input"""
    print_header("Package Configuration")
    
    # Suggest name based on current directory
    current_dir = Path.cwd().name
    default_name = current_dir if current_dir != "seton_pipeline_template" else "my_seton_package"
    
    while True:
        package_name = input(f"📦 Package name (default: {default_name}): ").strip()
        if not package_name:
            package_name = default_name
        
        # Validate package name
        if package_name.replace('_', '').isalnum():
            print_success(f"Package name: {package_name}")
            return package_name
        else:
            print_error("Package name must contain only letters, numbers, and underscores")


def get_github_pat() -> str:
    """Get GitHub Personal Access Token for seton_utils installation"""
    print_info("GitHub PAT needed to install seton_utils from private repository")
    print_info("Create PAT at: https://github.com/settings/tokens")
    print_info("Required scopes: repo, read:packages")
    
    while True:
        pat = input("🔑 GitHub Personal Access Token: ").strip()
        if pat:
            return pat
        print_error("GitHub PAT is required to install seton_utils")


def create_virtual_environment(package_name: str):
    """Create and activate virtual environment"""
    print_header("Creating Virtual Environment")
    
    venv_name = f"venv_{package_name}"
    
    if Path(venv_name).exists():
        print_warning(f"Virtual environment {venv_name} already exists")
        recreate = input("🔄 Recreate virtual environment? (y/N): ").strip().lower()
        if recreate == 'y':
            print_info(f"Removing existing {venv_name}")
            shutil.rmtree(venv_name)
        else:
            print_info(f"Using existing {venv_name}")
            return venv_name
    
    print_info(f"Creating virtual environment: {venv_name}")
    result = run_command(f"python -m venv {venv_name}")
    if result == "ERROR":  # Failed
        print_error("Failed to create virtual environment")
        return None
    
    print_success(f"Virtual environment created: {venv_name}")
    return venv_name


def get_venv_python(venv_name: str) -> str:
    """Get path to Python executable in virtual environment"""
    if os.name == 'nt':  # Windows
        return f"{venv_name}\\Scripts\\python.exe"
    else:  # Unix/Linux/macOS
        return f"{venv_name}/bin/python"


def install_dependencies(venv_python: str, github_pat: str):
    """Install package dependencies with improved error handling"""
    print_header("Installing Dependencies")
    
    # First, verify the virtual environment Python exists
    print_info(f"Checking virtual environment Python: {venv_python}")
    if not Path(venv_python).exists():
        print_error(f"Virtual environment Python not found at: {venv_python}")
        print_info("Available files in virtual environment:")
        venv_dir = Path(venv_python).parent
        if venv_dir.exists():
            for file in venv_dir.iterdir():
                print_info(f"  - {file.name}")
        return False
    
    print_success(f"Virtual environment Python found: {venv_python}")
    
    # Upgrade pip first
    print_info("Upgrading pip...")
    result = run_command(f'"{venv_python}" -m pip install --upgrade pip')
    if result == "ERROR":  # run_command returns "ERROR" on failure, None on success
        print_error("Failed to upgrade pip")
        return False
    
    # Clear pip cache to avoid cached source distributions
    print_info("Clearing pip cache to ensure fresh wheel downloads...")
    result = run_command(f'"{venv_python}" -m pip cache purge')
    if result == "ERROR":
        print_warning("Failed to clear pip cache - continuing anyway")
    
    # Install pandas (use modern versions compatible with Python 3.12)
    print_info("Installing pandas (using modern versions for Python 3.12+ compatibility)...")
    
    # Check Python version to determine pandas strategy
    python_version = sys.version_info
    if python_version >= (3, 12):
        print_info("Python 3.12+ detected - using modern pandas versions...")
        # Use current pandas versions available for Python 3.12
        result = run_command(f'"{venv_python}" -m pip install pandas --only-binary=pandas --no-cache-dir')
        if result == "ERROR":
            print_warning("Latest pandas wheel failed, trying specific version...")
            result = run_command(f'"{venv_python}" -m pip install "pandas>=2.1.0" --only-binary=pandas --no-cache-dir')
    else:
        print_info("Using pandas version range for older Python...")
        # For older Python versions, try the legacy constraint first, then modern
        result = run_command(f'"{venv_python}" -m pip install "pandas>=1.3.0,<2.1.0" --only-binary=pandas --no-cache-dir')
        if result == "ERROR":
            print_warning("Legacy pandas constraint failed, trying modern versions...")
            result = run_command(f'"{venv_python}" -m pip install pandas --only-binary=pandas --no-cache-dir')
    
    if result == "ERROR":
        print_error("❌ All pandas wheel installations failed!")
        print_error("💡 This means no precompiled wheels are available for:")
        print_error(f"   • Your Python version: {sys.version}")
        print_error(f"   • Your platform: {sys.platform}")
        print_error("")
        print_error("🔧 Solutions:")
        print_error("1. Install Visual C++ Build Tools:")
        print_error("   https://visualstudio.microsoft.com/visual-cpp-build-tools/")
        print_error("")
        print_error("2. Use conda instead:")
        print_error("   conda install pandas")
        print_error("")
        print_error("3. Manual installation with compilation:")
        print_error(f'   {venv_python} -m pip install pandas --no-binary=pandas')
        
        # Ask user if they want to try with compilation
        print_warning("")
        try_build = input("🤔 Try installing pandas with compilation anyway? (y/N): ").strip().lower()
        if try_build == 'y':
            print_info("Attempting pandas installation with compilation (this may take 10+ minutes)...")
            result = run_command(f'"{venv_python}" -m pip install pandas --no-binary=pandas')
            if result == "ERROR":
                print_error("Compilation failed - you need Visual C++ Build Tools")
                return False
            else:
                print_success("✅ pandas installed via compilation")
        else:
            print_error("Setup aborted - pandas is required")
            return False
    else:
        print_success("✅ pandas installed successfully (wheel)")
    
    # Verify pandas installation and check version
    print_info("Verifying pandas installation...")
    verify_cmd = f'''"{venv_python}" -c "
import pandas as pd
print(f'pandas version: {{pd.__version__}}')
print('✅ pandas ready for oracledb integration')
"'''
    
    result = run_command(verify_cmd)
    if result == "ERROR":
        print_error("pandas installation verification failed")
        return False
    
    # Install seton_utils from private repository
    print_info("Installing seton_utils from private repository...")
    print_info("Note: This may trigger seton_utils to update its pandas constraint")
    seton_utils_url = f"git+https://{github_pat}@github.com/JackJosephWright/seton_utils.git"
    
    # Install without --no-deps to let seton_utils handle its dependencies normally
    result = run_command(f'"{venv_python}" -m pip install {seton_utils_url} --no-cache-dir')
    if result == "ERROR":
        print_error("Failed to install seton_utils")
        print_warning("This might be due to pandas version conflicts in seton_utils setup.py")
        print_warning("Check your GitHub PAT has correct permissions:")
        print_warning("  - PAT must have 'repo' and 'read:packages' scopes")
        print_warning("  - PAT must not be expired")
        print_warning("  - Check network/VPN connectivity")
        print_info("💡 Manual installation command:")
        print_info(f"   {venv_python} -m pip install {seton_utils_url}")
        print_info("💡 If pandas version conflict, update seton_utils setup.py to allow modern pandas")
        return False
    
    print_success("✅ seton_utils installed successfully")
    
    # Install remaining dependencies (most should already be satisfied by seton_utils)
    print_info("Installing any remaining dependencies...")
    remaining_deps = [
        "openpyxl", "google-auth-httplib2", "google-api-python-client",
        "pydantic", "structlog", "pyyaml", "python-dateutil", "tenacity", "orjson", "tqdm"
    ]
    
    for dep in remaining_deps:
        print_info(f"Installing {dep}...")
        result = run_command(f'"{venv_python}" -m pip install {dep} --prefer-binary')
        if result == "ERROR":
            print_warning(f"Failed to install {dep}, continuing with others...")
    
    # oracledb should already be installed by seton_utils, but verify
    print_info("Verifying Oracle connectivity (oracledb)...")
    verify_oracle = f'"{venv_python}" -c "import oracledb; print(f\'oracledb version: {{oracledb.__version__}}\')"'
    result = run_command(verify_oracle)
    
    if result == "ERROR":
        print_info("Installing oracledb manually...")
        result = run_command(f'"{venv_python}" -m pip install oracledb --prefer-binary')
        if result == "ERROR":
            print_warning("❌ oracledb installation failed")
            print_info("📋 Oracle database features will be disabled")
        else:
            print_success("✅ oracledb installed successfully")
    else:
        print_success("✅ oracledb already available")
    
    # Install development dependencies
    print_info("Installing development dependencies...")
    result = run_command(f'"{venv_python}" -m pip install -r requirements-dev.txt --prefer-binary')
    if result == "ERROR":  # Failed
        print_warning("Some development dependencies failed - continuing anyway")
    
    print_success("✅ Dependencies installation completed")
    return True


def customize_template(package_name: str):
    """Customize template files with package name"""
    print_header("Customizing Template")
    
    # Create package directory structure
    src_dir = Path("src")
    package_dir = src_dir / package_name
    
    if package_dir.exists():
        print_warning(f"Package directory {package_dir} already exists")
    else:
        print_info(f"Creating package directory: {package_dir}")
        package_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        subdirs = ["config", "database", "google_sheets", "utils"]
        for subdir in subdirs:
            (package_dir / subdir).mkdir(exist_ok=True)
            (package_dir / subdir / "__init__.py").touch()
    
    # Update setup.py with package name
    setup_py_content = f'''"""
Setup configuration for {package_name}
"""
from setuptools import setup, find_packages

setup(
    name="{package_name}",
    version="0.1.0",
    description="A Seton ecosystem package",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(where="src"),
    package_dir={{"": "src"}},
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "openpyxl>=3.0.9",
        "google-auth>=2.0.0",
        "google-auth-oauthlib>=0.5.0",
        "google-auth-httplib2>=0.1.0",
        "google-api-python-client>=2.0.0",
        "gspread>=5.0.0",
        "cx_Oracle>=8.3.0",
    ],
    extras_require={{
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.12",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.910",
        ]
    }},
    entry_points={{
        "console_scripts": [
            "{package_name}={package_name}.main:main",
        ],
    }},
)
'''
    
    with open("setup.py", "w") as f:
        f.write(setup_py_content)
    
    print_success("Template customized successfully")


def create_env_file():
    """Create .env file from template"""
    print_header("Creating Environment Configuration")
    
    if Path(".env").exists():
        print_warning(".env file already exists")
        overwrite = input("🔄 Overwrite existing .env file? (y/N): ").strip().lower()
        if overwrite != 'y':
            print_info("Keeping existing .env file")
            return
    
    # Copy .env.example to .env
    if Path(".env.example").exists():
        shutil.copy(".env.example", ".env")
        print_success("Environment file created from template")
        print_info("Edit .env file to configure your specific settings")
    else:
        print_warning(".env.example not found, creating basic .env file")
        env_content = """# Seton Package Environment Configuration
ENVIRONMENT=development

# Google Sheets Configuration
GOOGLE_SHEET_ID_DEV=your_dev_sheet_id_here
GOOGLE_SHEET_ID_TEST=your_test_sheet_id_here
GOOGLE_SHEET_ID_PROD=your_prod_sheet_id_here

# Google Credentials
GOOGLE_CREDENTIALS_PATH=path/to/service-account.json

# GitHub Configuration (for CI/CD)
GITHUB_PAT=your_github_pat_here
"""
        with open(".env", "w") as f:
            f.write(env_content)
        print_success("Basic .env file created")


def validate_installation(venv_python: str, package_name: str):
    """Validate the installation with enhanced troubleshooting"""
    print_header("Validating Installation")
    
    # Test seton_utils import with enhanced error reporting
    print_info("Testing seton_utils import...")
    test_import = f"{venv_python} -c \"import seton_utils; print('seton_utils version:', seton_utils.__version__ if hasattr(seton_utils, '__version__') else 'imported successfully')\""
    
    result = run_command(test_import)
    if result is not None:
        print_error("seton_utils import failed")
        print_warning("Troubleshooting seton_utils installation:")
        
        # Check if seton_utils is installed
        check_installed = f"{venv_python} -m pip list | findstr seton" if os.name == 'nt' else f"{venv_python} -m pip list | grep seton"
        if run_command(check_installed) is not None:
            print_info("seton_utils not found in pip list - installation failed")
            print_info("Manual installation steps:")
            print_info("1. Activate virtual environment:")
            venv_activate = f"{Path.cwd()}/{'venv_' + package_name}/Scripts/activate" if os.name == 'nt' else f"source {Path.cwd()}/{'venv_' + package_name}/bin/activate"
            print_info(f"   {venv_activate}")
            print_info("2. Install seton_utils manually:")
            print_info("   pip install git+https://YOUR_PAT@github.com/JackJosephWright/seton_utils.git")
            print_info("3. Verify GitHub PAT permissions:")
            print_info("   - Visit: https://github.com/settings/tokens")
            print_info("   - Ensure PAT has 'repo' and 'read:packages' scopes")
            print_info("   - Check PAT expiration date")
        else:
            print_info("seton_utils is installed but import failed - checking dependencies...")
            # Check for missing dependencies
            missing_deps = f"{venv_python} -c \"import sys; missing=[]; deps=['pandas','cx_Oracle','gspread']; [missing.append(d) if __import__(d) else None for d in deps]; print('Missing:', missing) if missing else print('All deps OK')\""
            run_command(missing_deps)
        
        return False
    
    print_success("seton_utils import successful")
    
    # Test package structure
    print_info("Validating package structure...")
    required_files = [
        "src",
        "tests", 
        "requirements.txt",
        "requirements-dev.txt",
        ".env",
        "setup.py"
    ]
    
    all_files_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print_success(f"✓ {file_path}")
        else:
            print_error(f"✗ {file_path}")
            all_files_exist = False
    
    if not all_files_exist:
        return False
    
    # Test basic imports (optional - don't fail if these don't work)
    print_info("Testing basic package imports...")
    basic_tests = [
        f"{venv_python} -c \"import pandas; print('pandas OK')\"",
        f"{venv_python} -c \"import gspread; print('gspread OK')\"",
        f"{venv_python} -c \"import pydantic; print('pydantic OK')\"",
    ]
    
    for test in basic_tests:
        if run_command(test) is not None:
            print_warning("Some imports failed - this may affect functionality")
            break
    else:
        print_success("Basic imports successful")
    
    return True


def print_next_steps(package_name: str, venv_name: str, validation_success: bool = True):
    """Print next steps for the user"""
    print_header("Setup Complete! 🎉")
    
    activation_cmd = f"{venv_name}\\Scripts\\activate" if os.name == 'nt' else f"source {venv_name}/bin/activate"
    
    if validation_success:
        status_msg = f"{Colors.GREEN}Your Seton package '{package_name}' is ready for development!{Colors.ENDC}"
    else:
        status_msg = f"{Colors.YELLOW}Your Seton package '{package_name}' is set up, but some issues were detected.{Colors.ENDC}"
    
    print(f"""
{status_msg}

{Colors.BOLD}Next Steps:{Colors.ENDC}

1. {Colors.BLUE}Activate your virtual environment:{Colors.ENDC}
   {activation_cmd}

2. {Colors.BLUE}Edit your .env file:{Colors.ENDC}
   - Add your Google Sheet IDs
   - Configure Google credentials path
   - Set your environment preferences

3. {Colors.BLUE}Start developing:{Colors.ENDC}
   - Main entry point: src/{package_name}/main.py
   - Configuration: src/{package_name}/config/settings.py
   - Database queries: src/{package_name}/database/queries.py

4. {Colors.BLUE}Run tests:{Colors.ENDC}
   pytest

5. {Colors.BLUE}Key Documentation:{Colors.ENDC}
   - docs/oracle_column_naming.md (CRITICAL!)
   - docs/configuration.md
   - docs/development.md
""")

    if not validation_success:
        print(f"""
{Colors.YELLOW}⚠️  Installation Issues Detected:{Colors.ENDC}

{Colors.BLUE}If seton_utils import failed:{Colors.ENDC}
1. Run the troubleshooting script:
   python test_seton_utils.py

2. Manual installation:
   {activation_cmd}
   pip install git+https://YOUR_PAT@github.com/JackJosephWright/seton_utils.git

3. Check GitHub PAT permissions:
   - Visit: https://github.com/settings/tokens
   - Ensure 'repo' and 'read:packages' scopes

{Colors.BLUE}For build issues (cx_Oracle, pandas):{Colors.ENDC}
- Install Visual C++ Build Tools
- Or use precompiled wheels: pip install --only-binary=all cx_Oracle
""")

    print(f"""
{Colors.YELLOW}Remember: Oracle returns UPPERCASE column names!{Colors.ENDC}

{Colors.GREEN}Happy coding in the Seton ecosystem! 🚀{Colors.ENDC}
""")


def main():
    """Main setup function"""
    print_header("Seton Package Template Setup")
    print("This script will set up a complete development environment for your Seton package.\n")
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    # Get configuration
    package_name = get_package_name()
    github_pat = get_github_pat()
    
    # Create virtual environment
    venv_name = create_virtual_environment(package_name)
    if not venv_name:
        sys.exit(1)
    
    venv_python = get_venv_python(venv_name)
    
    # Install dependencies
    if not install_dependencies(venv_python, github_pat):
        sys.exit(1)
    
    # Customize template
    customize_template(package_name)
    
    # Create environment file
    create_env_file()
    
    # Validate installation
    validation_success = validate_installation(venv_python, package_name)
    if not validation_success:
        print_warning("Installation completed with some issues")
    
    # Print next steps
    print_next_steps(package_name, venv_name, validation_success)


if __name__ == "__main__":
    main()
