# PAI Deployment Guide

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
3. **Node.js** 20+ installed
4. **Git** installed

## Initial Setup

### 1. Configure AWS Credentials

```bash
aws configure
```

Or use environment variables:
```bash
export AWS_ACCESS_KEY_ID=your_key_id
export AWS_REGION=us-east-1
export AWS_SECRET_ACCESS_KEY=your_secret_key
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Build the Project

```bash
npm run build
```

## Deployment Options

### Option 1: Manual Deployment (Recommended for first-time)

#### Step 1: Deploy Infrastructure

```bash
./scripts/deploy.sh dev
```

This will:
- Create KMS encryption keys
- Set up DynamoDB tables for short-term and long-term memory
- Create S3 bucket for knowledge base
- Deploy Lambda functions (placeholder code)
- Set up HTTP API Gateway
- Configure all IAM roles and permissions

#### Step 2: Build and Package Lambda Functions

```bash
npm run build
./scripts/package-functions.sh
```

#### Step 3: Deploy Lambda Functions

```bash
./scripts/deploy-functions.sh dev
```

#### Step 4: Run Smoke Tests

```bash
./scripts/smoke-test.sh dev
```

### Option 2: Using GitHub Actions

1. **Set up GitHub Secrets**:
   - Go to repository Settings > Secrets and variables > Actions
   - Add secret: `AWS_ROLE_ARN` (ARN of IAM role for GitHub Actions)

2. **Configure OIDC Provider** (recommended over access keys):
   ```bash
   # Create OIDC provider for GitHub Actions
   aws iam create-open-id-connect-provider \
     --url https://token.actions.githubusercontent.com \
     --client-id-list sts.amazonaws.com \
     --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
   ```

3. **Push to main branch** or trigger workflow manually:
   - Push: `git push origin main`
   - Manual: Go to Actions tab > Deploy PAI to AWS > Run workflow

## Environment Configuration

### Development Environment

```bash
./scripts/deploy.sh dev
```

### Production Environment

```bash
./scripts/deploy.sh prod
```

## Post-Deployment

### Get API Endpoint

```bash
aws cloudformation describe-stacks \
  --stack-name pai-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
  --output text
```

### Test the API

```bash
# Chat endpoint
curl -X POST https://YOUR_API_ENDPOINT/dev/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello, AI!"}'

# Store knowledge
curl -X POST https://YOUR_API_ENDPOINT/dev/memory \
  -H "Content-Type: application/json" \
  -d '{"action":"store","content":"Important information","category":"notes"}'

# Search knowledge
curl -X POST https://YOUR_API_ENDPOINT/dev/search \
  -H "Content-Type: application/json" \
  -d '{"query":"important information","topK":5}'
```

## Cost Optimization Tips

1. **Lambda**:
   - Using ARM64 for ~20% cost savings
   - Reserved concurrency limits prevent runaway costs
   - Memory optimized per function

2. **DynamoDB**:
   - On-demand pricing (pay per request)
   - TTL enabled for short-term memory (auto-cleanup)
   - Point-in-time recovery for data protection

3. **S3**:
   - Intelligent-Tiering enabled
   - Lifecycle policies configured
   - Server-side encryption with KMS

4. **API Gateway**:
   - HTTP API (cheaper than REST API)
   - No custom domain (saves $0.50/month)

5. **Monitoring**:
   - CloudWatch Logs with 7-day retention
   - Basic monitoring only

**Expected Monthly Cost for Single User**: $1-5/month (depending on usage)

## LLM Integration (Next Steps)

### Option A: OpenAI

1. Get API key from https://platform.openai.com
2. Store in AWS Systems Manager Parameter Store:
   ```bash
   aws ssm put-parameter \
     --name /pai/dev/openai-api-key \
     --value "sk-xxxxx" \
     --type SecureString
   ```
3. Update Lambda code to use OpenAI API

### Option B: AWS Bedrock

1. Enable Bedrock in your AWS account
2. Update Lambda execution role with Bedrock permissions
3. Use Bedrock SDK in Lambda functions

## Troubleshooting

### CloudFormation Stack Failed

```bash
# Check stack events
aws cloudformation describe-stack-events \
  --stack-name pai-dev \
  --max-items 20

# Delete failed stack
./scripts/destroy.sh dev
```

### Lambda Function Errors

```bash
# View logs
aws logs tail /aws/lambda/pai-chat-dev --follow

# Update function code
./scripts/deploy-functions.sh dev
```

### Permission Errors

Check IAM role policies in CloudFormation template (infrastructure/main.yaml)

## Clean Up

To avoid ongoing costs, destroy the stack when not in use:

```bash
./scripts/destroy.sh dev
```

This will:
1. Empty S3 buckets
2. Delete all resources
3. Remove CloudFormation stack

## Security Notes

1. **Encryption**:
   - All data encrypted at rest with KMS
   - Client-side envelope encryption for sensitive data
   - TLS in transit via API Gateway

2. **Access Control**:
   - No public access to S3 buckets
   - Lambda functions have minimal IAM permissions
   - API Gateway has no authentication (add API keys or Cognito for production)

3. **For Production**:
   - Add API authentication (API keys, JWT, or Cognito)
   - Enable AWS WAF for API Gateway
   - Set up CloudTrail for audit logging
   - Enable VPC for Lambda functions if needed
   - Use AWS Secrets Manager for API keys
