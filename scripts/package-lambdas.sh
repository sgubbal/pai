#!/bin/bash
set -e

# Package Lambda Functions Script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ENVIRONMENT=${1:-dev}
STACK_NAME="pai-agent-${ENVIRONMENT}"
REGION=${AWS_REGION:-us-east-1}

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}PAI Lambda Function Packaging${NC}"
echo -e "${GREEN}========================================${NC}"

# Create build directory
BUILD_DIR="build/lambda-packages"
rm -rf $BUILD_DIR
mkdir -p $BUILD_DIR

echo -e "${YELLOW}Step 1: Installing dependencies...${NC}"

# Install dependencies in a temporary directory
pip install -r requirements.txt -t $BUILD_DIR/dependencies --platform manylinux2014_aarch64 --only-binary=:all: --python-version 3.11

echo -e "${GREEN}✓ Dependencies installed${NC}"

echo ""
echo -e "${YELLOW}Step 2: Packaging Lambda functions...${NC}"

# Function to package a Lambda
package_lambda() {
    local FUNCTION_NAME=$1
    local HANDLER_PATH=$2

    echo "Packaging $FUNCTION_NAME..."

    # Create function directory
    FUNCTION_DIR="$BUILD_DIR/$FUNCTION_NAME"
    mkdir -p $FUNCTION_DIR

    # Copy dependencies
    cp -r $BUILD_DIR/dependencies/* $FUNCTION_DIR/

    # Copy source code
    cp -r src/ $FUNCTION_DIR/

    # Copy handler
    cp $HANDLER_PATH $FUNCTION_DIR/handler.py

    # Create ZIP
    cd $FUNCTION_DIR
    zip -r -q ../${FUNCTION_NAME}.zip .
    cd - > /dev/null

    echo -e "${GREEN}✓ $FUNCTION_NAME packaged${NC}"
}

# Package each Lambda function
package_lambda "agent" "src/lambdas/agent/handler.py"
package_lambda "memory" "src/lambdas/memory/handler.py"
package_lambda "search" "src/lambdas/search/handler.py"

echo ""
echo -e "${YELLOW}Step 3: Uploading to Lambda functions...${NC}"

# Get function names from CloudFormation
AGENT_FUNCTION=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`AgentFunctionName`].OutputValue' \
    --output text)

# Update Lambda functions
update_lambda() {
    local FUNCTION_NAME=$1
    local ZIP_FILE=$2

    echo "Updating $FUNCTION_NAME..."

    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://$ZIP_FILE \
        --region $REGION > /dev/null

    echo -e "${GREEN}✓ $FUNCTION_NAME updated${NC}"
}

# Update each function
update_lambda "pai-agent-${ENVIRONMENT}" "$BUILD_DIR/agent.zip"
update_lambda "pai-memory-${ENVIRONMENT}" "$BUILD_DIR/memory.zip"
update_lambda "pai-search-${ENVIRONMENT}" "$BUILD_DIR/search.zip"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Lambda Functions Deployed!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Package sizes:"
ls -lh $BUILD_DIR/*.zip | awk '{print $9, $5}'
echo ""
