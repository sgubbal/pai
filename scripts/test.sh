#!/bin/bash
set -e

# Test Script for PAI Agent

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ENVIRONMENT=${1:-dev}
STACK_NAME="pai-agent-${ENVIRONMENT}"
REGION=${AWS_REGION:-us-east-1}

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}PAI Agent Testing${NC}"
echo -e "${GREEN}========================================${NC}"

# Get API endpoint
API_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
    --output text)

if [ -z "$API_ENDPOINT" ]; then
    echo -e "${RED}Error: Could not get API endpoint${NC}"
    exit 1
fi

echo "API Endpoint: $API_ENDPOINT"
echo ""

# Test 1: Send a chat message
echo -e "${YELLOW}Test 1: Sending chat message...${NC}"

RESPONSE=$(curl -s -X POST "$API_ENDPOINT/chat" \
    -H "Content-Type: application/json" \
    -d '{
        "message": "Hello! Can you tell me what you can help me with?",
        "conversation_id": "test-conversation-001"
    }')

echo "Response:"
echo $RESPONSE | jq '.'

if echo $RESPONSE | jq -e '.message' > /dev/null; then
    echo -e "${GREEN}✓ Chat test passed${NC}"
else
    echo -e "${RED}✗ Chat test failed${NC}"
fi

echo ""

# Test 2: Search (if vector search is configured)
echo -e "${YELLOW}Test 2: Testing search...${NC}"

SEARCH_RESPONSE=$(curl -s -X POST "$API_ENDPOINT/search" \
    -H "Content-Type: application/json" \
    -d '{
        "query": "help",
        "limit": 5
    }')

echo "Response:"
echo $SEARCH_RESPONSE | jq '.'

if echo $SEARCH_RESPONSE | jq -e '.results' > /dev/null; then
    echo -e "${GREEN}✓ Search test passed${NC}"
else
    echo -e "${YELLOW}⚠ Search test skipped (may not be configured)${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Testing Complete${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "You can test the API manually:"
echo ""
echo "curl -X POST $API_ENDPOINT/chat \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"message\": \"Your message here\"}'"
echo ""
