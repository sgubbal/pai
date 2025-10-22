#!/bin/bash

set -e

# Default values
ENVIRONMENT="${1:-dev}"
REGION="${AWS_REGION:-us-east-1}"
STACK_NAME="pai-${ENVIRONMENT}"

echo "==================================="
echo "Deploying Lambda Functions"
echo "==================================="
echo "Environment: ${ENVIRONMENT}"
echo "Region: ${REGION}"
echo "==================================="

# Check if packages exist
if [ ! -d "dist/packages" ]; then
    echo "Error: Lambda packages not found. Run './scripts/package-functions.sh' first."
    exit 1
fi

# Function to update Lambda function code
update_function() {
    local FUNCTION_NAME=$1
    local ZIP_FILE=$2

    echo "Updating ${FUNCTION_NAME}..."

    aws lambda update-function-code \
        --function-name "pai-${FUNCTION_NAME}-${ENVIRONMENT}" \
        --zip-file "fileb://${ZIP_FILE}" \
        --region "${REGION}" \
        --no-cli-pager > /dev/null

    # Wait for update to complete
    aws lambda wait function-updated \
        --function-name "pai-${FUNCTION_NAME}-${ENVIRONMENT}" \
        --region "${REGION}"

    echo "✓ ${FUNCTION_NAME} updated successfully"
}

# Update each Lambda function
update_function "chat" "dist/packages/chat.zip"
update_function "memory" "dist/packages/memory.zip"
update_function "vector-search" "dist/packages/vector-search.zip"

echo "==================================="
echo "Lambda deployment complete!"
echo "==================================="

# Display function info
echo ""
echo "Function Status:"
aws lambda list-functions \
    --query "Functions[?starts_with(FunctionName, 'pai-') && contains(FunctionName, '${ENVIRONMENT}')].{Name:FunctionName,Runtime:Runtime,Size:CodeSize,Updated:LastModified}" \
    --region "${REGION}" \
    --output table
