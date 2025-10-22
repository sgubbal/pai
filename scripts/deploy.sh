#!/bin/bash

set -e

# Default values
ENVIRONMENT="${1:-dev}"
REGION="${AWS_REGION:-us-east-1}"
STACK_NAME="pai-${ENVIRONMENT}"

echo "==================================="
echo "Deploying PAI Infrastructure"
echo "==================================="
echo "Environment: ${ENVIRONMENT}"
echo "Region: ${REGION}"
echo "Stack Name: ${STACK_NAME}"
echo "==================================="

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "Error: AWS CLI is not installed"
    exit 1
fi

# Check AWS credentials
echo "Checking AWS credentials..."
aws sts get-caller-identity > /dev/null || {
    echo "Error: AWS credentials not configured"
    exit 1
}

# Package CloudFormation template
echo "Packaging CloudFormation template..."
aws cloudformation package \
    --template-file infrastructure/main.yaml \
    --s3-bucket "pai-cfn-artifacts-$(aws sts get-caller-identity --query Account --output text)" \
    --s3-prefix "${ENVIRONMENT}/cfn" \
    --output-template-file infrastructure/packaged-main.yaml \
    --region "${REGION}" 2>/dev/null || {
    echo "Creating artifacts bucket..."
    BUCKET_NAME="pai-cfn-artifacts-$(aws sts get-caller-identity --query Account --output text)"
    aws s3 mb "s3://${BUCKET_NAME}" --region "${REGION}" 2>/dev/null || true

    aws cloudformation package \
        --template-file infrastructure/main.yaml \
        --s3-bucket "${BUCKET_NAME}" \
        --s3-prefix "${ENVIRONMENT}/cfn" \
        --output-template-file infrastructure/packaged-main.yaml \
        --region "${REGION}"
}

# Deploy CloudFormation stack
echo "Deploying CloudFormation stack..."
aws cloudformation deploy \
    --template-file infrastructure/packaged-main.yaml \
    --stack-name "${STACK_NAME}" \
    --parameter-overrides Environment="${ENVIRONMENT}" \
    --capabilities CAPABILITY_NAMED_IAM \
    --region "${REGION}" \
    --no-fail-on-empty-changeset

# Get stack outputs
echo "Retrieving stack outputs..."
aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --region "${REGION}" \
    --query 'Stacks[0].Outputs' \
    --output table

# Save outputs to file
aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --region "${REGION}" \
    --query 'Stacks[0].Outputs' \
    --output json > outputs.json

echo "==================================="
echo "Infrastructure deployment complete!"
echo "==================================="
