#!/bin/bash

# Integration test runner for Step Functions workflow
# This script runs integration tests against AWS or LocalStack

set -e

echo "=========================================="
echo "Step Functions Integration Tests"
echo "=========================================="
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "ERROR: pytest is not installed."
    echo "Please install it: pip install pytest pytest-cov moto boto3"
    exit 1
fi

echo "✓ pytest found"
echo ""

# Determine test environment
if [ "$1" == "aws" ]; then
    echo "Running tests against AWS..."
    TEST_ENV="aws"
    
    # Check if AWS CLI is configured
    if ! aws sts get-caller-identity &> /dev/null; then
        echo "ERROR: AWS CLI is not configured or credentials are invalid."
        echo "Please run 'aws configure' to set up your credentials."
        exit 1
    fi
    
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    AWS_REGION=$(aws configure get region || echo "us-east-1")
    
    echo "  Account: $AWS_ACCOUNT_ID"
    echo "  Region: $AWS_REGION"
    echo ""
    
    # Run integration tests (not skipped)
    pytest tests/integration/test_step_functions_workflow.py \
        -v \
        -m integration \
        --tb=short \
        --color=yes
    
elif [ "$1" == "localstack" ]; then
    echo "Running tests against LocalStack..."
    TEST_ENV="localstack"
    
    # Check if LocalStack is running
    if ! curl -s http://localhost:4566/_localstack/health > /dev/null; then
        echo "ERROR: LocalStack is not running."
        echo "Please start LocalStack: localstack start"
        exit 1
    fi
    
    echo "✓ LocalStack is running"
    echo ""
    
    # Set LocalStack endpoint
    export AWS_ENDPOINT_URL=http://localhost:4566
    export AWS_ACCESS_KEY_ID=test
    export AWS_SECRET_ACCESS_KEY=test
    export AWS_DEFAULT_REGION=us-east-1
    
    # Run integration tests
    pytest tests/integration/test_step_functions_workflow.py \
        -v \
        -m integration \
        --tb=short \
        --color=yes
    
else
    echo "Running unit tests only (no AWS/LocalStack required)..."
    TEST_ENV="unit"
    
    # Run unit tests (skip integration tests)
    pytest tests/integration/test_step_functions_workflow.py \
        -v \
        -m "not integration" \
        --tb=short \
        --color=yes \
        --cov=src \
        --cov-report=term-missing
fi

echo ""
echo "=========================================="
echo "✓ Tests completed successfully!"
echo "=========================================="
echo ""

# Print summary
if [ "$TEST_ENV" == "unit" ]; then
    echo "Summary:"
    echo "  - Unit tests: PASSED"
    echo "  - Integration tests: SKIPPED (use './run_integration_tests.sh aws' or './run_integration_tests.sh localstack')"
elif [ "$TEST_ENV" == "aws" ]; then
    echo "Summary:"
    echo "  - Integration tests against AWS: PASSED"
elif [ "$TEST_ENV" == "localstack" ]; then
    echo "Summary:"
    echo "  - Integration tests against LocalStack: PASSED"
fi

echo ""
