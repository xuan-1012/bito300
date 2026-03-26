# AWS Deployment Guide - Task 10.4

This guide provides step-by-step instructions for deploying the Crypto Suspicious Account Detection system to AWS.

## Prerequisites Checklist

Before deploying, ensure you have:

- [ ] AWS CLI installed and configured (`aws --version`)
- [ ] AWS SAM CLI installed (`sam --version`)
- [ ] AWS credentials configured (`aws sts get-caller-identity`)
- [ ] Python 3.11 installed
- [ ] BitoPro API credentials (if testing with real API)
- [ ] AWS Bedrock model access enabled (Claude 3 models)

## Step 1: Pre-Deployment Verification

### 1.1 Verify AWS Credentials

```bash
# Check your AWS identity
aws sts get-caller-identity

# Expected output:
# {
#     "UserId": "...",
#     "Account": "123456789012",
#     "Arn": "arn:aws:iam::123456789012:user/your-user"
# }
```

### 1.2 Check AWS Region

```bash
# Get current region
aws configure get region

# If not set, configure it:
aws configure set region us-east-1
```

### 1.3 Enable Bedrock Model Access

1. Go to AWS Console → Amazon Bedrock
2. Navigate to "Model access" in left sidebar
3. Click "Manage model access"
4. Enable these models:
   - ✅ Anthropic Claude 3 Sonnet
   - ✅ Anthropic Claude 3 Haiku
5. Click "Request model access"
6. Wait for approval (usually instant)

### 1.4 Verify Lambda Handler Files

```bash
# Check that all Lambda handlers exist
ls -la src/lambdas/*/handler.py

# Expected output:
# src/lambdas/data_fetcher/handler.py
# src/lambdas/feature_extractor/handler.py
# src/lambdas/risk_analyzer/handler.py
# src/lambdas/report_generator/handler.py
```

## Step 2: Build the SAM Application

```bash
cd infrastructure

# Build the SAM application
sam build --template-file template.yaml

# Expected output:
# Build Succeeded
# Built Artifacts  : .aws-sam/build
# Built Template   : .aws-sam/build/template.yaml
```

### Troubleshooting Build Issues

If build fails with "CodeUri not found":
```bash
# Ensure Lambda directories exist
mkdir -p ../src/lambdas/data_fetcher
mkdir -p ../src/lambdas/feature_extractor
mkdir -p ../src/lambdas/risk_analyzer
mkdir -p ../src/lambdas/report_generator

# Retry build
sam build --template-file template.yaml
```

## Step 3: Deploy to AWS

### Option A: Quick Deploy (Recommended)

```bash
cd infrastructure
chmod +x deploy.sh
./deploy.sh
```

### Option B: Manual Deploy with Guided Setup

```bash
cd infrastructure

# Deploy with guided prompts (first time)
sam deploy --guided

# You will be prompted for:
# - Stack Name: crypto-suspicious-detection
# - AWS Region: us-east-1 (or your preferred region)
# - Confirm changes before deploy: Y
# - Allow SAM CLI IAM role creation: Y
# - Disable rollback: N
# - Save arguments to configuration file: Y
```

### Option C: Manual Deploy with Parameters

```bash
cd infrastructure

sam deploy \
  --template-file .aws-sam/build/template.yaml \
  --stack-name crypto-suspicious-detection \
  --capabilities CAPABILITY_NAMED_IAM \
  --resolve-s3 \
  --region us-east-1 \
  --no-fail-on-empty-changeset
```

### Expected Deployment Output

```
Deploying with following values
===============================
Stack name                   : crypto-suspicious-detection
Region                       : us-east-1
Confirm changeset            : False
Disable rollback             : False
Deployment s3 bucket         : aws-sam-cli-managed-default-samclisourcebucket-...
Capabilities                 : ["CAPABILITY_NAMED_IAM"]
Parameter overrides          : {}
Signing Profiles             : {}

Initiating deployment
=====================

CloudFormation stack changeset
-------------------------------------------------------------------------------------------------
Operation                        LogicalResourceId                ResourceType
-------------------------------------------------------------------------------------------------
+ Add                            BitoproApiSecret                 AWS::SecretsManager::Secret
+ Add                            DataFetcherFunction              AWS::Lambda::Function
+ Add                            DataFetcherLogGroup              AWS::Logs::LogGroup
+ Add                            DataFetcherRole                  AWS::IAM::Role
+ Add                            FeatureExtractorFunction         AWS::Lambda::Function
+ Add                            FeatureExtractorLogGroup         AWS::Logs::LogGroup
+ Add                            FeatureExtractorRole             AWS::IAM::Role
+ Add                            FeaturesBucket                   AWS::S3::Bucket
+ Add                            RawDataBucket                    AWS::S3::Bucket
+ Add                            ReportGeneratorFunction          AWS::Lambda::Function
+ Add                            ReportGeneratorLogGroup          AWS::Logs::LogGroup
+ Add                            ReportGeneratorRole              AWS::IAM::Role
+ Add                            ReportsBucket                    AWS::S3::Bucket
+ Add                            RiskAnalyzerFunction             AWS::Lambda::Function
+ Add                            RiskAnalyzerLogGroup             AWS::Logs::LogGroup
+ Add                            RiskAnalyzerRole                 AWS::IAM::Role
+ Add                            RiskProfilesTable                AWS::DynamoDB::Table
+ Add                            RiskScoresBucket                 AWS::S3::Bucket
+ Add                            StateMachineLogGroup             AWS::Logs::LogGroup
+ Add                            StepFunctionsRole                AWS::IAM::Role
+ Add                            CryptoDetectionStateMachine      AWS::StepFunctions::StateMachine
-------------------------------------------------------------------------------------------------

Successfully created/updated stack - crypto-suspicious-detection in us-east-1
```

## Step 4: Verify Deployment

### 4.1 Check Stack Status

```bash
aws cloudformation describe-stacks \
  --stack-name crypto-suspicious-detection \
  --query 'Stacks[0].StackStatus' \
  --output text

# Expected: CREATE_COMPLETE or UPDATE_COMPLETE
```

### 4.2 View Stack Outputs

```bash
aws cloudformation describe-stacks \
  --stack-name crypto-suspicious-detection \
  --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
  --output table
```

### 4.3 Run Verification Script

```bash
cd infrastructure
chmod +x verify-deployment.sh
./verify-deployment.sh
```

Expected output:
```
==========================================
Infrastructure Verification
==========================================

Stack: crypto-suspicious-detection
Region: us-east-1

=== CloudFormation Stack ===
✓ Stack Status: CREATE_COMPLETE

=== S3 Buckets ===
✓ S3 Bucket: crypto-suspicious-detection-raw-data-123456789012
✓ S3 Bucket: crypto-suspicious-detection-features-123456789012
✓ S3 Bucket: crypto-suspicious-detection-risk-scores-123456789012
✓ S3 Bucket: crypto-suspicious-detection-reports-123456789012

=== S3 Bucket Encryption ===
✓ All buckets: AES256 encryption enabled

=== S3 Public Access Block ===
✓ All buckets: Public access blocked

=== DynamoDB Table ===
✓ DynamoDB Table: crypto-suspicious-detection-risk-profiles
✓ DynamoDB encryption: KMS enabled

=== Secrets Manager ===
✓ Secret: bitopro-api-key
⚠ WARNING: Secret still contains PLACEHOLDER values. Update with actual credentials!

=== Lambda Functions ===
✓ Lambda: data-fetcher
✓ Lambda: feature-extractor
✓ Lambda: risk-analyzer
✓ Lambda: report-generator

=== CloudWatch Log Groups ===
✓ Log Group: data-fetcher
✓ Log Group: feature-extractor
✓ Log Group: risk-analyzer
✓ Log Group: report-generator

=== IAM Roles ===
✓ IAM Role: data-fetcher-role
✓ IAM Role: feature-extractor-role
✓ IAM Role: risk-analyzer-role
✓ IAM Role: report-generator-role
✓ IAM Role: step-functions-role

==========================================
✓ Verification Complete
==========================================
```

## Step 5: Update BitoPro API Credentials

### 5.1 Get Secret ARN

```bash
SECRET_ARN=$(aws cloudformation describe-stacks \
  --stack-name crypto-suspicious-detection \
  --query 'Stacks[0].Outputs[?OutputKey==`BitoproSecretArn`].OutputValue' \
  --output text)

echo "Secret ARN: $SECRET_ARN"
```

### 5.2 Update Secret with Real Credentials

```bash
# Replace YOUR_API_KEY and YOUR_API_SECRET with actual values
aws secretsmanager update-secret \
  --secret-id $SECRET_ARN \
  --secret-string '{"api_key":"YOUR_API_KEY","api_secret":"YOUR_API_SECRET"}' \
  --region us-east-1
```

### 5.3 Verify Secret Update

```bash
aws secretsmanager get-secret-value \
  --secret-id $SECRET_ARN \
  --query 'SecretString' \
  --output text

# Should NOT contain "PLACEHOLDER"
```

## Step 6: Test Lambda Functions

### 6.1 Test Data Fetcher (with mock data)

```bash
aws lambda invoke \
  --function-name crypto-suspicious-detection-data-fetcher \
  --payload '{"test": true, "limit": 10}' \
  --region us-east-1 \
  response.json

cat response.json | jq .
```

### 6.2 Check CloudWatch Logs

```bash
# View Data Fetcher logs
aws logs tail /aws/lambda/crypto-suspicious-detection-data-fetcher \
  --follow \
  --region us-east-1
```

### 6.3 Test Feature Extractor

```bash
# First, get the S3 URI from Data Fetcher response
S3_URI=$(cat response.json | jq -r '.body' | jq -r '.s3_uri')

aws lambda invoke \
  --function-name crypto-suspicious-detection-feature-extractor \
  --payload "{\"s3_uri\": \"$S3_URI\"}" \
  --region us-east-1 \
  response_features.json

cat response_features.json | jq .
```

## Step 7: Test Step Functions Workflow

### 7.1 Get State Machine ARN

```bash
STATE_MACHINE_ARN=$(aws cloudformation describe-stacks \
  --stack-name crypto-suspicious-detection \
  --query 'Stacks[0].Outputs[?OutputKey==`StateMachineArn`].OutputValue' \
  --output text)

echo "State Machine ARN: $STATE_MACHINE_ARN"
```

### 7.2 Start Execution with Mock Data

```bash
# Start execution
EXECUTION_ARN=$(aws stepfunctions start-execution \
  --state-machine-arn $STATE_MACHINE_ARN \
  --name "test-execution-$(date +%s)" \
  --input '{"test": true, "limit": 50}' \
  --query 'executionArn' \
  --output text)

echo "Execution ARN: $EXECUTION_ARN"
```

### 7.3 Monitor Execution

```bash
# Check execution status
aws stepfunctions describe-execution \
  --execution-arn $EXECUTION_ARN \
  --query 'status' \
  --output text

# Get execution history
aws stepfunctions get-execution-history \
  --execution-arn $EXECUTION_ARN \
  --query 'events[*].[timestamp,type,id]' \
  --output table
```

### 7.4 View Execution in Console

```bash
# Open in browser (macOS)
open "https://console.aws.amazon.com/states/home?region=us-east-1#/executions/details/$EXECUTION_ARN"

# Or manually navigate to:
# AWS Console → Step Functions → State machines → crypto-suspicious-detection-workflow → Executions
```

## Step 8: Test with Real BitoPro API (Optional)

⚠️ **Only if you have valid BitoPro API credentials**

### 8.1 Update Secret (if not done in Step 5)

```bash
aws secretsmanager update-secret \
  --secret-id $SECRET_ARN \
  --secret-string '{"api_key":"YOUR_REAL_API_KEY","api_secret":"YOUR_REAL_API_SECRET"}' \
  --region us-east-1
```

### 8.2 Start Real Execution

```bash
# Fetch last 7 days of data
START_TIME=$(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%S)
END_TIME=$(date -u +%Y-%m-%dT%H:%M:%S)

aws stepfunctions start-execution \
  --state-machine-arn $STATE_MACHINE_ARN \
  --name "real-execution-$(date +%s)" \
  --input "{\"start_time\": \"$START_TIME\", \"end_time\": \"$END_TIME\", \"limit\": 1000}"
```

### 8.3 Monitor and Retrieve Report

```bash
# Wait for completion (check status every 30 seconds)
watch -n 30 "aws stepfunctions describe-execution \
  --execution-arn $EXECUTION_ARN \
  --query 'status' \
  --output text"

# Once SUCCEEDED, get the report URL from the output
aws stepfunctions describe-execution \
  --execution-arn $EXECUTION_ARN \
  --query 'output' \
  --output text | jq -r '.reportGeneratorResult.body' | jq -r '.presigned_url'
```

## Step 9: Verify All Resources Created

### 9.1 S3 Buckets

```bash
aws s3 ls | grep crypto-suspicious-detection

# Expected:
# crypto-suspicious-detection-raw-data-123456789012
# crypto-suspicious-detection-features-123456789012
# crypto-suspicious-detection-risk-scores-123456789012
# crypto-suspicious-detection-reports-123456789012
```

### 9.2 DynamoDB Table

```bash
aws dynamodb describe-table \
  --table-name crypto-suspicious-detection-risk-profiles \
  --query 'Table.[TableName,TableStatus,ItemCount]' \
  --output table
```

### 9.3 Lambda Functions

```bash
aws lambda list-functions \
  --query 'Functions[?starts_with(FunctionName, `crypto-suspicious-detection`)].FunctionName' \
  --output table
```

### 9.4 Step Functions State Machine

```bash
aws stepfunctions list-state-machines \
  --query 'stateMachines[?contains(name, `crypto`)].name' \
  --output table
```

## Troubleshooting

### Issue: "Stack already exists"

```bash
# Update existing stack
sam deploy --no-confirm-changeset
```

### Issue: "Insufficient permissions"

Ensure your AWS user/role has these permissions:
- `cloudformation:*`
- `s3:*`
- `lambda:*`
- `iam:*`
- `dynamodb:*`
- `secretsmanager:*`
- `logs:*`
- `states:*`

### Issue: "Bedrock access denied"

1. Go to AWS Bedrock console
2. Request model access for Claude 3 models
3. Wait for approval (usually instant)

### Issue: Lambda function fails

```bash
# Check logs
aws logs tail /aws/lambda/crypto-suspicious-detection-FUNCTION-NAME --follow

# Check function configuration
aws lambda get-function-configuration \
  --function-name crypto-suspicious-detection-FUNCTION-NAME
```

### Issue: Step Functions execution fails

```bash
# Get detailed error
aws stepfunctions describe-execution \
  --execution-arn $EXECUTION_ARN \
  --query '[status,error,cause]' \
  --output table

# Check execution history
aws stepfunctions get-execution-history \
  --execution-arn $EXECUTION_ARN \
  --max-results 100
```

## Deployment Checklist

- [ ] AWS CLI and SAM CLI installed
- [ ] AWS credentials configured
- [ ] Bedrock model access enabled
- [ ] SAM build successful
- [ ] SAM deploy successful
- [ ] Stack status: CREATE_COMPLETE
- [ ] All S3 buckets created (private, encrypted)
- [ ] DynamoDB table created (encrypted)
- [ ] All Lambda functions deployed
- [ ] Step Functions state machine created
- [ ] BitoPro API credentials updated in Secrets Manager
- [ ] Lambda functions tested individually
- [ ] Step Functions workflow tested end-to-end
- [ ] CloudWatch logs verified
- [ ] Report generated successfully

## Cost Estimation

For a 4-hour hackathon with moderate usage:

| Service | Usage | Estimated Cost |
|---------|-------|----------------|
| S3 | ~1 GB storage, 1000 requests | $0.01 |
| DynamoDB | On-demand, ~100 writes/reads | $0.05 |
| Lambda | 1024MB, 300s timeout, ~100 invocations | $0.20 |
| Bedrock | Claude 3 Haiku, ~100 requests | $0.50 |
| Secrets Manager | 1 secret | $0.40 |
| CloudWatch Logs | 7-day retention, ~100 MB | $0.01 |
| Step Functions | ~10 executions | $0.01 |
| **Total** | | **~$1.18** |

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
# Empty buckets if needed:
aws s3 rm s3://crypto-suspicious-detection-raw-data-$(aws sts get-caller-identity --query Account --output text) --recursive
aws s3 rm s3://crypto-suspicious-detection-features-$(aws sts get-caller-identity --query Account --output text) --recursive
aws s3 rm s3://crypto-suspicious-detection-risk-scores-$(aws sts get-caller-identity --query Account --output text) --recursive
aws s3 rm s3://crypto-suspicious-detection-reports-$(aws sts get-caller-identity --query Account --output text) --recursive
```

## Next Steps

After successful deployment:

1. ✅ Infrastructure deployed and verified
2. ✅ Lambda functions tested
3. ✅ Step Functions workflow tested
4. ⏭️ Prepare demo data and presentation (Task 12)
5. ⏭️ Run end-to-end test with real data
6. ⏭️ Generate demo reports for hackathon presentation

## Support Resources

- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [AWS Step Functions Documentation](https://docs.aws.amazon.com/step-functions/)
- [BitoPro API Documentation](https://github.com/bitoex/bitopro-offical-api-docs)

---

**Deployment Status**: Ready for execution
**Last Updated**: 2024-01-15
**Task**: 10.4 - Deploy to AWS
