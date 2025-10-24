#!/bin/bash

# Script to cleanup/destroy PAI chatbot infrastructure
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT=${1:-dev}
STACK_NAME="pai-chatbot-${ENVIRONMENT}"
REGION=${AWS_REGION:-us-east-1}

echo -e "${RED}========================================${NC}"
echo -e "${RED}PAI Chatbot Cleanup${NC}"
echo -e "${RED}========================================${NC}"
echo "Environment: $ENVIRONMENT"
echo "Stack Name: $STACK_NAME"
echo "Region: $REGION"
echo -e "${RED}========================================${NC}"

# Confirm deletion
read -p "Are you sure you want to delete the $STACK_NAME stack? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "Cleanup cancelled"
    exit 0
fi

# Delete CloudFormation stack
echo -e "${YELLOW}Deleting CloudFormation stack...${NC}"
aws cloudformation delete-stack \
    --stack-name "$STACK_NAME" \
    --region "$REGION"

echo -e "${YELLOW}Waiting for stack deletion...${NC}"
aws cloudformation wait stack-delete-complete \
    --stack-name "$STACK_NAME" \
    --region "$REGION"

echo -e "${GREEN}Stack deleted successfully${NC}"

# Cleanup S3 bucket (optional)
read -p "Do you want to delete the S3 bucket as well? (yes/no): " DELETE_S3
if [ "$DELETE_S3" == "yes" ]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
    PARAMS_FILE="$PROJECT_ROOT/infrastructure/parameters/${ENVIRONMENT}.json"

    if [ -f "$PARAMS_FILE" ]; then
        S3_BUCKET=$(jq -r '.[] | select(.ParameterKey=="S3BucketName") | .ParameterValue' "$PARAMS_FILE")

        if [ -n "$S3_BUCKET" ] && [ "$S3_BUCKET" != "REPLACE_WITH_YOUR_S3_BUCKET" ]; then
            echo -e "${YELLOW}Emptying S3 bucket...${NC}"
            aws s3 rm "s3://${S3_BUCKET}" --recursive

            echo -e "${YELLOW}Deleting S3 bucket...${NC}"
            aws s3 rb "s3://${S3_BUCKET}"

            echo -e "${GREEN}S3 bucket deleted${NC}"
        fi
    fi
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Cleanup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
