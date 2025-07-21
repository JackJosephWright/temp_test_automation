#!/usr/bin/env python3
"""
Enhanced seton_utils validation script for debugging installation issues.

This script provides detailed diagnostics for seton_utils installation problems.
Run this script to troubleshoot import errors and validate your installation.
"""

import sys
import subprocess
from pathlib import Path


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*50}")
    print(f"🔍 {title}")
    print('='*50)


def run_pip_command(command):
    """Run a pip command and return the result"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True
        )
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1


def check_python_environment():
    """Check Python environment details"""
    print_section("Python Environment")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Current working directory: {Path.cwd()}")
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Running in virtual environment")
    else:
        print("⚠️  Not running in virtual environment")


def check_pip_packages():
    """Check installed packages"""
    print_section("Installed Packages")
    
    stdout, stderr, returncode = run_pip_command("pip list")
    if returncode == 0:
        # Look for seton-related packages
        lines = stdout.split('\n')
        seton_packages = [line for line in lines if 'seton' in line.lower()]
        
        if seton_packages:
            print("✅ Seton-related packages found:")
            for pkg in seton_packages:
                print(f"   {pkg}")
        else:
            print("❌ No seton-related packages found")
            
        # Look for key dependencies
        key_deps = ['pandas', 'gspread', 'oracledb', 'pydantic', 'structlog']
        print("\n📦 Key dependencies:")
        for dep in key_deps:
            dep_lines = [line for line in lines if dep.lower() in line.lower()]
            if dep_lines:
                print(f"   ✅ {dep_lines[0]}")
            else:
                if dep == 'oracledb':
                    print(f"   ⚠️  {dep} not found (Oracle connectivity disabled)")
                    print(f"      💡 To install: pip install oracledb")
                    print(f"      📋 Modern Oracle driver (replaces cx_Oracle)")
                else:
                    print(f"   ❌ {dep} not found")
    else:
        print(f"❌ Failed to get pip list: {stderr}")


def test_seton_utils_import():
    """Test seton_utils import with detailed error reporting"""
    print_section("seton_utils Import Test")
    
    try:
        import seton_utils
        print("✅ seton_utils imported successfully")
        
        # Try to get version info
        version = getattr(seton_utils, '__version__', 'No version available')
        print(f"📋 Version: {version}")
        
        # Test specific module imports
        modules_to_test = [
            ('seton_utils.connect_to_ps', 'connect_to_ps'),
            ('seton_utils.gdrive.gdrive_helpers', 'get_gdrive_credentials'),
        ]
        
        print("\n🧪 Testing specific modules:")
        for module_name, function_name in modules_to_test:
            try:
                module = __import__(module_name, fromlist=[function_name])
                getattr(module, function_name)
                print(f"   ✅ {module_name}.{function_name}")
            except ImportError as e:
                print(f"   ❌ {module_name}.{function_name}: {e}")
            except AttributeError as e:
                print(f"   ⚠️  {module_name} imported but {function_name} not found: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ seton_utils import failed: {e}")
        print("\n🔧 Possible causes:")
        print("   1. seton_utils not installed")
        print("   2. Wrong virtual environment")
        print("   3. Installation failed due to missing dependencies")
        return False
    
    except Exception as e:
        print(f"❌ Unexpected error importing seton_utils: {e}")
        return False


def provide_troubleshooting_steps():
    """Provide troubleshooting steps"""
    print_section("Troubleshooting Steps")
    
    print("🔧 Manual Installation Steps:")
    print("1. Ensure you have a valid GitHub PAT with 'repo' and 'read:packages' permissions")
    print("2. Install seton_utils manually:")
    print("   pip install git+https://YOUR_PAT@github.com/JackJosephWright/seton_utils.git")
    print("")
    print("3. If installation fails due to build issues:")
    print("   pip install --no-deps git+https://YOUR_PAT@github.com/JackJosephWright/seton_utils.git")
    print("   pip install pandas gspread pydantic structlog python-dateutil")
    print("")
    print("4. For Oracle database connectivity (oracledb):")
    print("   - Install modern Oracle driver: pip install oracledb")
    print("   - Replaces legacy cx_Oracle (no build tools needed!)")
    print("   - Works with Oracle Instant Client or full Oracle Client")
    print("   - Note: Most Oracle features work without local Oracle install")
    print("")
    print("5. If you need legacy cx_Oracle (not recommended):")
    print("   - Install Microsoft Visual C++ Build Tools first")
    print("   - Link: https://visualstudio.microsoft.com/visual-cpp-build-tools/")
    print("   - Then: pip install cx_Oracle")
    print("")
    print("5. For other Windows build issues:")
    print("   - Use: pip install --only-binary=all PACKAGE_NAME")
    print("   - This forces precompiled wheels instead of building from source")
    print("")
    print("🔗 Useful Links:")
    print("   - GitHub PAT creation: https://github.com/settings/tokens")
    print("   - Visual C++ Build Tools: https://visualstudio.microsoft.com/visual-cpp-build-tools/")
    print("   - Oracle Instant Client: https://www.oracle.com/database/technologies/instant-client.html")


def main():
    """Main validation function"""
    print("🚀 seton_utils Installation Validator")
    print("This script will help diagnose seton_utils installation issues.")
    
    # Run all checks
    check_python_environment()
    check_pip_packages()
    
    success = test_seton_utils_import()
    
    if not success:
        provide_troubleshooting_steps()
        return 1
    else:
        print_section("Success!")
        print("✅ seton_utils is properly installed and working!")
        print("🎉 You're ready to develop with the Seton ecosystem!")
        return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
