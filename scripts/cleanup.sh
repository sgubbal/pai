#!/bin/bash
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ENVIRONMENT=${1:-dev}
STACK_NAME="chatbot-${ENVIRONMENT}"
REGION=${AWS_REGION:-us-east-1}

echo -e "${RED}========================================${NC}"
echo -e "${RED}Chatbot Stack Cleanup${NC}"
echo -e "${RED}========================================${NC}"
echo "Environment: $ENVIRONMENT"
echo "Stack Name: $STACK_NAME"
echo ""

read -p "Are you sure you want to delete the stack? This cannot be undone. (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo ""
echo -e "${YELLOW}Step 1: Deleting CloudFormation stack...${NC}"

aws cloudformation delete-stack \
    --stack-name $STACK_NAME \
    --region $REGION

echo "Waiting for stack deletion..."
aws cloudformation wait stack-delete-complete \
    --stack-name $STACK_NAME \
    --region $REGION

echo -e "${GREEN}✓ Stack deleted${NC}"

echo ""
echo -e "${YELLOW}Step 2: Cleaning up build artifacts...${NC}"

rm -rf build/

echo -e "${GREEN}✓ Build artifacts cleaned${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Cleanup Complete${NC}"
echo -e "${GREEN}========================================${NC}"
