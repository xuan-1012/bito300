"""Setup script for AWS Model Risk Scoring."""

from setuptools import setup, find_packages

setup(
    name="aws-model-risk-scoring",
    version="0.1.0",
    description="AWS Model Risk Scoring - Core inference engine for cryptocurrency fraud detection",
    author="Crypto Fraud Detection Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=[
        "boto3>=1.28.0",
        "botocore>=1.31.0",
        "pydantic>=2.0.0",
        "python-dateutil>=2.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "hypothesis>=6.82.0",
            "moto>=4.1.0",
            "black>=23.7.0",
            "flake8>=6.1.0",
            "mypy>=1.5.0",
        ],
    },
)
