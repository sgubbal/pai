# PAI Agent - Quick Start Guide

Get your Personal AI Agent up and running in 15 minutes!

## Prerequisites

- AWS Account
- AWS CLI configured
- Python 3.11+
- jq (JSON processor)

## Step 1: Enable AWS Bedrock Models (5 minutes)

1. Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Navigate to **Model access** in the left sidebar
3. Click **Request model access** or **Manage model access**
4. Enable the following models:
   - ✅ **Claude 3 Sonnet** (anthropic.claude-3-sonnet-20240229-v1:0)
   - ✅ **Titan Embeddings V2** (amazon.titan-embed-text-v2:0)
5. Click **Save changes**
6. Wait for approval (usually instant)

## Step 2: Clone and Setup (2 minutes)

```bash
# Clone the repository
git clone <your-repo-url>
cd pai

# Copy environment template
cp .env.example .env

# Edit .env with your AWS account details
# Required: AWS_REGION, AWS_ACCOUNT_ID
nano .env

# Install dependencies
pip install -r requirements-dev.txt
```

## Step 3: Deploy Infrastructure (5-10 minutes)

```bash
# Make scripts executable (if not already)
chmod +x scripts/*.sh

# Deploy CloudFormation stack
./scripts/deploy.sh dev
```

This will create:
- ✅ KMS encryption key
- ✅ DynamoDB tables (conversations, memories)
- ✅ S3 bucket (long-term storage)
- ✅ OpenSearch Serverless (vector search)
- ✅ Lambda functions (agent, memory, search)
- ✅ API Gateway endpoint

## Step 4: Deploy Lambda Code (2 minutes)

```bash
# Package and deploy Lambda functions
./scripts/package-lambdas.sh dev
```

## Step 5: Test Your Agent (1 minute)

```bash
# Run automated tests
./scripts/test.sh dev
```

Or test manually:

```bash
# Get your API endpoint
export API_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name pai-agent-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
  --output text)

# Send a message
curl -X POST $API_ENDPOINT/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! What can you help me with?",
    "conversation_id": "quickstart-test"
  }'
```

Expected response:
```json
{
  "conversation_id": "quickstart-test",
  "message": "Hello! I'm your personal AI assistant...",
  "timestamp": 1234567890,
  "message_id": "msg-xxxxx"
}
```

## You're Done! 🎉

Your Personal AI Agent is now running on AWS!

## What's Next?

### Monitor Your Agent

```bash
# View real-time logs
aws logs tail /aws/lambda/pai-agent-dev --follow

# Check API Gateway metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name Count \
  --dimensions Name=ApiId,Value=YOUR_API_ID \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

### Try Advanced Features

#### 1. Have a Conversation

```bash
# First message
curl -X POST $API_ENDPOINT/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My favorite color is blue",
    "conversation_id": "conv-001"
  }'

# Follow-up (agent remembers context)
curl -X POST $API_ENDPOINT/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What did I just tell you?",
    "conversation_id": "conv-001"
  }'
```

#### 2. Search Memories

```bash
curl -X POST $API_ENDPOINT/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "favorite color",
    "limit": 5
  }'
```

#### 3. Retrieve Conversation History

```bash
curl -X GET $API_ENDPOINT/memory/conv-001
```

### Customize Your Agent

Edit the system prompt in `src/lambdas/agent/handler.py:88`:

```python
system_prompt = """You are a helpful personal AI assistant...
[Your custom instructions here]
"""
```

Then redeploy:
```bash
./scripts/package-lambdas.sh dev
```

## Common Issues

### Issue: "Access Denied" from Bedrock

**Solution**: Ensure you've enabled model access in the Bedrock console (Step 1)

### Issue: Stack creation fails

**Solution**: Check CloudFormation events:
```bash
aws cloudformation describe-stack-events \
  --stack-name pai-agent-dev \
  --max-items 10
```

### Issue: Lambda timeout

**Solution**: Bedrock first calls can be slow. Wait and retry, or increase Lambda timeout in `infra/cloudformation/compute.yaml`

## Cost Monitoring

Check your costs:

```bash
# Get current month costs
aws ce get-cost-and-usage \
  --time-period Start=$(date +%Y-%m-01),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics UnblendedCost \
  --group-by Type=SERVICE
```

Expected costs: $10-30/month for low usage

## Clean Up

To delete everything:

```bash
./scripts/cleanup.sh dev
```

**Warning**: This is permanent and will delete all your data!

## Next Steps

- 📖 Read [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment guide
- 🏗️ Read [ARCHITECTURE.md](./ARCHITECTURE.md) for technical details
- 🔧 Explore the code in `src/` directory
- 🚀 Set up CI/CD with GitHub Actions
- 💻 Build a frontend application

## Getting Help

- Check CloudWatch logs for errors
- Review the [DEPLOYMENT.md](./DEPLOYMENT.md) troubleshooting section
- Open an issue on GitHub

## API Reference

### POST /chat

Send a message to your AI agent.

**Request**:
```json
{
  "message": "Your message here",
  "conversation_id": "optional-id",
  "use_memory": true,
  "save_to_memory": true
}
```

**Response**:
```json
{
  "conversation_id": "conv-xxx",
  "message": "AI response",
  "timestamp": 1234567890,
  "message_id": "msg-xxx"
}
```

### POST /search

Semantic search across your memories.

**Request**:
```json
{
  "query": "Search query",
  "limit": 10,
  "category": "optional",
  "min_score": 0.5
}
```

**Response**:
```json
{
  "query": "Search query",
  "count": 3,
  "results": [
    {
      "memory": {...},
      "score": 0.95,
      "rank": 1
    }
  ]
}
```

### GET /memory/{conversation_id}

Get conversation history.

**Response**:
```json
{
  "conversation_id": "conv-xxx",
  "message_count": 10,
  "messages": [
    {
      "role": "user",
      "content": "...",
      "timestamp": 1234567890
    }
  ]
}
```

---

**Happy coding! Your AI agent is ready to assist you.** 🤖
