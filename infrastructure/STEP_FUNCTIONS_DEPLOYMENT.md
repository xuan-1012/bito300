# Step Functions State Machine Deployment

## Overview

The Step Functions state machine orchestrates the complete workflow for the Crypto Suspicious Account Detection system. It coordinates four Lambda functions in sequence with error handling and retry logic.

## State Machine Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Step Functions Workflow                     │
│                                                              │
│  ┌──────────────┐                                           │
│  │ DataFetcher  │ ──────────────────────────────────────┐  │
│  └──────────────┘                                        │  │
│         │                                                 │  │
│         │ Success                                         │  │
│         ▼                                                 │  │
│  ┌──────────────────┐                                    │  │
│  │FeatureExtractor  │ ───────────────────────────────┐  │  │
│  └──────────────────┘                                 │  │  │
│         │                                              │  │  │
│         │ Success                                      │  │  │
│         ▼                                              │  │  │
│  ┌──────────────┐                                     │  │  │
│  │RiskAnalyzer  │ ──────────────────────────────┐    │  │  │
│  └──────────────┘                                │    │  │  │
│         │                                         │    │  │  │
│         │ Success                                 │    │  │  │
│         ▼                                         │    │  │  │
│  ┌──────────────────┐                            │    │  │  │
│  │ReportGenerator   │                            │    │  │  │
│  └──────────────────┘                            │    │  │  │
│         │                                         │    │  │  │
│         │ Success                                 │    │  │  │
│         ▼                                         │    │  │  │
│  ┌──────────────┐                                │    │  │  │
│  │SuccessState  │                                │    │  │  │
│  └──────────────┘                                │    │  │  │
│                                                   │    │  │  │
│         Error ────────────────────────────────────┘    │  │  │
│         Error ─────────────────────────────────────────┘  │  │
│         Error ────────────────────────────────────────────┘  │
│                                                              │
│         │                                                    │
│         ▼                                                    │
│  ┌──────────────┐                                           │
│  │  FailState   │                                           │
│  └──────────────┘                                           │
└─────────────────────────────────────────────────────────────┘
```

## State Machine Configuration

### States

1. **DataFetcher**
   - Timeout: 300 seconds (5 minutes)
   - Retry: 3 attempts with exponential backoff (2x)
   - Fetches transaction data from BitoPro API
   - Stores raw data to S3

2. **FeatureExtractor**
   - Timeout: 300 seconds (5 minutes)
   - Retry: 3 attempts with exponential backoff (2x)
   - Extracts risk features from raw transactions
   - Stores features to S3

3. **RiskAnalyzer**
   - Timeout: 3600 seconds (1 hour)
   - Retry: 2 attempts with exponential backoff (2x)
   - Analyzes risk using AWS Bedrock
   - Implements rate limiting (< 1 req/sec)
   - Stores risk assessments to S3 and DynamoDB

4. **ReportGenerator**
   - Timeout: 300 seconds (5 minutes)
   - Retry: 3 attempts with exponential backoff (2x)
   - Generates summary statistics
   - Creates visualizations (charts)
   - Generates HTML presentation
   - Stores reports to S3

### Error Handling

Each state includes:
- **Retry Policy**: Automatic retries with exponential backoff
- **Catch Block**: Captures all errors and transitions to FailState
- **Error Context**: Preserves error information in `$.error` path

### Retry Configuration

```json
{
  "ErrorEquals": [
    "States.TaskFailed",
    "States.Timeout",
    "Lambda.ServiceException",
    "Lambda.TooManyRequestsException"
  ],
  "IntervalSeconds": 2,
  "MaxAttempts": 3,
  "BackoffRate": 2.0
}
```

## Deployment

### Prerequisites

1. AWS SAM CLI installed
2. AWS CLI configured with appropriate credentials
3. Lambda functions deployed
4. IAM roles created

### Deploy via SAM Template

The state machine is automatically deployed as part of the SAM template:

```bash
cd infrastructure
./deploy.sh
```

This will:
1. Build the SAM application
2. Deploy all Lambda functions
3. Create the Step Functions state machine
4. Configure IAM roles and permissions
5. Set up CloudWatch logging

### Manual Deployment (Alternative)

If you need to deploy the state machine separately:

```bash
# Get Lambda function ARNs
DATA_FETCHER_ARN=$(aws cloudformation describe-stacks \
  --stack-name crypto-suspicious-detection \
  --query 'Stacks[0].Outputs[?OutputKey==`DataFetcherFunctionArn`].OutputValue' \
  --output text)

FEATURE_EXTRACTOR_ARN=$(aws cloudformation describe-stacks \
  --stack-name crypto-suspicious-detection \
  --query 'Stacks[0].Outputs[?OutputKey==`FeatureExtractorFunctionArn`].OutputValue' \
  --output text)

RISK_ANALYZER_ARN=$(aws cloudformation describe-stacks \
  --stack-name crypto-suspicious-detection \
  --query 'Stacks[0].Outputs[?OutputKey==`RiskAnalyzerFunctionArn`].OutputValue' \
  --output text)

REPORT_GENERATOR_ARN=$(aws cloudformation describe-stacks \
  --stack-name crypto-suspicious-detection \
  --query 'Stacks[0].Outputs[?OutputKey==`ReportGeneratorFunctionArn`].OutputValue' \
  --output text)

# Substitute ARNs in state machine definition
sed -e "s|\${DataFetcherFunctionArn}|$DATA_FETCHER_ARN|g" \
    -e "s|\${FeatureExtractorFunctionArn}|$FEATURE_EXTRACTOR_ARN|g" \
    -e "s|\${RiskAnalyzerFunctionArn}|$RISK_ANALYZER_ARN|g" \
    -e "s|\${ReportGeneratorFunctionArn}|$REPORT_GENERATOR_ARN|g" \
    state_machine.json > state_machine_resolved.json

# Create or update state machine
aws stepfunctions create-state-machine \
  --name crypto-suspicious-detection-workflow \
  --definition file://state_machine_resolved.json \
  --role-arn $(aws cloudformation describe-stacks \
    --stack-name crypto-suspicious-detection \
    --query 'Stacks[0].Outputs[?OutputKey==`StepFunctionsRoleArn`].OutputValue' \
    --output text)
```

## Verification

### Check State Machine Status

```bash
# Get state machine ARN
STATE_MACHINE_ARN=$(aws cloudformation describe-stacks \
  --stack-name crypto-suspicious-detection \
  --query 'Stacks[0].Outputs[?OutputKey==`StateMachineArn`].OutputValue' \
  --output text)

# Describe state machine
aws stepfunctions describe-state-machine \
  --state-machine-arn $STATE_MACHINE_ARN
```

### Start Execution

```bash
# Start execution with input
aws stepfunctions start-execution \
  --state-machine-arn $STATE_MACHINE_ARN \
  --name test-execution-$(date +%s) \
  --input '{
    "time_range": {
      "start": "2024-01-01T00:00:00Z",
      "end": "2024-01-31T23:59:59Z"
    },
    "account_ids": ["account1", "account2"]
  }'
```

### Monitor Execution

```bash
# List executions
aws stepfunctions list-executions \
  --state-machine-arn $STATE_MACHINE_ARN \
  --max-results 10

# Get execution details
EXECUTION_ARN=$(aws stepfunctions list-executions \
  --state-machine-arn $STATE_MACHINE_ARN \
  --max-results 1 \
  --query 'executions[0].executionArn' \
  --output text)

aws stepfunctions describe-execution \
  --execution-arn $EXECUTION_ARN

# Get execution history
aws stepfunctions get-execution-history \
  --execution-arn $EXECUTION_ARN \
  --max-results 100
```

### View Logs

```bash
# View state machine logs
aws logs tail /aws/states/crypto-suspicious-detection-workflow --follow
```

## IAM Permissions

The Step Functions execution role has the following permissions:

```yaml
Policies:
  - PolicyName: StepFunctionsPolicy
    PolicyDocument:
      Statement:
        - Effect: Allow
          Action:
            - lambda:InvokeFunction
          Resource:
            - arn:aws:lambda:*:*:function:crypto-suspicious-detection-*
        - Effect: Allow
          Action:
            - logs:CreateLogDelivery
            - logs:GetLogDelivery
            - logs:UpdateLogDelivery
            - logs:DeleteLogDelivery
            - logs:ListLogDeliveries
            - logs:PutResourcePolicy
            - logs:DescribeResourcePolicies
            - logs:DescribeLogGroups
          Resource: '*'
```

## Monitoring and Logging

### CloudWatch Logs

All state machine executions are logged to:
```
/aws/states/crypto-suspicious-detection-workflow
```

Log level: `ALL` (includes execution data)

### CloudWatch Metrics

Monitor the following metrics:
- `ExecutionsFailed`: Number of failed executions
- `ExecutionsSucceeded`: Number of successful executions
- `ExecutionTime`: Duration of executions
- `ExecutionThrottled`: Number of throttled executions

### Alarms (Optional)

Create CloudWatch alarms for:
```bash
# Alarm for failed executions
aws cloudwatch put-metric-alarm \
  --alarm-name crypto-detection-execution-failures \
  --alarm-description "Alert when state machine executions fail" \
  --metric-name ExecutionsFailed \
  --namespace AWS/States \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 1 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=StateMachineArn,Value=$STATE_MACHINE_ARN
```

## Troubleshooting

### Issue: State machine creation fails

**Cause**: Lambda functions not deployed or IAM role missing

**Solution**:
1. Verify Lambda functions exist:
   ```bash
   aws lambda list-functions --query 'Functions[?starts_with(FunctionName, `crypto-suspicious-detection`)].FunctionName'
   ```

2. Verify IAM role exists:
   ```bash
   aws iam get-role --role-name crypto-suspicious-detection-step-functions-role
   ```

### Issue: Execution fails at DataFetcher

**Cause**: BitoPro API credentials not configured

**Solution**:
```bash
aws secretsmanager update-secret \
  --secret-id crypto-suspicious-detection-bitopro-api-key \
  --secret-string '{"api_key":"YOUR_KEY","api_secret":"YOUR_SECRET"}'
```

### Issue: Execution fails at RiskAnalyzer

**Cause**: Bedrock model access not enabled

**Solution**:
1. Go to AWS Bedrock console
2. Navigate to "Model access"
3. Request access to Claude 3 models

### Issue: Execution times out

**Cause**: Processing large dataset or rate limiting

**Solution**:
1. Increase timeout in state machine definition
2. Process data in smaller batches
3. Optimize Lambda function code

## Cost Optimization

### Execution Costs

- **State Transitions**: $0.025 per 1,000 transitions
- **Typical Execution**: 5 transitions = $0.000125 per execution

### Recommendations

1. Use Express Workflows for high-volume scenarios (cheaper but no execution history)
2. Batch process multiple accounts in single execution
3. Set appropriate timeouts to avoid unnecessary charges
4. Use CloudWatch Logs Insights for debugging instead of detailed logging

## Next Steps

1. ✅ State machine deployed
2. Test with sample data
3. Monitor execution metrics
4. Optimize performance
5. Set up alarms and notifications

## References

- [AWS Step Functions Documentation](https://docs.aws.amazon.com/step-functions/)
- [State Machine Definition Language](https://states-language.net/spec.html)
- [Error Handling in Step Functions](https://docs.aws.amazon.com/step-functions/latest/dg/concepts-error-handling.html)
- [Step Functions Best Practices](https://docs.aws.amazon.com/step-functions/latest/dg/sfn-best-practices.html)
