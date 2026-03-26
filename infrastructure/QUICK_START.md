# Quick Start Guide

## 1-Minute Setup

```bash
# Install prerequisites (if not already installed)
brew install awscli aws-sam-cli  # macOS
# or use appropriate package manager for your OS

# Configure AWS credentials
aws configure

# Deploy infrastructure
cd infrastructure
chmod +x deploy.sh
./deploy.sh

# Update BitoPro API credentials
aws secretsmanager update-secret \
  --secret-id crypto-suspicious-detection-bitopro-api-key \
  --secret-string '{"api_key":"YOUR_KEY","api_secret":"YOUR_SECRET"}'

# Verify deployment
chmod +x verify-deployment.sh
./verify-deployment.sh
```

## What Gets Deployed

✅ **4 S3 Buckets** (private, encrypted)
- Raw transaction data
- Extracted features
- Risk scores
- Reports and charts

✅ **1 DynamoDB Table** (KMS encrypted)
- Account risk profiles

✅ **4 Lambda Functions** (with IAM roles)
- Data Fetcher
- Feature Extractor
- Risk Analyzer
- Report Generator

✅ **1 Secrets Manager Secret**
- BitoPro API credentials

✅ **4 CloudWatch Log Groups**
- Lambda function logs

## Common Commands

```bash
# View stack outputs
aws cloudformation describe-stacks \
  --stack-name crypto-suspicious-detection \
  --query 'Stacks[0].Outputs'

# Test Lambda function
aws lambda invoke \
  --function-name crypto-suspicious-detection-data-fetcher \
  --payload '{}' response.json

# View logs
aws logs tail /aws/lambda/crypto-suspicious-detection-data-fetcher --follow

# Update infrastructure
cd infrastructure
sam build && sam deploy --no-confirm-changeset

# Delete everything
aws cloudformation delete-stack --stack-name crypto-suspicious-detection
```

## Troubleshooting

**Problem**: SAM CLI not found
```bash
# Install SAM CLI
brew install aws-sam-cli  # macOS
```

**Problem**: Bedrock access denied
```bash
# Enable Bedrock model access in AWS Console
# Go to: Bedrock > Model access > Request access
```

**Problem**: Stack already exists
```bash
# Update existing stack
sam deploy --no-confirm-changeset
```

## Security Compliance

✅ All S3 buckets are private
✅ All data encrypted at rest
✅ API keys in Secrets Manager
✅ IAM least privilege roles
✅ No public resources

## Cost

Estimated: **~$1.12** for 4-hour hackathon

## Next Steps

1. ✅ Infrastructure deployed
2. ⏭️ Implement Lambda code
3. ⏭️ Create Step Functions
4. ⏭️ Test workflow
5. ⏭️ Demo!

For detailed instructions, see [DEPLOYMENT.md](../DEPLOYMENT.md)
