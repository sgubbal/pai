# Quick Start Guide

Get your PAI chatbot running in under 10 minutes!

## Prerequisites Check

```bash
# Check AWS CLI
aws --version

# Check Python
python3 --version  # Should be 3.12+

# Check jq
jq --version

# Verify AWS credentials
aws sts get-caller-identity
```

## Step-by-Step Deployment

### 1. Generate API Key (2 minutes)

```bash
# Generate a secure 32-character API key
API_KEY=$(openssl rand -base64 32)
echo "Your API Key: $API_KEY"
echo "SAVE THIS - You'll need it to access your chatbot!"
```

### 2. Configure Parameters (2 minutes)

```bash
# Navigate to parameters
cd infrastructure/parameters

# Choose a unique S3 bucket name
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
S3_BUCKET="pai-deployment-${AWS_ACCOUNT_ID}"

# Update dev.json
jq --arg key "$API_KEY" \
   --arg bucket "$S3_BUCKET" \
   '(.[] | select(.ParameterKey=="ApiKeyValue") | .ParameterValue) = $key |
    (.[] | select(.ParameterKey=="S3BucketName") | .ParameterValue) = $bucket' \
   dev.json > dev.json.tmp && mv dev.json.tmp dev.json

echo "Configuration updated!"
```

### 3. Deploy (5 minutes)

```bash
# Go back to project root
cd ../..

# Deploy to dev environment
./scripts/deploy.sh dev
```

Wait for the deployment to complete. You'll see:
```
========================================
Deployment Complete!
========================================
API Endpoint: https://xxxxx.execute-api.us-east-1.amazonaws.com/dev
```

### 4. Test Your Chatbot (1 minute)

```bash
# Set your API endpoint and key
API_ENDPOINT="<your-endpoint-from-above>"
API_KEY="<your-api-key-from-step-1>"

# Test it!
curl -X POST $API_ENDPOINT/chat \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! Can you explain what AWS Lambda is in simple terms?"
  }'
```

You should get a response like:
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "AWS Lambda is a serverless compute service...",
  "usage": {
    "input_tokens": 20,
    "output_tokens": 150
  },
  "model": "anthropic.claude-3-5-sonnet-20241022-v2:0"
}
```

## Common First Commands

### Continue a conversation
```bash
CONVERSATION_ID="<id-from-previous-response>"

curl -X POST $API_ENDPOINT/chat \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"conversation_id\": \"$CONVERSATION_ID\",
    \"message\": \"Can you give me an example?\"
  }"
```

### Get conversation history
```bash
curl -X GET $API_ENDPOINT/conversations/$CONVERSATION_ID \
  -H "Authorization: Bearer $API_KEY"
```

### Create a new conversation explicitly
```bash
curl -X POST $API_ENDPOINT/conversations \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "initial_message": "Hi there!"
  }'
```

## Troubleshooting

### Issue: "Unauthorized"
**Solution**: Check your API key format
```bash
# Should be: Authorization: Bearer <your-key>
# NOT: Authorization: <your-key>
```

### Issue: Deployment fails
**Solution**: Check CloudFormation events
```bash
aws cloudformation describe-stack-events \
  --stack-name pai-chatbot-dev \
  --max-items 10
```

### Issue: Lambda timeout
**Solution**: Check logs
```bash
aws logs tail /aws/lambda/pai-chatbot-dev --follow
```

## View Your Resources

### CloudFormation Stack
```bash
aws cloudformation describe-stacks --stack-name pai-chatbot-dev
```

### DynamoDB Table
```bash
aws dynamodb describe-table --table-name PAI-Conversations-dev
```

### Lambda Functions
```bash
aws lambda list-functions --query 'Functions[?starts_with(FunctionName, `pai-`)]'
```

### API Gateway
```bash
aws apigateway get-rest-apis --query 'items[?name==`pai-api-dev`]'
```

## Next Steps

1. **Add GitHub Secrets** for CI/CD
   ```
   AWS_ACCESS_KEY_ID
   AWS_SECRET_ACCESS_KEY
   API_KEY
   S3_BUCKET_NAME
   ```

2. **Monitor Costs**
   - Set up AWS Cost Explorer
   - Create billing alarms

3. **Customize**
   - Adjust system prompts in your requests
   - Modify Lambda memory/timeout in `compute.yaml`
   - Update Bedrock model in `constants.py`

4. **Scale to RAG**
   - Follow the RAG extension guide in README.md

## Cleanup

When you're done testing:
```bash
./scripts/cleanup.sh dev
```

This will delete all resources (you'll be prompted to confirm).

## Cost Estimate

For testing (first month):
- Free tier eligible: ~$0-5
- Light usage: ~$10-20/month
- See README.md for detailed cost breakdown

## Getting Help

- Check full documentation: `README.md`
- View CloudFormation templates: `infrastructure/templates/`
- Run tests: `pytest tests/ -v`

Enjoy your personal AI chatbot!
