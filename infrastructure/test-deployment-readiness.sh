#!/bin/bash

# Test Deployment Readiness Script
# Verifies that all prerequisites are met before deploying to AWS

set -e

echo "=========================================="
echo "Deployment Readiness Check"
echo "=========================================="
echo ""

ERRORS=0
WARNINGS=0

# Function to check command existence
check_command() {
    local cmd=$1
    local name=$2
    
    echo -n "Checking $name... "
    if command -v $cmd &> /dev/null; then
        VERSION=$($cmd --version 2>&1 | head -n 1)
        echo "✓ Found ($VERSION)"
        return 0
    else
        echo "✗ NOT FOUND"
        ERRORS=$((ERRORS + 1))
        return 1
    fi
}

# Function to check file existence
check_file() {
    local file=$1
    local description=$2
    
    echo -n "Checking $description... "
    if [ -f "$file" ]; then
        echo "✓ EXISTS"
        return 0
    else
        echo "✗ NOT FOUND"
        ERRORS=$((ERRORS + 1))
        return 1
    fi
}

# Check AWS CLI
echo "=== Prerequisites ==="
check_command "aws" "AWS CLI"
check_command "sam" "AWS SAM CLI"
check_command "python3" "Python 3"
check_command "jq" "jq (JSON processor)" || WARNINGS=$((WARNINGS + 1))

echo ""

# Check AWS credentials
echo "=== AWS Credentials ==="
echo -n "Checking AWS credentials... "
if aws sts get-caller-identity &> /dev/null; then
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    USER_ARN=$(aws sts get-caller-identity --query Arn --output text)
    echo "✓ CONFIGURED"
    echo "  Account: $ACCOUNT_ID"
    echo "  User: $USER_ARN"
else
    echo "✗ NOT CONFIGURED"
    echo "  Run: aws configure"
    ERRORS=$((ERRORS + 1))
fi

echo -n "Checking AWS region... "
REGION=$(aws configure get region 2>/dev/null || echo "")
if [ -n "$REGION" ]; then
    echo "✓ SET ($REGION)"
else
    echo "⚠ NOT SET (will use default)"
    WARNINGS=$((WARNINGS + 1))
fi

echo ""

# Check Lambda handler files
echo "=== Lambda Handler Files ==="
check_file "../src/lambdas/data_fetcher/handler.py" "Data Fetcher handler"
check_file "../src/lambdas/feature_extractor/handler.py" "Feature Extractor handler"
check_file "../src/lambdas/risk_analyzer/handler.py" "Risk Analyzer handler"
check_file "../src/lambdas/report_generator/handler.py" "Report Generator handler"

echo ""

# Check infrastructure files
echo "=== Infrastructure Files ==="
check_file "template.yaml" "SAM template"
check_file "state_machine.json" "Step Functions definition"
check_file "deploy.sh" "Deployment script"
check_file "verify-deployment.sh" "Verification script"

echo ""

# Check common modules
echo "=== Common Modules ==="
check_file "../src/common/models.py" "Data models"
check_file "../src/common/validators.py" "Validators"
check_file "../src/common/rate_limiter.py" "Rate limiter"
check_file "../src/common/aws_clients.py" "AWS clients"

echo ""

# Check utility modules
echo "=== Utility Modules ==="
check_file "../src/utils/bitopro_client.py" "BitoPro client"

echo ""

# Check Python dependencies
echo "=== Python Dependencies ==="
echo -n "Checking boto3... "
if python3 -c "import boto3" 2>/dev/null; then
    echo "✓ INSTALLED"
else
    echo "⚠ NOT INSTALLED"
    echo "  Run: pip install boto3"
    WARNINGS=$((WARNINGS + 1))
fi

echo -n "Checking matplotlib... "
if python3 -c "import matplotlib" 2>/dev/null; then
    echo "✓ INSTALLED"
else
    echo "⚠ NOT INSTALLED (optional for charts)"
    echo "  Run: pip install matplotlib"
    WARNINGS=$((WARNINGS + 1))
fi

echo ""

# Check Bedrock access (if AWS credentials are configured)
if aws sts get-caller-identity &> /dev/null; then
    echo "=== AWS Bedrock Access ==="
    echo -n "Checking Bedrock model access... "
    
    # Try to list foundation models (this will fail if Bedrock is not accessible)
    if aws bedrock list-foundation-models --region ${REGION:-us-east-1} &> /dev/null 2>&1; then
        echo "✓ ACCESSIBLE"
        
        # Check if Claude 3 models are available
        CLAUDE_MODELS=$(aws bedrock list-foundation-models \
            --region ${REGION:-us-east-1} \
            --query 'modelSummaries[?contains(modelId, `claude-3`)].modelId' \
            --output text 2>/dev/null || echo "")
        
        if [ -n "$CLAUDE_MODELS" ]; then
            echo "  Claude 3 models available: ✓"
        else
            echo "  ⚠ Claude 3 models not found - may need to request access"
            WARNINGS=$((WARNINGS + 1))
        fi
    else
        echo "⚠ NOT ACCESSIBLE"
        echo "  Enable Bedrock access in AWS Console:"
        echo "  1. Go to Amazon Bedrock service"
        echo "  2. Navigate to 'Model access'"
        echo "  3. Request access to Claude 3 models"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    echo ""
fi

# Check for existing stack
if aws sts get-caller-identity &> /dev/null; then
    echo "=== Existing Stack Check ==="
    echo -n "Checking for existing stack... "
    
    STACK_STATUS=$(aws cloudformation describe-stacks \
        --stack-name crypto-suspicious-detection \
        --region ${REGION:-us-east-1} \
        --query 'Stacks[0].StackStatus' \
        --output text 2>/dev/null || echo "NOT_FOUND")
    
    if [ "$STACK_STATUS" = "NOT_FOUND" ]; then
        echo "✓ NO EXISTING STACK (fresh deployment)"
    else
        echo "⚠ STACK EXISTS (Status: $STACK_STATUS)"
        echo "  This will be an UPDATE operation"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    echo ""
fi

# Summary
echo "=========================================="
echo "Readiness Check Summary"
echo "=========================================="
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "✓ ALL CHECKS PASSED"
    echo ""
    echo "You are ready to deploy!"
    echo ""
    echo "Next steps:"
    echo "  1. Review the deployment guide: cat DEPLOYMENT_GUIDE.md"
    echo "  2. Run deployment: ./deploy.sh"
    echo "  3. Verify deployment: ./verify-deployment.sh"
    echo ""
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo "⚠ PASSED WITH WARNINGS"
    echo ""
    echo "Warnings: $WARNINGS"
    echo ""
    echo "You can proceed with deployment, but review the warnings above."
    echo ""
    echo "Next steps:"
    echo "  1. Review warnings and fix if needed"
    echo "  2. Run deployment: ./deploy.sh"
    echo "  3. Verify deployment: ./verify-deployment.sh"
    echo ""
    exit 0
else
    echo "✗ FAILED"
    echo ""
    echo "Errors: $ERRORS"
    echo "Warnings: $WARNINGS"
    echo ""
    echo "Please fix the errors above before deploying."
    echo ""
    exit 1
fi
