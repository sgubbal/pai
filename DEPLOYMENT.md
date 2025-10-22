# PAI Agent Deployment Guide

Complete guide for deploying the Personal AI Agent to AWS.

## Prerequisites

### Required Tools

1. **AWS CLI** (v2.x or later)
   ```bash
   aws --version
   ```

2. **Python 3.11+**
   ```bash
   python --version
   ```

3. **Git**
   ```bash
   git --version
   ```

4. **jq** (for JSON parsing in scripts)
   ```bash
   jq --version
   ```

### AWS Account Setup

1. **AWS Account**: You need an AWS account with appropriate permissions

2. **AWS Credentials**: Configure your AWS credentials
   ```bash
   aws configure
   ```

3. **Bedrock Model Access**: Request access to the following models in AWS Bedrock:
   - Claude 3 Sonnet (`anthropic.claude-3-sonnet-20240229-v1:0`)
   - Titan Embeddings V2 (`amazon.titan-embed-text-v2:0`)

   To request access:
   - Go to AWS Console → Amazon Bedrock → Model access
   - Request access for the required models
   - Wait for approval (usually instant for most models)

## Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd pai
```

### 2. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements-dev.txt
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env
```

Required environment variables:
```bash
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=your-account-id
ENVIRONMENT=dev
```

## Deployment Steps

### Option 1: Automated Deployment (Recommended)

```bash
# Deploy infrastructure
./scripts/deploy.sh dev

# Package and deploy Lambda functions
./scripts/package-lambdas.sh dev

# Test the deployment
./scripts/test.sh dev
```

### Option 2: Manual Deployment

#### Step 1: Deploy Infrastructure

```bash
aws cloudformation create-stack \
  --stack-name pai-agent-dev \
  --template-body file://infra/cloudformation/main.yaml \
  --parameters ParameterKey=EnvironmentName,ParameterValue=dev \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1

# Wait for completion
aws cloudformation wait stack-create-complete \
  --stack-name pai-agent-dev \
  --region us-east-1
```

#### Step 2: Package Lambda Functions

```bash
# Create package directory
mkdir -p build/lambda-packages

# Install dependencies
pip install -r requirements.txt -t build/lambda-packages/dependencies \
  --platform manylinux2014_aarch64 \
  --only-binary=:all: \
  --python-version 3.11

# Create Lambda packages
cd build/lambda-packages
mkdir agent memory search

# Copy dependencies and code
for func in agent memory search; do
  cp -r dependencies/* $func/
  cp -r ../../src/ $func/
  cp ../../src/lambdas/$func/handler.py $func/
  cd $func
  zip -r -q ../${func}.zip .
  cd ..
done
```

#### Step 3: Deploy Lambda Code

```bash
# Update each Lambda function
aws lambda update-function-code \
  --function-name pai-agent-dev \
  --zip-file fileb://build/lambda-packages/agent.zip

aws lambda update-function-code \
  --function-name pai-memory-dev \
  --zip-file fileb://build/lambda-packages/memory.zip

aws lambda update-function-code \
  --function-name pai-search-dev \
  --zip-file fileb://build/lambda-packages/search.zip
```

## Verify Deployment

### 1. Get API Endpoint

```bash
aws cloudformation describe-stacks \
  --stack-name pai-agent-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
  --output text
```

### 2. Test the API

```bash
# Send a test message
curl -X POST https://your-api-endpoint/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! What can you help me with?",
    "conversation_id": "test-001"
  }'
```

Expected response:
```json
{
  "conversation_id": "test-001",
  "message": "Hello! I'm your personal AI assistant...",
  "timestamp": 1234567890,
  "message_id": "msg-xxxxx"
}
```

### 3. Check Logs

```bash
# View Lambda logs
aws logs tail /aws/lambda/pai-agent-dev --follow
```

## Post-Deployment Configuration

### 1. Initialize Vector Index

The vector search index needs to be created on first use:

```bash
# This will be automatically created when the first memory is indexed
# Or you can create it manually via the OpenSearch dashboard
```

### 2. Configure Retention Policies

Update DynamoDB TTL settings if needed:
- Short-term memory: 7 days (default)
- Long-term memory: 365 days (default)

## Troubleshooting

### Common Issues

#### 1. Stack Creation Fails

**Problem**: CloudFormation stack fails to create

**Solutions**:
- Check AWS credentials: `aws sts get-caller-identity`
- Verify IAM permissions
- Check CloudFormation events for specific errors:
  ```bash
  aws cloudformation describe-stack-events --stack-name pai-agent-dev
  ```

#### 2. Lambda Function Fails

**Problem**: Lambda returns 500 error

**Solutions**:
- Check Lambda logs:
  ```bash
  aws logs tail /aws/lambda/pai-agent-dev --follow
  ```
- Verify environment variables are set
- Check IAM role permissions

#### 3. Bedrock Access Denied

**Problem**: "Access denied" when calling Bedrock

**Solutions**:
- Ensure you've requested model access in Bedrock console
- Verify IAM role has `bedrock:InvokeModel` permission
- Check the region supports Bedrock (us-east-1, us-west-2, etc.)

#### 4. OpenSearch Connection Issues

**Problem**: Vector search not working

**Solutions**:
- Verify OpenSearch Serverless collection is created
- Check network policy allows access
- Verify data access policy includes Lambda execution role

## Updating the Deployment

### Update Code Only

```bash
./scripts/package-lambdas.sh dev
```

### Update Infrastructure

```bash
./scripts/deploy.sh dev
```

### Full Redeployment

```bash
# Delete stack
./scripts/cleanup.sh dev

# Redeploy
./scripts/deploy.sh dev
./scripts/package-lambdas.sh dev
```

## Cost Management

### Expected Monthly Costs (Low Usage)

- **Lambda**: $1-3/month
- **DynamoDB**: $1-2/month
- **S3**: $0.50-1/month
- **OpenSearch Serverless**: $5-10/month
- **Bedrock**: $5-15/month

**Total**: ~$10-30/month

### Cost Optimization Tips

1. **Use ARM64 Lambda**: 20% cheaper (already configured)
2. **Enable S3 Intelligent-Tiering**: Automatic cost optimization
3. **Set appropriate TTLs**: Automatically delete old data
4. **Monitor Bedrock usage**: Most expensive component
5. **Consider pausing OpenSearch**: If not using search

## CI/CD with GitHub Actions

### Setup

1. Add AWS credentials to GitHub Secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_REGION`

2. Workflows are automatically triggered:
   - **test.yaml**: Runs on PRs and pushes to develop
   - **deploy.yaml**: Runs on pushes to main

### Manual Deployment

```bash
# Go to GitHub Actions → Deploy to AWS → Run workflow
# Select environment: dev/staging/prod
```

## Security Best Practices

1. **Rotate KMS Keys**: Enable automatic key rotation
2. **Review IAM Policies**: Follow least-privilege principle
3. **Enable CloudTrail**: Audit all API calls
4. **Use VPC Endpoints**: For private AWS service access (optional)
5. **Monitor Costs**: Set up billing alarms

## Monitoring

### CloudWatch Dashboards

Create custom dashboards to monitor:
- Lambda invocations and errors
- DynamoDB read/write capacity
- API Gateway requests
- Bedrock API calls

### Alarms

Set up CloudWatch alarms for:
- Lambda errors > threshold
- API Gateway 5xx errors
- DynamoDB throttling
- High costs

## Cleanup

To completely remove the deployment:

```bash
./scripts/cleanup.sh dev
```

This will:
1. Empty S3 buckets
2. Delete CloudFormation stack
3. Remove all resources
4. Clean build artifacts

## Next Steps

- Set up monitoring and alarms
- Configure backup policies
- Implement frontend application
- Add multi-user support (future)
- Integrate additional AI models

## Support

For issues or questions:
- Check CloudFormation events
- Review Lambda logs in CloudWatch
- Check the GitHub issues
- Review AWS service quotas
