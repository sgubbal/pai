#!/bin/bash

set -e

# Default values
ENVIRONMENT="${1:-dev}"
REGION="${AWS_REGION:-us-east-1}"
STACK_NAME="pai-${ENVIRONMENT}"

echo "==================================="
echo "WARNING: Destroying PAI Stack"
echo "==================================="
echo "Environment: ${ENVIRONMENT}"
echo "Region: ${REGION}"
echo "Stack Name: ${STACK_NAME}"
echo "==================================="

# Confirm destruction
read -p "Are you sure you want to destroy the ${ENVIRONMENT} environment? (yes/no): " CONFIRM
if [ "${CONFIRM}" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

# Get S3 buckets from stack
echo "Emptying S3 buckets..."
BUCKETS=$(aws cloudformation describe-stack-resources \
    --stack-name "${STACK_NAME}" \
    --region "${REGION}" \
    --query 'StackResources[?ResourceType==`AWS::S3::Bucket`].PhysicalResourceId' \
    --output text)

for BUCKET in ${BUCKETS}; do
    echo "Emptying bucket: ${BUCKET}"
    aws s3 rm "s3://${BUCKET}" --recursive --region "${REGION}" || true
done

# Delete CloudFormation stack
echo "Deleting CloudFormation stack..."
aws cloudformation delete-stack \
    --stack-name "${STACK_NAME}" \
    --region "${REGION}"

echo "Waiting for stack deletion..."
aws cloudformation wait stack-delete-complete \
    --stack-name "${STACK_NAME}" \
    --region "${REGION}"

echo "==================================="
echo "Stack destroyed successfully!"
echo "==================================="
