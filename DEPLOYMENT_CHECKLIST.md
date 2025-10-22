# Deployment Checklist

Use this checklist to deploy your Personal AI Agent to AWS.

## Prerequisites

- [ ] AWS account created
- [ ] AWS CLI installed and configured (`aws configure`)
- [ ] Node.js 20+ installed
- [ ] Git installed

## Step 1: Enable AWS Bedrock (5 minutes)

- [ ] Navigate to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/)
- [ ] Select your region (recommend `us-east-1`)
- [ ] Click "Model access" in sidebar
- [ ] Click "Request model access"
- [ ] Enable these models:
  - [ ] ✅ Anthropic Claude 3.5 Sonnet
  - [ ] ✅ Amazon Titan Text Embeddings V2
  - [ ] ✅ Amazon Titan Text Embeddings (V1, as fallback)
- [ ] Wait for approval (usually instant)

**Detailed instructions**: See [BEDROCK_SETUP.md](./BEDROCK_SETUP.md)

## Step 2: Clone and Setup (2 minutes)

```bash
# Clone the repository (if not already done)
git clone <your-repo-url>
cd pai

# Install dependencies
./scripts/setup.sh
```

- [ ] Dependencies installed successfully
- [ ] No errors in setup script

## Step 3: Configure Environment (1 minute)

```bash
# Copy environment template
cp .env.example .env

# Edit .env and set your AWS region
nano .env  # or use your preferred editor
```

Update these values in `.env`:
- [ ] `AWS_REGION` - Your AWS region (e.g., `us-east-1`)
- [ ] `AWS_ACCOUNT_ID` - Your AWS account ID
- [ ] `ENVIRONMENT` - `dev` for testing, `prod` for production

## Step 4: Deploy Infrastructure (5 minutes)

```bash
# Deploy CloudFormation stack
./scripts/deploy.sh dev
```

This creates:
- [ ] DynamoDB tables (conversations, knowledge)
- [ ] S3 bucket (knowledge base)
- [ ] KMS encryption key
- [ ] Lambda functions (placeholder code)
- [ ] API Gateway endpoints
- [ ] IAM roles and policies

**Wait for**: `CREATE_COMPLETE` status

## Step 5: Build Application (2 minutes)

```bash
# Compile TypeScript to JavaScript
npm run build
```

- [ ] TypeScript compiled successfully
- [ ] No build errors
- [ ] `dist/` directory created

## Step 6: Deploy Lambda Functions (3 minutes)

```bash
# Package Lambda functions
./scripts/package-functions.sh

# Deploy to AWS
./scripts/deploy-functions.sh dev
```

This updates:
- [ ] Chat Lambda with Bedrock integration
- [ ] Memory Lambda with encryption
- [ ] Vector Search Lambda with Titan embeddings

**Wait for**: Function updates to complete

## Step 7: Test Deployment (2 minutes)

```bash
# Run smoke tests
./scripts/smoke-test.sh dev
```

Expected results:
- [ ] ✅ Chat API responds successfully
- [ ] ✅ Memory storage works
- [ ] ✅ Vector search works
- [ ] ✅ Encryption/decryption works

## Step 8: Get API Endpoint

```bash
# Get your API endpoint
aws cloudformation describe-stacks \
  --stack-name pai-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
  --output text
```

- [ ] Copy API endpoint URL
- [ ] Save for frontend integration

Example: `https://abc123xyz.execute-api.us-east-1.amazonaws.com/dev`

## Step 9: Test Chat (2 minutes)

```bash
# Replace with your actual API endpoint
export API_ENDPOINT="https://your-api-endpoint.amazonaws.com/dev"

# Test chat
curl -X POST "$API_ENDPOINT/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! Can you introduce yourself?",
    "useKnowledgeBase": false
  }'
```

Expected response:
- [ ] Status 200 OK
- [ ] Response contains AI-generated text from Claude
- [ ] Session ID returned
- [ ] No errors

## Step 10: Test Knowledge Base (optional, 5 minutes)

```bash
# Store knowledge
curl -X POST "$API_ENDPOINT/memory" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "store",
    "content": "My favorite programming language is TypeScript",
    "category": "preferences"
  }'

# Search knowledge
curl -X POST "$API_ENDPOINT/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "programming language preference",
    "topK": 3
  }'

# Chat with knowledge base
curl -X POST "$API_ENDPOINT/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is my favorite programming language?",
    "useKnowledgeBase": true
  }'
```

- [ ] Knowledge stored successfully
- [ ] Vector search returns results
- [ ] Chat uses knowledge base context

## Verification Checklist

### Infrastructure
- [ ] CloudFormation stack status: `CREATE_COMPLETE`
- [ ] All Lambda functions deployed
- [ ] API Gateway endpoint accessible
- [ ] DynamoDB tables created
- [ ] S3 bucket created and encrypted
- [ ] KMS key created

### Functionality
- [ ] Chat API returns Claude responses
- [ ] Conversation history persists
- [ ] Memory storage works
- [ ] Vector search returns relevant results
- [ ] Encryption/decryption works
- [ ] Knowledge base integration works

### Security
- [ ] All data encrypted at rest (DynamoDB, S3)
- [ ] TLS encryption in transit
- [ ] IAM roles follow least privilege
- [ ] No public S3 access
- [ ] KMS key properly configured

### Cost Optimization
- [ ] Lambda uses ARM64 architecture
- [ ] DynamoDB in on-demand mode
- [ ] S3 Intelligent-Tiering enabled
- [ ] HTTP API (not REST API)
- [ ] Reserved concurrency limits set

## Troubleshooting

### Bedrock Access Denied
**Error**: "Model access denied"
**Solution**: Enable models in Bedrock console (Step 1)

### Lambda Timeout
**Error**: "Task timed out after 30.00 seconds"
**Solution**: Check CloudWatch logs, may need to increase timeout

### CloudFormation Failed
**Error**: Stack creation failed
**Solution**:
```bash
# Check stack events
aws cloudformation describe-stack-events --stack-name pai-dev

# Delete failed stack
./scripts/destroy.sh dev

# Try again
./scripts/deploy.sh dev
```

### Chat Returns Error
**Error**: Chat returns Bedrock error message
**Solution**:
1. Verify Bedrock models enabled
2. Check Lambda IAM permissions
3. Verify region matches Bedrock availability
4. Check CloudWatch logs

## Next Steps

After successful deployment:

1. **Build a frontend**
   - React/Next.js web app
   - Mobile app
   - CLI tool

2. **Add features**
   - Streaming responses
   - Multi-modal support
   - Voice interface
   - Advanced memory management

3. **Production hardening**
   - Add authentication
   - Set up monitoring/alerts
   - Enable WAF
   - Multi-region deployment

4. **Scale**
   - Increase Lambda concurrency
   - Add caching layer
   - Consider OpenSearch for large knowledge bases

## Cost Monitoring

```bash
# Check estimated costs
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --filter file://cost-filter.json
```

Expected costs (single user):
- Infrastructure: $1-2/month
- Bedrock (moderate usage): $2-5/month
- **Total**: $3-7/month

## Support

- **Documentation**: See [README.md](./README.md)
- **Bedrock Setup**: See [BEDROCK_SETUP.md](./BEDROCK_SETUP.md)
- **Architecture**: See [ARCHITECTURE.md](./ARCHITECTURE.md)
- **API Docs**: See [API.md](./API.md)

## Cleanup

To delete all resources:

```bash
# Destroy stack
./scripts/destroy.sh dev

# Verify deletion
aws cloudformation describe-stacks --stack-name pai-dev
```

---

**🎉 Congratulations!** You've successfully deployed your Personal AI Agent!
