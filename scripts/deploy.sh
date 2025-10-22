#!/bin/bash
set -e

# PAI Agent Deployment Script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT=${1:-dev}
STACK_NAME="pai-agent-${ENVIRONMENT}"
REGION=${AWS_REGION:-us-east-1}

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}PAI Agent Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo "Environment: $ENVIRONMENT"
echo "Stack Name: $STACK_NAME"
echo "Region: $REGION"
echo ""

# Check AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed${NC}"
    exit 1
fi

# Check AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}Error: AWS credentials not configured${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Validating CloudFormation templates...${NC}"

# Validate main template
aws cloudformation validate-template \
    --template-body file://infra/cloudformation/main.yaml \
    --region $REGION > /dev/null

echo -e "${GREEN}✓ Main template is valid${NC}"

# Validate nested templates
for template in infra/cloudformation/{security,storage,ai,compute}.yaml; do
    aws cloudformation validate-template \
        --template-body file://$template \
        --region $REGION > /dev/null
    echo -e "${GREEN}✓ $(basename $template) is valid${NC}"
done

echo ""
echo -e "${YELLOW}Step 2: Creating S3 bucket for CloudFormation artifacts...${NC}"

# Create unique bucket name
BUCKET_NAME="pai-cfn-artifacts-${ENVIRONMENT}-$(aws sts get-caller-identity --query Account --output text)"

# Create bucket if it doesn't exist
if ! aws s3 ls "s3://$BUCKET_NAME" 2>&1 | grep -q 'NoSuchBucket'; then
    echo "Using existing bucket: $BUCKET_NAME"
else
    echo "Creating bucket: $BUCKET_NAME"
    aws s3 mb "s3://$BUCKET_NAME" --region $REGION
fi

echo -e "${GREEN}✓ S3 bucket ready${NC}"

echo ""
echo -e "${YELLOW}Step 3: Packaging CloudFormation templates...${NC}"

# Package the template (uploads nested stacks to S3)
aws cloudformation package \
    --template-file infra/cloudformation/main.yaml \
    --s3-bucket $BUCKET_NAME \
    --s3-prefix cloudformation-templates \
    --output-template-file /tmp/packaged-template.yaml \
    --region $REGION

echo -e "${GREEN}✓ Templates packaged and uploaded to S3${NC}"

echo ""
echo -e "${YELLOW}Step 4: Deploying CloudFormation stack...${NC}"

# Deploy the packaged template
aws cloudformation deploy \
    --stack-name $STACK_NAME \
    --template-file /tmp/packaged-template.yaml \
    --parameter-overrides EnvironmentName=$ENVIRONMENT \
    --capabilities CAPABILITY_NAMED_IAM \
    --region $REGION

echo -e "${GREEN}✓ Stack deployment completed successfully${NC}"

echo ""
echo -e "${YELLOW}Step 5: Getting stack outputs...${NC}"

# Get stack outputs
OUTPUTS=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs' \
    --output json)

# Display key outputs
API_ENDPOINT=$(echo $OUTPUTS | jq -r '.[] | select(.OutputKey=="ApiEndpoint") | .OutputValue')
AGENT_FUNCTION=$(echo $OUTPUTS | jq -r '.[] | select(.OutputKey=="AgentFunctionName") | .OutputValue')

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "API Endpoint: $API_ENDPOINT"
echo "Agent Function: $AGENT_FUNCTION"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Package and deploy Lambda functions:"
echo "   ./scripts/package-lambdas.sh"
echo ""
echo "2. Test the deployment:"
echo "   ./scripts/test.sh"
echo ""
echo "3. View logs:"
echo "   aws logs tail /aws/lambda/$AGENT_FUNCTION --follow"
echo ""
