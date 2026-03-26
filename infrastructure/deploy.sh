#!/bin/bash

# Deployment script for Crypto Suspicious Account Detection System
# This script deploys the AWS infrastructure using SAM CLI

set -e

echo "=========================================="
echo "Crypto Suspicious Account Detection"
echo "Infrastructure Deployment"
echo "=========================================="
echo ""

# Check if SAM CLI is installed
if ! command -v sam &> /dev/null; then
    echo "ERROR: AWS SAM CLI is not installed."
    echo "Please install it from: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html"
    exit 1
fi

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "ERROR: AWS CLI is not configured or credentials are invalid."
    echo "Please run 'aws configure' to set up your credentials."
    exit 1
fi

echo "✓ AWS SAM CLI found"
echo "✓ AWS credentials configured"
echo ""

# Get AWS account ID and region
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=$(aws configure get region || echo "us-east-1")

echo "Deploying to:"
echo "  Account: $AWS_ACCOUNT_ID"
echo "  Region: $AWS_REGION"
echo ""

# Build the SAM application
echo "Building SAM application..."
sam build --template-file template.yaml

if [ $? -ne 0 ]; then
    echo "ERROR: SAM build failed"
    exit 1
fi

echo "✓ Build completed"
echo ""

# Deploy the SAM application
echo "Deploying SAM application..."
sam deploy \
    --template-file .aws-sam/build/template.yaml \
    --stack-name crypto-suspicious-detection \
    --capabilities CAPABILITY_NAMED_IAM \
    --region $AWS_REGION \
    --no-fail-on-empty-changeset \
    --resolve-s3

if [ $? -ne 0 ]; then
    echo "ERROR: SAM deploy failed"
    exit 1
fi

echo ""
echo "=========================================="
echo "✓ Deployment completed successfully!"
echo "=========================================="
echo ""

# Get stack outputs
echo "Stack Outputs:"
aws cloudformation describe-stacks \
    --stack-name crypto-suspicious-detection \
    --region $AWS_REGION \
    --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
    --output table

echo ""
echo "IMPORTANT: Update the BitoPro API credentials in Secrets Manager:"
echo "  Secret Name: crypto-suspicious-detection-bitopro-api-key"
echo ""
echo "Run the following command to update the secret:"
echo "  aws secretsmanager update-secret \\"
echo "    --secret-id crypto-suspicious-detection-bitopro-api-key \\"
echo "    --secret-string '{\"api_key\":\"YOUR_API_KEY\",\"api_secret\":\"YOUR_API_SECRET\"}' \\"
echo "    --region $AWS_REGION"
echo ""
