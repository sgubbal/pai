#!/bin/bash
set -e

# Cleanup Script - Delete PAI Stack

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ENVIRONMENT=${1:-dev}
STACK_NAME="pai-agent-${ENVIRONMENT}"
REGION=${AWS_REGION:-us-east-1}

echo -e "${RED}========================================${NC}"
echo -e "${RED}PAI Agent Cleanup${NC}"
echo -e "${RED}========================================${NC}"
echo "Environment: $ENVIRONMENT"
echo "Stack Name: $STACK_NAME"
echo "Region: $REGION"
echo ""

# Confirmation
read -p "Are you sure you want to delete the stack? This cannot be undone. (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo ""
echo -e "${YELLOW}Step 1: Emptying S3 bucket...${NC}"

# Get bucket name
BUCKET_NAME=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`LongTermMemoryBucket`].OutputValue' \
    --output text 2>/dev/null || echo "")

if [ -n "$BUCKET_NAME" ]; then
    echo "Emptying bucket: $BUCKET_NAME"
    aws s3 rm s3://$BUCKET_NAME --recursive --region $REGION || true
    echo -e "${GREEN}✓ Bucket emptied${NC}"
else
    echo "Bucket not found, skipping..."
fi

echo ""
echo -e "${YELLOW}Step 2: Deleting CloudFormation stack...${NC}"

aws cloudformation delete-stack \
    --stack-name $STACK_NAME \
    --region $REGION

echo "Waiting for stack deletion..."
aws cloudformation wait stack-delete-complete \
    --stack-name $STACK_NAME \
    --region $REGION

echo -e "${GREEN}✓ Stack deleted${NC}"

echo ""
echo -e "${YELLOW}Step 3: Cleaning up build artifacts...${NC}"

rm -rf build/
rm -rf lambda-packages/

echo -e "${GREEN}✓ Build artifacts cleaned${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Cleanup Complete${NC}"
echo -e "${GREEN}========================================${NC}"
