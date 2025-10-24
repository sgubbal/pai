#!/bin/bash

# Script to deploy PAI chatbot infrastructure
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

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$PROJECT_ROOT/build"
TEMPLATE_DIR="$PROJECT_ROOT/infrastructure/templates"
PARAMS_FILE="$PROJECT_ROOT/infrastructure/parameters/${ENVIRONMENT}.json"

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}PAI Chatbot Deployment${NC}"
echo -e "${YELLOW}========================================${NC}"
echo "Environment: $ENVIRONMENT"
echo "Stack Name: $STACK_NAME"
echo "Region: $REGION"
echo -e "${YELLOW}========================================${NC}"

# Check if parameter file exists
if [ ! -f "$PARAMS_FILE" ]; then
    echo -e "${RED}Error: Parameter file not found: $PARAMS_FILE${NC}"
    exit 1
fi

# Read S3 bucket name from parameters
S3_BUCKET=$(jq -r '.[] | select(.ParameterKey=="S3BucketName") | .ParameterValue' "$PARAMS_FILE")

if [ "$S3_BUCKET" == "REPLACE_WITH_YOUR_S3_BUCKET" ] || [ -z "$S3_BUCKET" ]; then
    echo -e "${RED}Error: S3 bucket name not configured in $PARAMS_FILE${NC}"
    echo "Please update the S3BucketName parameter"
    exit 1
fi

# Check if API key is configured
API_KEY=$(jq -r '.[] | select(.ParameterKey=="ApiKeyValue") | .ParameterValue' "$PARAMS_FILE")
if [ "$API_KEY" == "REPLACE_WITH_YOUR_API_KEY" ] || [ -z "$API_KEY" ]; then
    echo -e "${RED}Error: API key not configured in $PARAMS_FILE${NC}"
    echo "Please update the ApiKeyValue parameter"
    exit 1
fi

# Create S3 bucket if it doesn't exist
echo -e "${YELLOW}Checking S3 bucket...${NC}"
if ! aws s3 ls "s3://${S3_BUCKET}" 2>/dev/null; then
    echo -e "${YELLOW}Creating S3 bucket: ${S3_BUCKET}${NC}"
    aws s3 mb "s3://${S3_BUCKET}" --region "$REGION"

    # Enable versioning
    aws s3api put-bucket-versioning \
        --bucket "${S3_BUCKET}" \
        --versioning-configuration Status=Enabled
else
    echo -e "${GREEN}S3 bucket exists: ${S3_BUCKET}${NC}"
fi

# Package Lambda functions
echo -e "${YELLOW}Packaging Lambda functions...${NC}"
bash "$SCRIPT_DIR/package-lambdas.sh"

# Upload Lambda packages to S3
echo -e "${YELLOW}Uploading Lambda packages to S3...${NC}"
aws s3 cp "$BUILD_DIR/layers/dependencies.zip" "s3://${S3_BUCKET}/layers/dependencies.zip"
aws s3 cp "$BUILD_DIR/functions/chatbot.zip" "s3://${S3_BUCKET}/functions/chatbot.zip"
aws s3 cp "$BUILD_DIR/functions/authorizer.zip" "s3://${S3_BUCKET}/functions/authorizer.zip"
echo -e "${GREEN}Lambda packages uploaded${NC}"

# Upload CloudFormation templates to S3
echo -e "${YELLOW}Uploading CloudFormation templates to S3...${NC}"
aws s3 cp "$TEMPLATE_DIR/" "s3://${S3_BUCKET}/templates/" --recursive --exclude "*" --include "*.yaml"
echo -e "${GREEN}Templates uploaded${NC}"

# Deploy CloudFormation stack
echo -e "${YELLOW}Deploying CloudFormation stack...${NC}"
aws cloudformation deploy \
    --template-file "$TEMPLATE_DIR/main.yaml" \
    --stack-name "$STACK_NAME" \
    --parameter-overrides file://"$PARAMS_FILE" \
    --capabilities CAPABILITY_NAMED_IAM \
    --region "$REGION" \
    --no-fail-on-empty-changeset

# Get stack outputs
echo -e "${YELLOW}Retrieving stack outputs...${NC}"
API_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
    --output text)

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo "API Endpoint: $API_ENDPOINT"
echo ""
echo "Next steps:"
echo "1. Test the API using:"
echo "   curl -X POST $API_ENDPOINT/chat \\"
echo "     -H 'Authorization: Bearer YOUR_API_KEY' \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"message\": \"Hello, how are you?\"}'"
echo ""
echo "2. View logs:"
echo "   aws logs tail /aws/lambda/pai-chatbot-${ENVIRONMENT} --follow"
echo -e "${GREEN}========================================${NC}"
