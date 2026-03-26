# Infrastructure Setup

This directory contains the AWS infrastructure configuration for the Crypto Suspicious Account Detection system.

## Overview

The infrastructure is defined using AWS SAM (Serverless Application Model) and includes:

### AWS Resources

1. **S3 Buckets** (All private with AES-256 encryption):
   - `raw-data`: Stores raw transaction data from BitoPro API
   - `features`: Stores extracted risk features
   - `risk-scores`: Stores risk assessment results
   - `reports`: Stores generated reports and visualizations

2. **DynamoDB Table**:
   - `risk-profiles`: Stores account risk profiles with encryption at rest (KMS)
   - Partition key: `account_id`
   - Sort key: `timestamp`
   - Global Secondary Index: `RiskLevelIndex`

3. **AWS Secrets Manager**:
   - `bitopro-api-key`: Stores BitoPro API credentials securely

4. **CloudWatch Log Groups**:
   - `/aws/lambda/data-fetcher`: Logs for Data Fetcher Lambda
   - `/aws/lambda/feature-extractor`: Logs for Feature Extractor Lambda
   - `/aws/lambda/risk-analyzer`: Logs for Risk Analyzer Lambda
   - `/aws/lambda/report-generator`: Logs for Report Generator Lambda

5. **IAM Roles** (Least Privilege):
   - `DataFetcherRole`: Access to Secrets Manager and raw data S3 bucket
   - `FeatureExtractorRole`: Read from raw data, write to features bucket
   - `RiskAnalyzerRole`: Read features, write risk scores, access Bedrock and DynamoDB
   - `ReportGeneratorRole`: Read risk scores and DynamoDB, write to reports bucket
   - `StepFunctionsRole`: Invoke Lambda functions and manage logs

6. **Lambda Functions** (Placeholders):
   - `data-fetcher`: Fetches transactions from BitoPro API
   - `feature-extractor`: Extracts risk features from transactions
   - `risk-analyzer`: Analyzes risk using AWS Bedrock
   - `report-generator`: Generates reports and visualizations

## Security Compliance

✅ All S3 buckets are private with public access blocked
✅ All S3 buckets use AES-256 encryption
✅ DynamoDB table uses KMS encryption at rest
✅ API credentials stored in Secrets Manager (never hardcoded)
✅ IAM roles follow least privilege principle
✅ No public EC2 instances or security groups with 0.0.0.0/0
✅ CloudWatch logging enabled for all Lambda functions

## Prerequisites

1. **AWS CLI** installed and configured:
   ```bash
   aws --version
   aws configure
   ```

2. **AWS SAM CLI** installed:
   ```bash
   sam --version
   ```
   Install from: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html

3. **AWS Account** with appropriate permissions to create:
   - S3 buckets
   - DynamoDB tables
   - Lambda functions
   - IAM roles and policies
   - Secrets Manager secrets
   - CloudWatch log groups

## Deployment

### Quick Deploy

```bash
cd infrastructure
chmod +x deploy.sh
./deploy.sh
```

### Manual Deploy

```bash
cd infrastructure

# Build the SAM application
sam build --template-file template.yaml

# Deploy the application
sam deploy \
  --template-file .aws-sam/build/template.yaml \
  --stack-name crypto-suspicious-detection \
  --capabilities CAPABILITY_NAMED_IAM \
  --resolve-s3
```

### Update BitoPro API Credentials

After deployment, update the Secrets Manager secret with your actual BitoPro API credentials:

```bash
aws secretsmanager update-secret \
  --secret-id crypto-suspicious-detection-bitopro-api-key \
  --secret-string '{"api_key":"YOUR_ACTUAL_API_KEY","api_secret":"YOUR_ACTUAL_API_SECRET"}' \
  --region us-east-1
```

## Verification

After deployment, verify the resources:

```bash
# Check stack status
aws cloudformation describe-stacks \
  --stack-name crypto-suspicious-detection \
  --query 'Stacks[0].StackStatus'

# List S3 buckets
aws s3 ls | grep crypto-suspicious-detection

# Check DynamoDB table
aws dynamodb describe-table \
  --table-name crypto-suspicious-detection-risk-profiles

# Verify Secrets Manager secret
aws secretsmanager describe-secret \
  --secret-id crypto-suspicious-detection-bitopro-api-key

# List Lambda functions
aws lambda list-functions \
  --query 'Functions[?starts_with(FunctionName, `crypto-suspicious-detection`)].FunctionName'
```

## Cleanup

To delete all resources:

```bash
# Delete the CloudFormation stack
aws cloudformation delete-stack \
  --stack-name crypto-suspicious-detection

# Wait for deletion to complete
aws cloudformation wait stack-delete-complete \
  --stack-name crypto-suspicious-detection

# Note: S3 buckets with versioning enabled may need manual cleanup
```

## Cost Estimation

For a 4-hour hackathon with moderate usage:

- **S3**: ~$0.01 (minimal storage)
- **DynamoDB**: ~$0.00 (on-demand pricing, low volume)
- **Lambda**: ~$0.20 (1024MB, 300s timeout, ~100 invocations)
- **Bedrock**: ~$0.50 (Claude 3 Haiku, ~100 requests)
- **Secrets Manager**: ~$0.40 (1 secret)
- **CloudWatch Logs**: ~$0.01 (7-day retention)

**Total estimated cost**: ~$1.12 for the hackathon

## Troubleshooting

### Issue: SAM build fails

**Solution**: Ensure Lambda function directories exist:
```bash
mkdir -p ../src/lambdas/data_fetcher
mkdir -p ../src/lambdas/feature_extractor
mkdir -p ../src/lambdas/risk_analyzer
mkdir -p ../src/lambdas/report_generator
```

### Issue: Deployment fails with "Insufficient permissions"

**Solution**: Ensure your AWS user/role has the following permissions:
- `cloudformation:*`
- `s3:*`
- `lambda:*`
- `iam:*`
- `dynamodb:*`
- `secretsmanager:*`
- `logs:*`

### Issue: Bedrock access denied

**Solution**: Enable Bedrock model access in AWS Console:
1. Go to AWS Bedrock console
2. Navigate to "Model access"
3. Request access to Claude 3 models

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     AWS Cloud                                │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │ Secrets Mgr  │    │  CloudWatch  │    │ Step Functions│ │
│  │ (API Keys)   │    │   (Logs)     │    │ (Orchestrate) │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Lambda Functions                         │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────┐│  │
│  │  │  Data    │→ │ Feature  │→ │   Risk   │→ │Report││  │
│  │  │ Fetcher  │  │Extractor │  │ Analyzer │  │ Gen  ││  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────┘│  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Storage Layer                            │  │
│  │  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌────────┐│  │
│  │  │ Raw  │  │Feats │  │ Risk │  │Report│  │DynamoDB││  │
│  │  │ S3   │  │ S3   │  │ S3   │  │ S3   │  │ Table  ││  │
│  │  └──────┘  └──────┘  └──────┘  └──────┘  └────────┘│  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────┐                                           │
│  │   Bedrock    │                                           │
│  │ (Claude 3)   │                                           │
│  └──────────────┘                                           │
└─────────────────────────────────────────────────────────────┘
```

## Next Steps

After infrastructure deployment:

1. Implement Lambda function code in `../src/lambdas/`
2. Create Step Functions state machine definition
3. Deploy Lambda function code
4. Test the complete workflow
5. Generate demo reports for presentation

## Support

For issues or questions:
- Check AWS CloudFormation console for stack events
- Review CloudWatch logs for Lambda execution errors
- Verify IAM permissions and resource configurations
