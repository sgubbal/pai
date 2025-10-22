#!/bin/bash

set -e

# Default values
ENVIRONMENT="${1:-dev}"
REGION="${AWS_REGION:-us-east-1}"
STACK_NAME="pai-${ENVIRONMENT}"

echo "==================================="
echo "Running Smoke Tests"
echo "==================================="

# Get API endpoint from CloudFormation outputs
API_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --region "${REGION}" \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
    --output text)

if [ -z "${API_ENDPOINT}" ]; then
    echo "Error: Could not retrieve API endpoint"
    exit 1
fi

echo "API Endpoint: ${API_ENDPOINT}"
echo ""

# Test 1: Chat endpoint
echo "Test 1: Chat endpoint..."
RESPONSE=$(curl -s -X POST "${API_ENDPOINT}/chat" \
    -H "Content-Type: application/json" \
    -d '{"message":"Hello, this is a test message"}')

if echo "${RESPONSE}" | jq -e '.sessionId' > /dev/null 2>&1; then
    echo "✓ Chat endpoint working"
    SESSION_ID=$(echo "${RESPONSE}" | jq -r '.sessionId')
    echo "  Session ID: ${SESSION_ID}"
else
    echo "✗ Chat endpoint failed"
    echo "${RESPONSE}"
    exit 1
fi

# Test 2: Memory storage
echo ""
echo "Test 2: Memory storage..."
RESPONSE=$(curl -s -X POST "${API_ENDPOINT}/memory" \
    -H "Content-Type: application/json" \
    -d '{"action":"store","content":"This is a test knowledge item","category":"test"}')

if echo "${RESPONSE}" | jq -e '.success' > /dev/null 2>&1; then
    echo "✓ Memory storage working"
    KNOWLEDGE_ID=$(echo "${RESPONSE}" | jq -r '.id')
    echo "  Knowledge ID: ${KNOWLEDGE_ID}"
else
    echo "✗ Memory storage failed"
    echo "${RESPONSE}"
    exit 1
fi

# Test 3: Vector search
echo ""
echo "Test 3: Vector search..."
RESPONSE=$(curl -s -X POST "${API_ENDPOINT}/search" \
    -H "Content-Type: application/json" \
    -d '{"query":"test knowledge","topK":5}')

if echo "${RESPONSE}" | jq -e '.results' > /dev/null 2>&1; then
    echo "✓ Vector search working"
    RESULT_COUNT=$(echo "${RESPONSE}" | jq '.count')
    echo "  Results found: ${RESULT_COUNT}"
else
    echo "✗ Vector search failed"
    echo "${RESPONSE}"
    exit 1
fi

# Test 4: Memory retrieval
echo ""
echo "Test 4: Memory retrieval..."
RESPONSE=$(curl -s -X POST "${API_ENDPOINT}/memory" \
    -H "Content-Type: application/json" \
    -d "{\"action\":\"retrieve\",\"sessionId\":\"${SESSION_ID}\"}")

if echo "${RESPONSE}" | jq -e '.messages' > /dev/null 2>&1; then
    echo "✓ Memory retrieval working"
    MESSAGE_COUNT=$(echo "${RESPONSE}" | jq '.count')
    echo "  Messages retrieved: ${MESSAGE_COUNT}"
else
    echo "✗ Memory retrieval failed"
    echo "${RESPONSE}"
    exit 1
fi

echo ""
echo "==================================="
echo "All smoke tests passed!"
echo "==================================="
