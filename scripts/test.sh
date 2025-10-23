#!/bin/bash
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ENVIRONMENT=${1:-dev}
STACK_NAME="chatbot-${ENVIRONMENT}"
REGION=${AWS_REGION:-us-east-1}

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Chatbot API Test${NC}"
echo -e "${GREEN}========================================${NC}"

# Get API endpoint
API_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
    --output text)

echo "API Endpoint: $API_ENDPOINT"
echo ""

# Test chat endpoint
echo -e "${YELLOW}Testing /chat endpoint...${NC}"

RESPONSE=$(curl -s -X POST "${API_ENDPOINT}/chat" \
    -H "Content-Type: application/json" \
    -d '{"conversation_id": "test-123", "message": "Hello! Tell me a short joke."}')

echo "Response:"
echo "$RESPONSE" | python3 -m json.tool

echo ""
echo -e "${GREEN}✓ Test complete${NC}"
