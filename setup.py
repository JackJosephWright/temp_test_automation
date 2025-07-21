"""
Setup configuration for temp_test_automation
"""
from setuptools import setup, find_packages

setup(
    name="temp_test_automation",
    version="0.1.0",
    description="A Seton ecosystem package",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
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
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.12",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.910",
        ]
    },
    entry_points={
        "console_scripts": [
            "temp_test_automation=temp_test_automation.main:main",
        ],
    },
)
