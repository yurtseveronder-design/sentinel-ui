"""
sentinel-ui: setup.py
Package installation configuration for the enterprise AI security and testing framework.
"""

from setuptools import setup, find_packages

setup(
    name="sentinel-ui",
    version="1.0.0",
    description="Professional enterprise AI security guardrails, vector RAG, and testing toolkit",
    author="Onder Yurtsever",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "email-validator>=2.0.0",
        "pytest>=7.0.0",
    ],
)