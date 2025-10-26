#!/bin/bash

# Script to set up CloudWatch Logs role for API Gateway
# This enables API Gateway to write logs to CloudWatch
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

REGION=${AWS_REGION:-us-east-1}
ROLE_NAME="APIGatewayCloudWatchLogsRole"

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}API Gateway CloudWatch Logs Setup${NC}"
echo -e "${YELLOW}========================================${NC}"
echo "Region: $REGION"
echo -e "${YELLOW}========================================${NC}"

# Check if role already exists
if aws iam get-role --role-name "$ROLE_NAME" 2>/dev/null; then
    echo -e "${YELLOW}Role $ROLE_NAME already exists${NC}"
    ROLE_ARN=$(aws iam get-role --role-name "$ROLE_NAME" --query 'Role.Arn' --output text)
else
    echo -e "${YELLOW}Creating IAM role for API Gateway CloudWatch Logs...${NC}"

    # Create trust policy
    TRUST_POLICY=$(cat <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "apigateway.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
)

    # Create the IAM role
    aws iam create-role \
        --role-name "$ROLE_NAME" \
        --assume-role-policy-document "$TRUST_POLICY" \
        --description "Allows API Gateway to write logs to CloudWatch"

    echo -e "${GREEN}IAM role created${NC}"

    # Attach the managed policy
    echo -e "${YELLOW}Attaching CloudWatch Logs policy...${NC}"
    aws iam attach-role-policy \
        --role-name "$ROLE_NAME" \
        --policy-arn arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs

    echo -e "${GREEN}Policy attached${NC}"

    # Get the role ARN
    ROLE_ARN=$(aws iam get-role --role-name "$ROLE_NAME" --query 'Role.Arn' --output text)
fi

# Set the CloudWatch Logs role in API Gateway account settings
echo -e "${YELLOW}Configuring API Gateway account settings...${NC}"
aws apigateway update-account \
    --patch-operations op=replace,path=/cloudwatchRoleArn,value="$ROLE_ARN" \
    --region "$REGION"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo "CloudWatch Logs Role ARN: $ROLE_ARN"
echo ""
echo "Next steps:"
echo "1. Uncomment the LoggingLevel setting in infrastructure/templates/api.yaml"
echo "2. Redeploy your CloudFormation stack"
echo "3. API Gateway will now write logs to CloudWatch"
echo -e "${GREEN}========================================${NC}"
