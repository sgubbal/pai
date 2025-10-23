#!/bin/bash
set -e

# Personal AI Chatbot Deployment Script

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Parameters
ENVIRONMENT=${1:-dev}
ENABLE_RAG=${2:-false}
STACK_NAME="chatbot-${ENVIRONMENT}"
REGION=${AWS_REGION:-us-east-1}
BUCKET_NAME="chatbot-cfn-artifacts-${ENVIRONMENT}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Personal AI Chatbot Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo "Environment: $ENVIRONMENT"
echo "Stack Name: $STACK_NAME"
echo "Region: $REGION"
echo "Enable RAG: $ENABLE_RAG"
echo ""

###################
# Step 1: Validate Templates
###################
echo -e "${YELLOW}Step 1: Validating CloudFormation templates...${NC}"

aws cloudformation validate-template \
    --template-body file://infra/cloudformation/main.yaml \
    --region $REGION > /dev/null

echo -e "${GREEN}✓ Templates validated${NC}"

###################
# Step 2: Create S3 Bucket for Artifacts
###################
echo ""
echo -e "${YELLOW}Step 2: Creating S3 bucket for CFN artifacts...${NC}"

if aws s3 ls "s3://${BUCKET_NAME}" 2>&1 | grep -q 'NoSuchBucket'; then
    aws s3 mb "s3://${BUCKET_NAME}" --region $REGION
    echo -e "${GREEN}✓ Bucket created${NC}"
else
    echo "Using existing bucket: ${BUCKET_NAME}"
fi

###################
# Step 3: Package Templates
###################
echo ""
echo -e "${YELLOW}Step 3: Packaging CloudFormation templates...${NC}"

aws cloudformation package \
    --template-file infra/cloudformation/main.yaml \
    --s3-bucket $BUCKET_NAME \
    --output-template-file /tmp/packaged-template.yaml \
    --region $REGION

echo -e "${GREEN}✓ Templates packaged${NC}"

###################
# Step 4: Deploy Stack
###################
echo ""
echo -e "${YELLOW}Step 4: Deploying CloudFormation stack...${NC}"

aws cloudformation deploy \
    --template-file /tmp/packaged-template.yaml \
    --stack-name $STACK_NAME \
    --parameter-overrides \
        Environment=$ENVIRONMENT \
        EnableRAG=$ENABLE_RAG \
    --capabilities CAPABILITY_NAMED_IAM \
    --region $REGION

echo -e "${GREEN}✓ Stack deployment completed${NC}"

###################
# Step 5: Get Outputs
###################
echo ""
echo -e "${YELLOW}Step 5: Getting stack outputs...${NC}"

aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`QuickStartGuide`].OutputValue' \
    --output text

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Deploy Lambda code: ./scripts/package-lambdas.sh $ENVIRONMENT"
echo "2. Test the API: ./scripts/test.sh $ENVIRONMENT"
echo ""
