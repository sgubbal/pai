# Quick Start Guide

Get your Personal AI Agent running in under 10 minutes!

## Prerequisites

- AWS Account
- AWS CLI configured
- Node.js 20+

## Step 1: Clone and Install

```bash
git clone <your-repo-url>
cd pai
npm install
```

## Step 2: Build the Project

```bash
npm run build
```

## Step 3: Deploy to AWS

```bash
# Deploy infrastructure (takes ~3-5 minutes)
./scripts/deploy.sh dev
```

## Step 4: Package and Deploy Functions

```bash
# Package Lambda functions
./scripts/package-functions.sh

# Deploy functions
./scripts/deploy-functions.sh dev
```

## Step 5: Test Your AI Agent

```bash
# Run smoke tests
./scripts/smoke-test.sh dev
```

## Step 6: Get Your API Endpoint

```bash
aws cloudformation describe-stacks \
  --stack-name pai-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
  --output text
```

## Example Usage

### Chat with AI

```bash
curl -X POST https://YOUR_API_ENDPOINT/dev/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, what can you help me with?",
    "useKnowledgeBase": true
  }'
```

Response:
```json
{
  "response": "AI response here...",
  "sessionId": "uuid-here",
  "timestamp": 1234567890
}
```

### Store Knowledge

```bash
curl -X POST https://YOUR_API_ENDPOINT/dev/memory \
  -H "Content-Type: application/json" \
  -d '{
    "action": "store",
    "content": "My birthday is January 15th",
    "category": "personal"
  }'
```

### Search Knowledge

```bash
curl -X POST https://YOUR_API_ENDPOINT/dev/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "when is my birthday",
    "topK": 5
  }'
```

## Next Steps

1. **Integrate LLM**: Add OpenAI or AWS Bedrock integration
2. **Build Frontend**: Create a web or mobile interface
3. **Add Authentication**: Secure your API endpoints
4. **Customize**: Modify Lambda functions for your use case

## Clean Up

When you're done testing:

```bash
./scripts/destroy.sh dev
```

## Cost Estimate

With light usage (testing):
- **First Month**: ~$1-2 (mostly free tier)
- **Ongoing**: ~$1-5/month for single user

The serverless architecture means you only pay for what you use!

## Troubleshooting

### Deployment Fails

Check CloudFormation events:
```bash
aws cloudformation describe-stack-events --stack-name pai-dev --max-items 20
```

### Function Errors

View logs:
```bash
aws logs tail /aws/lambda/pai-chat-dev --follow
```

### Need Help?

Check the full [DEPLOYMENT.md](./DEPLOYMENT.md) guide for detailed instructions.
