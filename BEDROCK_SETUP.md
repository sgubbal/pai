# AWS Bedrock Setup Guide

This guide walks you through enabling AWS Bedrock for your Personal AI Agent.

## Prerequisites

- AWS account
- AWS CLI configured
- Appropriate IAM permissions to enable Bedrock models

## Step 1: Enable Bedrock Models

AWS Bedrock requires you to request access to foundation models before using them.

### Via AWS Console

1. Navigate to AWS Bedrock console: https://console.aws.amazon.com/bedrock/
2. Click on **Model access** in the left sidebar
3. Click **Request model access** (or **Manage model access**)
4. Select the following models:
   - ✅ **Anthropic Claude 3.5 Sonnet** (for chat responses)
   - ✅ **Amazon Titan Embeddings G1 - Text**
   - ✅ **Amazon Titan Text Embeddings V2** (recommended)
5. Click **Request model access**
6. Wait for approval (usually instant for Titan, may take a few minutes for Claude)

### Via AWS CLI

```bash
# Check current model access
aws bedrock list-foundation-models --region us-east-1

# Note: Model access requests must be done via the console for the first time
```

## Step 2: Verify Region Availability

Bedrock is not available in all regions. Recommended regions:

- ✅ `us-east-1` (N. Virginia) - Best availability
- ✅ `us-west-2` (Oregon)
- ✅ `eu-central-1` (Frankfurt)
- ✅ `ap-southeast-1` (Singapore)

**Update your deployment region if needed:**

```bash
# In your .env or deployment scripts
export AWS_REGION=us-east-1
```

## Step 3: Verify IAM Permissions

Ensure your Lambda execution role has Bedrock permissions (already configured in CloudFormation):

```yaml
- Effect: Allow
  Action:
    - 'bedrock:InvokeModel'
    - 'bedrock:InvokeModelWithResponseStream'
  Resource:
    - 'arn:aws:bedrock:*::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0'
    - 'arn:aws:bedrock:*::foundation-model/amazon.titan-embed-text-v1'
    - 'arn:aws:bedrock:*::foundation-model/amazon.titan-embed-text-v2:0'
```

## Step 4: Test Bedrock Access

Test if you can invoke Bedrock models:

```bash
# Test Claude 3.5 Sonnet
aws bedrock-runtime invoke-model \
  --region us-east-1 \
  --model-id anthropic.claude-3-5-sonnet-20240620-v1:0 \
  --body '{"anthropic_version":"bedrock-2023-05-31","max_tokens":100,"messages":[{"role":"user","content":"Hello"}]}' \
  --cli-binary-format raw-in-base64-out \
  /tmp/response.json

cat /tmp/response.json

# Test Titan Embeddings
aws bedrock-runtime invoke-model \
  --region us-east-1 \
  --model-id amazon.titan-embed-text-v2:0 \
  --body '{"inputText":"Hello world"}' \
  --cli-binary-format raw-in-base64-out \
  /tmp/embedding.json

cat /tmp/embedding.json
```

## Step 5: Deploy Your Application

Once Bedrock access is enabled, deploy your application:

```bash
# Install dependencies
npm install

# Build TypeScript
npm run build

# Deploy infrastructure
./scripts/deploy.sh dev

# Package and deploy Lambda functions
./scripts/package-functions.sh
./scripts/deploy-functions.sh dev

# Test deployment
./scripts/smoke-test.sh dev
```

## Troubleshooting

### Error: "Model access denied"

**Solution**: Request model access in the Bedrock console (Step 1)

### Error: "ResourceNotFoundException: Could not resolve the foundation model"

**Possible causes**:
1. Wrong region - Bedrock may not be available in your region
2. Model ID incorrect - Check the model ID matches exactly
3. Model access not granted yet - Wait a few minutes and retry

**Solution**:
```bash
# Check available models in your region
aws bedrock list-foundation-models --region us-east-1 --query 'modelSummaries[?contains(modelId, `claude`) || contains(modelId, `titan`)].{ID:modelId,Name:modelName}' --output table
```

### Error: "AccessDeniedException"

**Solution**: Ensure your IAM role/user has `bedrock:InvokeModel` permission

```bash
# Check your current IAM identity
aws sts get-caller-identity

# Test if you have Bedrock permissions
aws bedrock list-foundation-models --region us-east-1
```

### Chat returns fallback error message

If you see: "I encountered an error while processing your request..."

**Check CloudWatch Logs:**
```bash
# Get recent Lambda logs
aws logs tail /aws/lambda/pai-chat-dev --follow --region us-east-1
```

Common causes:
- Bedrock not enabled in the region
- Model access not granted
- IAM permissions missing
- Request throttling (increase Lambda timeout or add retry logic)

## Cost Considerations

### Bedrock Pricing (as of 2024)

**Claude 3.5 Sonnet:**
- Input: $3.00 per million tokens (~750,000 words)
- Output: $15.00 per million tokens (~750,000 words)

**Titan Embeddings:**
- $0.0001 per 1,000 tokens (very cheap!)

### Example Usage Costs

| Usage Pattern | Monthly Cost |
|--------------|--------------|
| 100 chats/day (avg 500 tokens each) | ~$2-4 |
| 1000 chats/day | ~$20-40 |
| 100 embeddings/day | ~$0.10 |

**Note**: This is in addition to AWS infrastructure costs (~$1-2/month for Lambda, DynamoDB, etc.)

## Model Details

### Claude 3.5 Sonnet
- **Model ID**: `anthropic.claude-3-5-sonnet-20240620-v1:0`
- **Context Window**: 200K tokens
- **Max Output**: 4,096 tokens
- **Best For**: Complex reasoning, long conversations, nuanced responses

### Titan Embeddings V2
- **Model ID**: `amazon.titan-embed-text-v2:0`
- **Dimensions**: 1,024
- **Max Input**: 8,192 tokens
- **Best For**: Semantic search, RAG, similarity matching

### Titan Embeddings V1 (Fallback)
- **Model ID**: `amazon.titan-embed-text-v1`
- **Dimensions**: 1,536
- **Max Input**: 8,192 tokens

## Alternative Models

If Claude 3.5 Sonnet is not available, you can modify `src/lambda/chat.ts` to use:

### Claude 3 Haiku (Faster, Cheaper)
```typescript
modelId: 'anthropic.claude-3-haiku-20240307-v1:0'
```

### Claude 3 Opus (Most Capable)
```typescript
modelId: 'anthropic.claude-3-opus-20240229-v1:0'
```

## Next Steps

1. ✅ Enable Bedrock models in AWS Console
2. ✅ Deploy your application
3. ✅ Test the chat API
4. 📱 Build a frontend (web, mobile, CLI)
5. 🚀 Add more features (streaming, multi-modal, etc.)

## Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Claude on Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/models-claude.html)
- [Titan Embeddings](https://docs.aws.amazon.com/bedrock/latest/userguide/titan-embedding-models.html)
- [Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)

## Support

If you encounter issues:
1. Check CloudWatch Logs for Lambda errors
2. Verify model access in Bedrock console
3. Ensure you're in a supported region
4. Check IAM permissions

For more help, see the main [README.md](./README.md) or [DEPLOYMENT.md](./DEPLOYMENT.md).
