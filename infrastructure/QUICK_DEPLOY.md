# Quick Deploy Reference Card

## Prerequisites
```bash
# Install AWS CLI
brew install awscli  # macOS
# OR download from: https://aws.amazon.com/cli/

# Install SAM CLI
brew install aws-sam-cli  # macOS
# OR download from: https://docs.aws.amazon.com/serverless-application-model/

# Configure AWS
aws configure
```

## Deploy in 3 Steps

### 1. Check Readiness
```bash
cd infrastructure
chmod +x test-deployment-readiness.sh
./test-deployment-readiness.sh
```

### 2. Deploy
```bash
chmod +x deploy.sh
./deploy.sh
```

### 3. Verify
```bash
chmod +x verify-deployment.sh
./verify-deployment.sh
```

## Update API Credentials
```bash
SECRET_ARN=$(aws cloudformation describe-stacks \
  --stack-name crypto-suspicious-detection \
  --query 'Stacks[0].Outputs[?OutputKey==`BitoproSecretArn`].OutputValue' \
  --output text)

aws secretsmanager update-secret \
  --secret-id $SECRET_ARN \
  --secret-string '{"api_key":"YOUR_KEY","api_secret":"YOUR_SECRET"}'
```

## Test Workflow
```bash
STATE_MACHINE_ARN=$(aws cloudformation describe-stacks \
  --stack-name crypto-suspicious-detection \
  --query 'Stacks[0].Outputs[?OutputKey==`StateMachineArn`].OutputValue' \
  --output text)

aws stepfunctions start-execution \
  --state-machine-arn $STATE_MACHINE_ARN \
  --name "test-$(date +%s)" \
  --input '{"test": true, "limit": 50}'
```

## View Logs
```bash
aws logs tail /aws/lambda/crypto-suspicious-detection-data-fetcher --follow
```

## Cleanup
```bash
aws cloudformation delete-stack --stack-name crypto-suspicious-detection
```

## Troubleshooting

**Build fails?**
```bash
cd infrastructure
sam build --template-file template.yaml --debug
```

**Deploy fails?**
```bash
sam deploy --no-confirm-changeset --debug
```

**Bedrock access denied?**
- Go to AWS Console → Bedrock → Model access
- Request access to Claude 3 models

**Lambda fails?**
```bash
aws logs tail /aws/lambda/crypto-suspicious-detection-FUNCTION-NAME --follow
```

## Cost
~$1-2 for 4-hour hackathon with moderate usage

## Documentation
- Full guide: `DEPLOYMENT_GUIDE.md`
- Summary: `TASK_10.4_DEPLOYMENT_SUMMARY.md`
- Existing docs: `README.md`, `DEPLOYMENT.md`
