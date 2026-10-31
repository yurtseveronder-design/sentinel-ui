from setuptools import setup, find_packages

setup(
    name="sentinel-ui",
    version="1.0.0",
    description="Enterprise-grade AI security and testing framework",
    author="Enterprise Security Team",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "pytest>=7.0.0",
        "requests>=2.28.0",
        "numpy>=1.22.0",
        "streamlit>=1.24.0",
        "fpdf2>=2.7.0"
    ],
)