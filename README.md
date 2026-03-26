<<<<<<< HEAD
# AWS Model Risk Scoring

AWS 模型層與風險評分層是加密貨幣可疑帳戶偵測系統的核心推論引擎，負責將前處理後的交易特徵轉換為可操作的風險評分。

## Overview

This system provides:
- **AWS Native**: Uses Amazon Bedrock Foundation Models and SageMaker for inference
- **Stable Inference**: Implements rate limiting, fallback mechanisms, and error handling
- **Explainability**: Provides risk factor analysis and natural language explanations
- **Flexible Architecture**: Supports both supervised (labeled) and unsupervised (unlabeled) modes
- **Cost Optimization**: Prioritizes Bedrock on-demand to avoid expensive model training

## Project Structure

```
.
├── src/
│   └── model_risk_scoring/
│       ├── models/          # Data models (TransactionFeatures, RiskAssessment, etc.)
│       ├── engines/         # Inference engines (Bedrock, SageMaker, Fallback)
│       ├── utils/           # Utilities (RateLimiter, FeatureProcessor, etc.)
│       └── exceptions/      # Custom exceptions
├── tests/
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests with real AWS services
│   └── property/           # Property-based tests using Hypothesis
├── requirements.txt        # Python dependencies
├── setup.py               # Package setup
└── pytest.ini             # Pytest configuration
```

## Setup

### Prerequisites

- Python 3.11 or higher
- AWS credentials configured (for Bedrock and SageMaker access)

### Installation

#### Linux/macOS

```bash
# Make setup script executable
chmod +x setup_env.sh

# Run setup script
./setup_env.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

#### Windows (PowerShell)

```powershell
# Run setup script
.\setup_env.ps1

# Or manually:
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run unit tests only
pytest -m unit

# Run with coverage report
pytest --cov=src/model_risk_scoring --cov-report=html

# Run property-based tests
pytest -m property
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## MVP Scope

For hackathon deployment (< 4 hours), the MVP includes:
- ✅ Bedrock LLM inference (unsupervised mode)
- ✅ Fallback rule engine
- ✅ Rate limiter (< 1 req/sec)
- ✅ Feature validation
- ✅ Risk level classification
- ✅ S3 storage for results
- ✅ CloudWatch logging

**Deferred for post-MVP:**
- ❌ SageMaker Endpoint integration
- ❌ DynamoDB storage
- ❌ Feature normalization
- ❌ Batch inference optimization

## Architecture

### Inference Modes

1. **UNSUPERVISED** (MVP): Uses Amazon Bedrock LLM (Claude 3 Sonnet) for risk assessment
2. **SUPERVISED** (Post-MVP): Uses SageMaker Endpoint with trained models
3. **FALLBACK**: Rule-based engine when AI services are unavailable

### Risk Levels

- **LOW** (0-25): Normal behavior
- **MEDIUM** (26-50): Moderate risk
- **HIGH** (51-75): High risk, requires investigation
- **CRITICAL** (76-100): Critical risk, immediate action required

## License

Copyright © 2024 Crypto Fraud Detection Team
=======
# AWS Model Risk Scoring

AWS 模型層與風險評分層是加密貨幣可疑帳戶偵測系統的核心推論引擎，負責將前處理後的交易特徵轉換為可操作的風險評分。

## Overview

This system provides:
- **AWS Native**: Uses Amazon Bedrock Foundation Models and SageMaker for inference
- **Stable Inference**: Implements rate limiting, fallback mechanisms, and error handling
- **Explainability**: Provides risk factor analysis and natural language explanations
- **Flexible Architecture**: Supports both supervised (labeled) and unsupervised (unlabeled) modes
- **Cost Optimization**: Prioritizes Bedrock on-demand to avoid expensive model training

## Project Structure

```
.
├── src/
│   └── model_risk_scoring/
│       ├── models/          # Data models (TransactionFeatures, RiskAssessment, etc.)
│       ├── engines/         # Inference engines (Bedrock, SageMaker, Fallback)
│       ├── utils/           # Utilities (RateLimiter, FeatureProcessor, etc.)
│       └── exceptions/      # Custom exceptions
├── tests/
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests with real AWS services
│   └── property/           # Property-based tests using Hypothesis
├── requirements.txt        # Python dependencies
├── setup.py               # Package setup
└── pytest.ini             # Pytest configuration
```

## Setup

### Prerequisites

- Python 3.11 or higher
- AWS credentials configured (for Bedrock and SageMaker access)

### Installation

#### Linux/macOS

```bash
# Make setup script executable
chmod +x setup_env.sh

# Run setup script
./setup_env.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

#### Windows (PowerShell)

```powershell
# Run setup script
.\setup_env.ps1

# Or manually:
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run unit tests only
pytest -m unit

# Run with coverage report
pytest --cov=src/model_risk_scoring --cov-report=html

# Run property-based tests
pytest -m property
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## MVP Scope

For hackathon deployment (< 4 hours), the MVP includes:
- ✅ Bedrock LLM inference (unsupervised mode)
- ✅ Fallback rule engine
- ✅ Rate limiter (< 1 req/sec)
- ✅ Feature validation
- ✅ Risk level classification
- ✅ S3 storage for results
- ✅ CloudWatch logging

**Deferred for post-MVP:**
- ❌ SageMaker Endpoint integration
- ❌ DynamoDB storage
- ❌ Feature normalization
- ❌ Batch inference optimization

## Architecture

### Inference Modes

1. **UNSUPERVISED** (MVP): Uses Amazon Bedrock LLM (Claude 3 Sonnet) for risk assessment
2. **SUPERVISED** (Post-MVP): Uses SageMaker Endpoint with trained models
3. **FALLBACK**: Rule-based engine when AI services are unavailable

### Risk Levels

- **LOW** (0-25): Normal behavior
- **MEDIUM** (26-50): Moderate risk
- **HIGH** (51-75): High risk, requires investigation
- **CRITICAL** (76-100): Critical risk, immediate action required

## License

Copyright © 2024 Crypto Fraud Detection Team
>>>>>>> 3ed03a3 (Initial commit)
