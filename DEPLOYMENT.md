# Deployment Guide - Crypto Suspicious Account Detection

This guide provides step-by-step instructions for deploying the infrastructure for the Crypto Suspicious Account Detection system.

## Prerequisites

### 1. Install Required Tools

#### AWS CLI
```bash
# macOS
brew install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Windows
# Download and run: https://awscli.amazonaws.com/AWSCLIV2.msi

# Verify installation
aws --version
```

#### AWS SAM CLI
```bash
# macOS
brew install aws-sam-cli

# Linux
wget https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-x86_64.zip
unzip aws-sam-cli-linux-x86_64.zip -d sam-installation
sudo ./sam-installation/install

# Windows
# Download and run: https://github.com/aws/aws-sam-cli/releases/latest/download/AWS_SAM_CLI_64_PY3.msi

# Verify installation
sam --version
```

### 2. Configure AWS Credentials

```bash
# Configure AWS CLI with your credentials
aws configure

# You will be prompted for:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region name (e.g., us-east-1)
# - Default output format (json)

# Verify configuration
aws sts get-caller-identity
```

### 3. Enable AWS Bedrock Model Access

1. Log in to AWS Console
2. Navigate to Amazon Bedrock service
3. Go to "Model access" in the left sidebar
4. Click "Manage model access"
5. Select the following models:
   - Anthropic Claude 3 Sonnet
   - Anthropic Claude 3 Haiku
6. Click "Request model access"
7. Wait for approval (usually instant for these models)

## Deployment Steps

### Step 1: Clone and Navigate to Project

```bash
cd /path/to/crypto-suspicious-account-detection
```

### Step 2: Deploy Infrastructure

#### Option A: Quick Deploy (Recommended)

```bash
cd infrastructure
chmod +x deploy.sh
./deploy.sh
```

#### Option B: Manual Deploy

```bash
cd infrastructure

# Build the SAM application
sam build --template-file template.yaml

# Deploy with guided prompts
sam deploy --guided

# Or deploy with default configuration
sam deploy \
  --template-file .aws-sam/build/template.yaml \
  --stack-name crypto-suspicious-detection \
  --capabilities CAPABILITY_NAMED_IAM \
  --resolve-s3 \
  --region us-east-1
```

### Step 3: Update BitoPro API Credentials

After deployment, update the Secrets Manager secret with your actual BitoPro API credentials:

```bash
# Get the secret ARN from stack outputs
SECRET_ARN=$(aws cloudformation describe-stacks \
  --stack-name crypto-suspicious-detection \
  --query 'Stacks[0].Outputs[?OutputKey==`BitoproSecretArn`].OutputValue' \
  --output text)

# Update the secret with your actual credentials
aws secretsmanager update-secret \
  --secret-id $SECRET_ARN \
  --secret-string '{"api_key":"YOUR_ACTUAL_API_KEY","api_secret":"YOUR_ACTUAL_API_SECRET"}' \
  --region us-east-1
```

### Step 4: Verify Deployment

```bash
cd infrastructure
chmod +x verify-deployment.sh
./verify-deployment.sh
```

This script will check:
- ✓ CloudFormation stack status
- ✓ S3 buckets (private, encrypted)
- ✓ DynamoDB table (encrypted)
- ✓ Secrets Manager secret
- ✓ Lambda functions
- ✓ CloudWatch log groups
- ✓ IAM roles

### Step 5: View Stack Outputs

```bash
aws cloudformation describe-stacks \
  --stack-name crypto-suspicious-detection \
  --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
  --output table
```

## Deployed Resources

After successful deployment, you will have:

### S3 Buckets (All Private with AES-256 Encryption)
- `crypto-suspicious-detection-raw-data-{account-id}`: Raw transaction data
- `crypto-suspicious-detection-features-{account-id}`: Extracted features
- `crypto-suspicious-detection-risk-scores-{account-id}`: Risk assessments
- `crypto-suspicious-detection-reports-{account-id}`: Reports and charts

### DynamoDB Table
- `crypto-suspicious-detection-risk-profiles`: Account risk profiles (KMS encrypted)

### Lambda Functions
- `crypto-suspicious-detection-data-fetcher`: Fetches transactions from BitoPro
- `crypto-suspicious-detection-feature-extractor`: Extracts risk features
- `crypto-suspicious-detection-risk-analyzer`: Analyzes risk with Bedrock
- `crypto-suspicious-detection-report-generator`: Generates reports

### IAM Roles (Least Privilege)
- `crypto-suspicious-detection-data-fetcher-role`
- `crypto-suspicious-detection-feature-extractor-role`
- `crypto-suspicious-detection-risk-analyzer-role`
- `crypto-suspicious-detection-report-generator-role`
- `crypto-suspicious-detection-step-functions-role`

### Secrets Manager
- `crypto-suspicious-detection-bitopro-api-key`: BitoPro API credentials

### CloudWatch Log Groups
- `/aws/lambda/crypto-suspicious-detection-data-fetcher`
- `/aws/lambda/crypto-suspicious-detection-feature-extractor`
- `/aws/lambda/crypto-suspicious-detection-risk-analyzer`
- `/aws/lambda/crypto-suspicious-detection-report-generator`

## Testing the Infrastructure

### Test Lambda Functions

```bash
# Test Data Fetcher
aws lambda invoke \
  --function-name crypto-suspicious-detection-data-fetcher \
  --payload '{"test": true}' \
  --region us-east-1 \
  response.json

cat response.json

# Test Feature Extractor
aws lambda invoke \
  --function-name crypto-suspicious-detection-feature-extractor \
  --payload '{"test": true}' \
  --region us-east-1 \
  response.json

cat response.json
```

### Check CloudWatch Logs

```bash
# View Data Fetcher logs
aws logs tail /aws/lambda/crypto-suspicious-detection-data-fetcher --follow

# View Feature Extractor logs
aws logs tail /aws/lambda/crypto-suspicious-detection-feature-extractor --follow
```

### Verify S3 Bucket Configuration

```bash
# Check bucket encryption
aws s3api get-bucket-encryption \
  --bucket crypto-suspicious-detection-raw-data-$(aws sts get-caller-identity --query Account --output text)

# Check public access block
aws s3api get-public-access-block \
  --bucket crypto-suspicious-detection-raw-data-$(aws sts get-caller-identity --query Account --output text)
```

## Troubleshooting

### Issue: "Stack already exists"

If you need to update the stack:
```bash
sam deploy --no-confirm-changeset
```

### Issue: "Insufficient permissions"

Ensure your AWS user/role has the following permissions:
- `cloudformation:*`
- `s3:*`
- `lambda:*`
- `iam:*`
- `dynamodb:*`
- `secretsmanager:*`
- `logs:*`

### Issue: "Bedrock access denied"

1. Go to AWS Bedrock console
2. Navigate to "Model access"
3. Request access to Claude 3 models
4. Wait for approval (usually instant)

### Issue: Lambda function fails to deploy

Check that the Lambda handler files exist:
```bash
ls -la src/lambdas/*/handler.py
```

If missing, they should have been created during infrastructure setup.

### Issue: SAM build fails

Ensure you're in the correct directory:
```bash
cd infrastructure
sam build --template-file template.yaml
```

## Updating the Infrastructure

To update the infrastructure after making changes to `template.yaml`:

```bash
cd infrastructure
sam build --template-file template.yaml
sam deploy --no-confirm-changeset
```

## Cleanup

To delete all resources and avoid charges:

```bash
# Delete the CloudFormation stack
aws cloudformation delete-stack \
  --stack-name crypto-suspicious-detection \
  --region us-east-1

# Wait for deletion to complete
aws cloudformation wait stack-delete-complete \
  --stack-name crypto-suspicious-detection \
  --region us-east-1

# Note: S3 buckets with versioning may need manual cleanup
# List and delete objects if needed
aws s3 rm s3://crypto-suspicious-detection-raw-data-{account-id} --recursive
aws s3 rm s3://crypto-suspicious-detection-features-{account-id} --recursive
aws s3 rm s3://crypto-suspicious-detection-risk-scores-{account-id} --recursive
aws s3 rm s3://crypto-suspicious-detection-reports-{account-id} --recursive
```

## Cost Estimation

Estimated costs for a 4-hour hackathon with moderate usage:

| Service | Usage | Estimated Cost |
|---------|-------|----------------|
| S3 | ~1 GB storage, 1000 requests | $0.01 |
| DynamoDB | On-demand, ~100 writes/reads | $0.00 |
| Lambda | 1024MB, 300s timeout, ~100 invocations | $0.20 |
| Bedrock | Claude 3 Haiku, ~100 requests | $0.50 |
| Secrets Manager | 1 secret | $0.40 |
| CloudWatch Logs | 7-day retention, ~100 MB | $0.01 |
| **Total** | | **~$1.12** |

## Security Checklist

Before going to production, verify:

- [x] All S3 buckets are private with public access blocked
- [x] All S3 buckets use AES-256 encryption
- [x] DynamoDB table uses KMS encryption at rest
- [x] API credentials stored in Secrets Manager (not hardcoded)
- [x] IAM roles follow least privilege principle
- [x] No public EC2 instances or 0.0.0.0/0 security groups
- [x] CloudWatch logging enabled for all Lambda functions
- [x] No sensitive data logged to CloudWatch
- [x] Bedrock rate limiting implemented (< 1 req/sec)

## Next Steps

After infrastructure deployment:

1. ✅ Infrastructure deployed and verified
2. ⏭️ Implement Lambda function code (Tasks 2-8)
3. ⏭️ Create Step Functions state machine (Task 9)
4. ⏭️ Deploy and test complete workflow (Task 10)
5. ⏭️ Prepare demo and presentation (Task 12)

## Support

For issues or questions:
- Check CloudFormation console for stack events
- Review CloudWatch logs for Lambda execution errors
- Verify IAM permissions and resource configurations
- Consult AWS documentation for specific services

## References

- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [AWS Security Best Practices](https://docs.aws.amazon.com/security/)
