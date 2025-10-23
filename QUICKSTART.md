# Quick Start Guide

## 🚀 Deploy Your Chatbot in 3 Steps

### Step 1: Deploy Infrastructure

```bash
./scripts/deploy.sh dev
```

This creates:
- ✅ API Gateway endpoint
- ✅ Lambda function (chat handler)
- ✅ DynamoDB table (conversations)
- ✅ KMS encryption key
- ✅ IAM roles

**Time**: ~3-5 minutes

### Step 2: Deploy Lambda Code

```bash
./scripts/package-lambdas.sh dev
```

This:
- ✅ Installs Python dependencies
- ✅ Packages Lambda function
- ✅ Uploads to AWS

**Time**: ~1-2 minutes

### Step 3: Test Your Chatbot

```bash
./scripts/test.sh dev
```

Or manually:

```bash
# Get endpoint
ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name chatbot-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
  --output text)

# Send message
curl -X POST "${ENDPOINT}/chat" \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": "test", "message": "Hello!"}'
```

## 📊 What You Get

### Phase 1 (Deployed)
- Conversational AI with Claude 3.5 Sonnet
- Conversation history (last 10 messages)
- Auto-expiring data (30 days)
- End-to-end encryption
- RESTful API

**Cost**: ~$10/month

### Phase 2 (Optional - Enable Later)

When ready:

```bash
./scripts/deploy.sh dev true  # Enable RAG
```

This adds:
- Document upload (S3)
- Semantic search (OpenSearch)
- Vector embeddings (Bedrock Titan)
- RAG capabilities

**Additional Cost**: ~$15-20/month

## 🔍 Verify Deployment

```bash
# Check stack status
aws cloudformation describe-stacks \
  --stack-name chatbot-dev \
  --query 'Stacks[0].StackStatus'

# View Lambda logs
aws logs tail /aws/lambda/chatbot-chat-dev --follow
```

## 🧹 Cleanup

```bash
./scripts/cleanup.sh dev
```

## Next Steps

1. Read [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
2. Read [README.md](README.md) for full documentation
3. Set up GitHub Actions for CI/CD
4. Enable RAG when ready for Phase 2

---

**Questions?** Check the [README](README.md) or [ARCHITECTURE](ARCHITECTURE.md)
